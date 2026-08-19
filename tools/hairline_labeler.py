import csv
import sqlite3
import sys
from pathlib import Path

import cv2
import numpy as np
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.hairline import (  # noqa: E402
    calculate_boundary_difference_ratios,
    calculate_skin_ratio_profile,
    detect_hairline_y,
    estimate_hairline_y,
    get_forehead_roi,
    get_skin_hair_boundary_points,
    get_vertical_landmark_y,
)
from core.mediapipe_tasks import create_face_landmarker, create_selfie_segmenter  # noqa: E402
from main import create_raw_face, detect_face, load_image  # noqa: E402


DEFAULT_DB_PATH = "data/face_analysis.db"
DEFAULT_CSV_PATH = "data/hairline_labels_v3.csv"
DEFAULT_SELFIE_MODEL_PATH = "models/selfie_multiclass_256x256.tflite"
DEFAULT_FACE_LANDMARKER_MODEL_PATH = "models/face_landmarker.task"

NEAR_BOUNDARY_DIFFERENCE_RATIO_THRESHOLD = 0.08
FINAL_SOURCE_DIFFERENCE_RATIO_THRESHOLD = 0.30

VISIBILITY_OPTIONS = ("visible", "partial", "covered")
TRUE_Y_MODES = (
    "detected hairline 사용",
    "manual y 직접 지정",
    "true hairline 알 수 없음",
)
CSV_COLUMNS = [
    "face_measurement_id",
    "person_id",
    "image_name",
    "image_path",
    "visibility_label",
    "true_hairline_y",
    "true_y_source",
    "estimated_hairline_y",
    "detected_hairline_y",
    "detected_estimated_difference_ratio",
    "mean_difference_ratio",
    "std_difference_ratio",
    "min_difference_ratio",
    "max_difference_ratio",
    "near_boundary_ratio",
    "mean_skin_ratio",
]


def load_existing_label_ids(csv_path: Path) -> set[int]:
    if not csv_path.exists():
        return set()

    with csv_path.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        existing_ids = set()
        for row in reader:
            value = row.get("face_measurement_id")
            if value:
                try:
                    existing_ids.add(int(value))
                except ValueError:
                    pass
        return existing_ids


def load_existing_label_rows(csv_path: Path) -> dict[int, dict]:
    if not csv_path.exists():
        return {}

    with csv_path.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        rows = {}
        for row in reader:
            value = row.get("face_measurement_id")
            if not value:
                continue
            try:
                rows[int(value)] = row
            except ValueError:
                pass
        return rows


@st.cache_data(show_spinner="DB에서 라벨링 대상 로딩 중...")
def load_face_measurement_targets(db_path_string: str) -> list[dict]:
    db_path = Path(db_path_string)
    if not db_path.exists():
        return []

    db_uri_path = db_path.resolve().as_posix()
    conn = sqlite3.connect(f"file:{db_uri_path}?mode=ro", uri=True)
    try:
        rows = conn.execute(
            """
            SELECT id, person_id, image_path
            FROM face_measurements
            ORDER BY id
            """
        ).fetchall()
    finally:
        conn.close()

    return [
        {
            "face_measurement_id": row[0],
            "person_id": row[1],
            "image_path": row[2],
        }
        for row in rows
    ]


def target_image_path(target: dict) -> Path:
    return Path(target["image_path"])


def target_session_key(target: dict) -> str:
    return str(target["face_measurement_id"])


def target_display_name(target: dict) -> str:
    return f'{target["face_measurement_id"]} | person {target["person_id"]} | {target["image_path"]}'


def find_target_by_id(targets: list[dict], face_measurement_id: int) -> dict | None:
    for target in targets:
        if target["face_measurement_id"] == face_measurement_id:
            return target
    return None


def parse_review_ids(review_ids_text: str) -> list[int]:
    normalized_text = review_ids_text.replace(",", " ").replace("\n", " ")
    review_ids = []
    for value in normalized_text.split():
        try:
            review_ids.append(int(value))
        except ValueError:
            pass
    return review_ids


def filter_targets_by_ids(targets: list[dict], review_ids: list[int]) -> list[dict]:
    if not review_ids:
        return []

    targets_by_id = {
        target["face_measurement_id"]: target
        for target in targets
    }
    return [
        targets_by_id[review_id]
        for review_id in review_ids
        if review_id in targets_by_id
    ]


def get_existing_label_progress(existing_ids: set[int], targets: list[dict]) -> int:
    target_ids = {
        target["face_measurement_id"]
        for target in targets
    }
    return len(existing_ids & target_ids)


@st.cache_resource(show_spinner="MediaPipe 모델 로딩 중...")
def load_models(face_model_path: str, selfie_model_path: str):
    return (
        create_face_landmarker(face_model_path),
        create_selfie_segmenter(selfie_model_path),
    )


def optional_float(value):
    if value is None:
        return None
    if isinstance(value, float) and np.isnan(value):
        return None
    return float(value)


def calculate_stats(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {
            "mean": None,
            "std": None,
            "min": None,
            "max": None,
        }

    values_array = np.asarray(values, dtype=float)
    return {
        "mean": float(np.mean(values_array)),
        "std": float(np.std(values_array)),
        "min": float(np.min(values_array)),
        "max": float(np.max(values_array)),
    }


def calculate_near_boundary_ratio(difference_ratios: list[float]) -> float | None:
    if not difference_ratios:
        return None

    near_count = sum(
        abs(difference_ratio) <= NEAR_BOUNDARY_DIFFERENCE_RATIO_THRESHOLD
        for difference_ratio in difference_ratios
    )
    return near_count / len(difference_ratios)


def calculate_detected_estimated_difference_ratio(
    detected_hairline_y: float | None,
    estimated_hairline_y: float,
    vertical_facepoints,
) -> float | None:
    if detected_hairline_y is None:
        return None

    middle_face_length = (
        vertical_facepoints.subnasale_y
        - vertical_facepoints.glabella_y
    )
    if middle_face_length == 0:
        return None

    return abs(detected_hairline_y - estimated_hairline_y) / middle_face_length


def calculate_analysis_final_hairline(
    detected_hairline_y: float | None,
    estimated_hairline_y: float,
    difference_ratio: float | None,
) -> tuple[str, float]:
    if detected_hairline_y is None:
        return "estimated", estimated_hairline_y

    if (
        difference_ratio is not None
        and difference_ratio > FINAL_SOURCE_DIFFERENCE_RATIO_THRESHOLD
    ):
        return "estimated", estimated_hairline_y

    return "detected", detected_hairline_y


@st.cache_data(show_spinner="이미지 분석 중...")
def calculate_hairline_features(
    image_path_string: str,
    image_mtime: float,
    _face_landmarker,
    _selfie_segmenter,
):
    del image_mtime

    image_path = Path(image_path_string)
    image, mp_image, image_height, image_width = load_image(str(image_path))
    detection_result = detect_face(mp_image, _face_landmarker, _selfie_segmenter)
    if detection_result is None:
        return None

    face_landmarker_result, segmented_masks_result = detection_result
    raw_face = create_raw_face(face_landmarker_result, image_width, image_height)
    vertical_facepoints = get_vertical_landmark_y(raw_face)

    category_mask = segmented_masks_result.category_mask.numpy_view()
    category_mask_2d = np.squeeze(category_mask)

    estimated_hairline_y = estimate_hairline_y(vertical_facepoints)
    detected_hairline_y = detect_hairline_y(raw_face, category_mask_2d)
    roi_info = get_forehead_roi(raw_face, vertical_facepoints)
    boundary_points = get_skin_hair_boundary_points(category_mask_2d, roi_info)
    difference_ratios = calculate_boundary_difference_ratios(
        boundary_points,
        estimated_hairline_y,
        vertical_facepoints,
    )
    skin_ratios = calculate_skin_ratio_profile(category_mask_2d, roi_info)

    difference_stats = calculate_stats(difference_ratios)
    skin_stats = calculate_stats(skin_ratios)
    detected_estimated_difference_ratio = calculate_detected_estimated_difference_ratio(
        detected_hairline_y,
        estimated_hairline_y,
        vertical_facepoints,
    )
    analysis_final_source, analysis_final_hairline_y = calculate_analysis_final_hairline(
        detected_hairline_y,
        estimated_hairline_y,
        detected_estimated_difference_ratio,
    )

    return {
        "image": image,
        "image_height": image_height,
        "estimated_hairline_y": optional_float(estimated_hairline_y),
        "detected_hairline_y": optional_float(detected_hairline_y),
        "detected_estimated_difference_ratio": optional_float(
            detected_estimated_difference_ratio
        ),
        "analysis_final_source": analysis_final_source,
        "analysis_final_hairline_y": optional_float(analysis_final_hairline_y),
        "roi_info": roi_info,
        "boundary_points": boundary_points,
        "mean_difference_ratio": difference_stats["mean"],
        "std_difference_ratio": difference_stats["std"],
        "min_difference_ratio": difference_stats["min"],
        "max_difference_ratio": difference_stats["max"],
        "near_boundary_ratio": calculate_near_boundary_ratio(difference_ratios),
        "mean_skin_ratio": skin_stats["mean"],
    }


def draw_dashed_horizontal_line(image, y: int, color, thickness: int = 2, dash_length: int = 14):
    height, width = image.shape[:2]
    if y < 0 or y >= height:
        return

    for start_x in range(0, width, dash_length * 2):
        end_x = min(start_x + dash_length, width - 1)
        cv2.line(image, (start_x, y), (end_x, y), color, thickness)


def draw_labeling_view(features: dict, true_hairline_y: float | None):
    view = features["image"].copy()
    height, width = view.shape[:2]

    estimated_y = features["estimated_hairline_y"]
    detected_y = features["detected_hairline_y"]

    if estimated_y is not None:
        y = int(round(estimated_y))
        cv2.line(view, (0, y), (width - 1, y), (0, 255, 0), 2)

    if detected_y is not None:
        draw_dashed_horizontal_line(view, int(round(detected_y)), (255, 255, 0), 2)

    for x, y in features["boundary_points"]:
        cv2.circle(view, (int(x), int(y)), 1, (255, 0, 255), -1)

    if true_hairline_y is not None:
        y = int(round(true_hairline_y))
        cv2.line(view, (0, y), (width - 1, y), (0, 0, 255), 2)

    roi = features["roi_info"]
    cv2.rectangle(
        view,
        (roi.left_x, roi.top_y),
        (roi.right_x, roi.bottom_y),
        (180, 180, 180),
        1,
    )

    return cv2.cvtColor(view, cv2.COLOR_BGR2RGB)


def format_csv_value(value):
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6f}"
    return value


def build_label_row(
    target: dict,
    features: dict,
    visibility_label: str,
    true_hairline_y: float | None,
    true_y_source: str,
) -> dict:
    if true_hairline_y is None:
        true_y_source = "unknown"

    return {
        "face_measurement_id": target["face_measurement_id"],
        "person_id": target["person_id"],
        "image_name": target["image_path"],
        "image_path": target["image_path"],
        "visibility_label": visibility_label,
        "true_hairline_y": format_csv_value(true_hairline_y),
        "true_y_source": true_y_source,
        "estimated_hairline_y": format_csv_value(features["estimated_hairline_y"]),
        "detected_hairline_y": format_csv_value(features["detected_hairline_y"]),
        "detected_estimated_difference_ratio": format_csv_value(
            features["detected_estimated_difference_ratio"]
        ),
        "mean_difference_ratio": format_csv_value(features["mean_difference_ratio"]),
        "std_difference_ratio": format_csv_value(features["std_difference_ratio"]),
        "min_difference_ratio": format_csv_value(features["min_difference_ratio"]),
        "max_difference_ratio": format_csv_value(features["max_difference_ratio"]),
        "near_boundary_ratio": format_csv_value(features["near_boundary_ratio"]),
        "mean_skin_ratio": format_csv_value(features["mean_skin_ratio"]),
    }


def ensure_csv_schema(csv_path: Path):
    if not csv_path.exists() or csv_path.stat().st_size == 0:
        return

    with csv_path.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames == CSV_COLUMNS:
            return
        rows = list(reader)

    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                column: row.get(column, "")
                for column in CSV_COLUMNS
            })


def save_label(
    csv_path: Path,
    target: dict,
    features: dict,
    visibility_label: str,
    true_hairline_y: float | None,
    true_y_source: str,
):
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    ensure_csv_schema(csv_path)
    should_write_header = not csv_path.exists() or csv_path.stat().st_size == 0
    row = build_label_row(
        target,
        features,
        visibility_label,
        true_hairline_y,
        true_y_source,
    )

    if csv_path.exists() and csv_path.stat().st_size > 0:
        with csv_path.open("r", newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            rows = [
                existing_row
                for existing_row in reader
                if existing_row.get("face_measurement_id") != str(target["face_measurement_id"])
            ]

        with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            writer.writerows(rows)
            writer.writerow(row)
            csv_file.flush()
        return

    with csv_path.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_COLUMNS)
        if should_write_header:
            writer.writeheader()
        writer.writerow(row)
        csv_file.flush()


def initialize_session_state():
    defaults = {
        "current_index": 0,
        "current_image_name": None,
        "visibility_label": None,
        "true_y_mode": TRUE_Y_MODES[2],
        "manual_y": None,
        "skipped_face_measurement_ids": set(),
        "visited_target_ids": [],
        "review_target_id": None,
        "review_ids_text": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_selection_for_target(target: dict, features: dict, existing_label_row: dict | None):
    session_key = target_session_key(target)
    if st.session_state.current_image_name == session_key:
        return

    roi = features["roi_info"]
    detected_y = features["detected_hairline_y"]
    default_manual_y = detected_y if detected_y is not None else (roi.top_y + roi.bottom_y) / 2
    default_manual_y = max(roi.top_y, min(default_manual_y, roi.bottom_y))

    st.session_state.current_image_name = session_key
    st.session_state.manual_y = int(round(default_manual_y))
    st.session_state.visibility_label = None
    st.session_state.true_y_mode = TRUE_Y_MODES[2]

    if existing_label_row is None:
        return

    visibility_label = existing_label_row.get("visibility_label")
    true_y_source = existing_label_row.get("true_y_source")
    true_hairline_y = existing_label_row.get("true_hairline_y")

    if visibility_label in VISIBILITY_OPTIONS:
        st.session_state.visibility_label = visibility_label
    if true_y_source == "detected":
        st.session_state.true_y_mode = TRUE_Y_MODES[0]
    elif true_y_source == "manual":
        st.session_state.true_y_mode = TRUE_Y_MODES[1]
        if true_hairline_y:
            st.session_state.manual_y = int(round(float(true_hairline_y)))
    else:
        st.session_state.true_y_mode = TRUE_Y_MODES[2]

    st.session_state.manual_y = int(
        max(roi.top_y, min(st.session_state.manual_y, roi.bottom_y))
    )


def get_current_true_y(features: dict) -> tuple[float | None, str]:
    mode = st.session_state.true_y_mode

    if mode == TRUE_Y_MODES[0]:
        return features["detected_hairline_y"], "detected"
    if mode == TRUE_Y_MODES[1]:
        return float(st.session_state.manual_y), "manual"
    return None, "unknown"


def clamp_current_index(pending_count: int, allow_end: bool = False):
    if pending_count <= 0:
        st.session_state.current_index = 0
        return
    if allow_end and st.session_state.current_index >= pending_count:
        st.session_state.current_index = pending_count
        return
    st.session_state.current_index = max(
        0,
        min(st.session_state.current_index, pending_count - 1),
    )


def remember_visited_target(target: dict):
    face_measurement_id = target["face_measurement_id"]
    if (
        st.session_state.visited_target_ids
        and st.session_state.visited_target_ids[-1] == face_measurement_id
    ):
        return

    st.session_state.visited_target_ids.append(face_measurement_id)


def render_sidebar():
    st.sidebar.header("설정")
    db_path_string = st.sidebar.text_input("SQLite DB 경로", DEFAULT_DB_PATH)
    csv_path_string = st.sidebar.text_input("CSV 경로", DEFAULT_CSV_PATH)
    face_model_path_string = st.sidebar.text_input(
        "Face landmarker 모델",
        DEFAULT_FACE_LANDMARKER_MODEL_PATH,
    )
    selfie_model_path_string = st.sidebar.text_input(
        "Selfie segmenter 모델",
        DEFAULT_SELFIE_MODEL_PATH,
    )
    review_ids_text = st.sidebar.text_area(
        "검토할 face_measurement_id 목록",
        help="비워두면 일반 라벨링 모드입니다. 예: 32, 31, 42",
    )

    return (
        Path(db_path_string),
        Path(csv_path_string),
        Path(face_model_path_string),
        Path(selfie_model_path_string),
        review_ids_text,
    )


def render_navigation(
    current_target: dict,
    pending_count: int,
    is_review_mode: bool,
    is_id_review_mode: bool,
):
    previous_col, skip_col = st.columns(2)

    with previous_col:
        if st.button("이전 이미지", disabled=not st.session_state.visited_target_ids):
            st.session_state.review_target_id = st.session_state.visited_target_ids.pop()
            st.session_state.current_image_name = None
            st.rerun()

    with skip_col:
        if st.button("현재 이미지 건너뛰기", disabled=(pending_count == 0 and not is_review_mode)):
            if is_review_mode:
                st.session_state.review_target_id = None
            elif is_id_review_mode:
                st.session_state.current_index += 1
                clamp_current_index(pending_count, allow_end=True)
            else:
                remember_visited_target(current_target)
                st.session_state.skipped_face_measurement_ids.add(
                    current_target["face_measurement_id"]
                )
                clamp_current_index(pending_count)
            st.session_state.current_image_name = None
            st.rerun()


def render_label_controls(features: dict):
    visibility_label = st.radio(
        "visibility label",
        VISIBILITY_OPTIONS,
        index=(
            VISIBILITY_OPTIONS.index(st.session_state.visibility_label)
            if st.session_state.visibility_label in VISIBILITY_OPTIONS
            else None
        ),
        horizontal=True,
        key="visibility_label",
    )

    st.radio(
        "true hairline_y 선택",
        TRUE_Y_MODES,
        horizontal=True,
        key="true_y_mode",
    )

    roi = features["roi_info"]
    slider_min = max(0, int(roi.top_y))
    slider_max = min(features["image_height"] - 1, int(roi.bottom_y))
    if slider_min >= slider_max:
        slider_min = 0
        slider_max = features["image_height"] - 1

    if st.session_state.true_y_mode == TRUE_Y_MODES[0]:
        if features["detected_hairline_y"] is None:
            st.warning("이 이미지에서는 detected_hairline_y가 없습니다. unknown을 선택하거나 manual y를 지정하세요.")
    elif st.session_state.true_y_mode == TRUE_Y_MODES[1]:
        st.slider(
            "manual true_hairline_y",
            min_value=slider_min,
            max_value=slider_max,
            key="manual_y",
        )

    return visibility_label


def render_feature_summary(features: dict):
    st.caption(
        "green: estimated_hairline_y / cyan dashed: detected_hairline_y / "
        "magenta: boundary_points / red: true_hairline_y"
    )
    final_source = features["analysis_final_source"].upper()
    final_y = int(round(features["analysis_final_hairline_y"]))
    st.write(f"실제 분석 로직: {final_source} 사용 (y={final_y})")
    cols = st.columns(4)
    cols[0].metric("estimated_y", format_csv_value(features["estimated_hairline_y"]) or "-")
    cols[1].metric("detected_y", format_csv_value(features["detected_hairline_y"]) or "-")
    cols[2].metric("near_boundary", format_csv_value(features["near_boundary_ratio"]) or "-")
    cols[3].metric("mean_skin", format_csv_value(features["mean_skin_ratio"]) or "-")


def run_labeler():
    st.set_page_config(page_title="Hairline Labeler", layout="wide")
    st.title("Hairline Labeler")

    initialize_session_state()
    db_path, csv_path, face_model_path, selfie_model_path, review_ids_text = render_sidebar()
    if st.session_state.review_ids_text != review_ids_text:
        st.session_state.review_ids_text = review_ids_text
        st.session_state.current_index = 0
        st.session_state.current_image_name = None
        st.session_state.review_target_id = None

    targets = load_face_measurement_targets(str(db_path))
    review_ids = parse_review_ids(review_ids_text)
    review_targets = filter_targets_by_ids(targets, review_ids)
    is_id_review_mode = bool(review_ids)
    existing_label_ids = load_existing_label_ids(csv_path)
    existing_label_rows = load_existing_label_rows(csv_path)
    labeled_count = get_existing_label_progress(existing_label_ids, targets)
    if is_id_review_mode:
        pending_targets = review_targets
    else:
        pending_targets = [
            target
            for target in targets
            if (
                target["face_measurement_id"] not in existing_label_ids
                and target["face_measurement_id"]
                not in st.session_state.skipped_face_measurement_ids
            )
        ]
    clamp_current_index(len(pending_targets), allow_end=is_id_review_mode)
    review_target = (
        find_target_by_id(targets, st.session_state.review_target_id)
        if st.session_state.review_target_id is not None
        else None
    )
    if st.session_state.review_target_id is not None and review_target is None:
        st.session_state.review_target_id = None

    st.progress(
        0 if not targets else min(labeled_count / len(targets), 1.0),
        text=f"{labeled_count} / {len(targets)}",
    )

    if not targets:
        st.info("DB의 face_measurements 테이블에 라벨링할 대상이 없습니다.")
        return

    if is_id_review_mode and not pending_targets:
        st.warning("입력한 face_measurement_id에 해당하는 DB 대상이 없습니다.")
        return

    if is_id_review_mode and st.session_state.current_index >= len(pending_targets):
        st.success("검토 목록을 모두 확인했습니다.")
        if st.button("검토 목록 처음으로"):
            st.session_state.current_index = 0
            st.session_state.current_image_name = None
            st.rerun()
        return

    if not pending_targets and review_target is None:
        st.success("모든 이미지 라벨링이 완료되었습니다.")
        return

    face_landmarker, selfie_segmenter = load_models(
        str(face_model_path),
        str(selfie_model_path),
    )

    is_review_mode = review_target is not None
    current_target = (
        review_target
        if is_review_mode
        else pending_targets[st.session_state.current_index]
    )
    current_image_path = target_image_path(current_target)
    if is_review_mode:
        st.subheader("이전 이미지")
    elif is_id_review_mode:
        st.subheader(f"{st.session_state.current_index + 1} / {len(pending_targets)} review")
    else:
        st.subheader(f"{st.session_state.current_index + 1} / {len(pending_targets)} pending")
    st.write(target_display_name(current_target))

    if not current_image_path.exists():
        st.warning(f"이미지 파일을 찾을 수 없습니다: {current_target['image_path']}")
        render_navigation(current_target, len(pending_targets), is_review_mode, is_id_review_mode)
        return

    features = calculate_hairline_features(
        str(current_image_path),
        current_image_path.stat().st_mtime,
        face_landmarker,
        selfie_segmenter,
    )

    if features is None:
        st.warning("얼굴 또는 segmentation 결과를 만들 수 없어 이 이미지를 라벨링할 수 없습니다.")
        render_navigation(current_target, len(pending_targets), is_review_mode, is_id_review_mode)
        return

    existing_label_row = existing_label_rows.get(current_target["face_measurement_id"])
    reset_selection_for_target(current_target, features, existing_label_row)
    visibility_label = render_label_controls(features)
    true_hairline_y, true_y_source = get_current_true_y(features)

    overlay_image = draw_labeling_view(features, true_hairline_y)
    st.image(overlay_image, use_container_width=True)
    render_feature_summary(features)

    save_col, nav_col = st.columns([1, 2])
    with save_col:
        if st.button("저장하고 다음", type="primary"):
            if visibility_label not in VISIBILITY_OPTIONS:
                st.error("visibility label을 먼저 선택해야 저장할 수 있습니다.")
            elif st.session_state.true_y_mode == TRUE_Y_MODES[0] and true_hairline_y is None:
                st.error("detected_hairline_y가 없어 detected 값을 저장할 수 없습니다.")
            else:
                save_label(
                    csv_path,
                    current_target,
                    features,
                    visibility_label,
                    true_hairline_y,
                    true_y_source,
                )
                if is_review_mode:
                    st.session_state.review_target_id = None
                elif is_id_review_mode:
                    st.session_state.current_index += 1
                    clamp_current_index(len(pending_targets), allow_end=True)
                else:
                    remember_visited_target(current_target)
                st.session_state.current_image_name = None
                st.success(f"저장됨: {target_display_name(current_target)}")
                st.rerun()

    with nav_col:
        render_navigation(current_target, len(pending_targets), is_review_mode, is_id_review_mode)


if __name__ == "__main__":
    run_labeler()
