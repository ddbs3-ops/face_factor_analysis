import numpy as np  # 마스크 배열에서 중앙값을 계산하기 위해 numpy를 가져옵니다.

from core.schemas import RawFace,VerticalFacePoints,HairlineROI  # 얼굴 랜드마크와 이미지 크기를 담은 RawFace 타입을 가져옵니다.
from core.face_features import get_pixel_point

def detect_hairline_y(
    raw_face: RawFace,
    category_mask_2d: np.ndarray,
    hair_class_id: int = 1,
    skin_class_id: int = 3,
    top_ratio: float = 0.15,
) -> float | None:

    if not 0 < top_ratio <= 1:
        raise ValueError("top_ratio는 0보다 크고 1 이하여야 합니다.")

    mask_height, mask_width = category_mask_2d.shape

    if (
        mask_width != raw_face.image_width
        or mask_height != raw_face.image_height
    ):
        raise ValueError("원본 이미지와 마스크 크기가 다릅니다.")

    vertical_facepoints = get_vertical_landmark_y(raw_face)

    roi_info = get_forehead_roi(
        raw_face,
        vertical_facepoints
    )

    boundary_points = get_skin_hair_boundary_points(
        category_mask_2d,
        roi_info,
        skin_class_id=skin_class_id,
        hair_class_id=hair_class_id,
    )

    if not boundary_points:
        return None

    boundary_y_values = sorted(
        y for _, y in boundary_points
    )

    top_count = max(
        1,
        int(len(boundary_y_values) * top_ratio)
    )

    top_y_values = boundary_y_values[:top_count]

    return int(np.median(top_y_values))

def estimate_hairline_y(
    vertical_facepoints : VerticalFacePoints
):
    middle_face_length = (
        vertical_facepoints.subnasale_y
        - vertical_facepoints.glabella_y
    )

    lower_face_length = (
        vertical_facepoints.chin_y
        - vertical_facepoints.subnasale_y
    )

    estimated_upper_face_length = ((middle_face_length + lower_face_length) / 2) * 0.9

    hairline_y = (
        vertical_facepoints.glabella_y
        - estimated_upper_face_length
    )

    return max(0, hairline_y)

    

def get_vertical_landmark_y(
    raw_face: RawFace,
)-> VerticalFacePoints:

    glabella_y = (
        raw_face.points[8].y
        + raw_face.points[9].y
    ) / 2 * raw_face.image_height

    subnasale_y = (
        raw_face.points[94].y
        * raw_face.image_height
    )

    chin_y = (
        raw_face.points[152].y
        * raw_face.image_height
    )

    return VerticalFacePoints(
        glabella_y=glabella_y,
        subnasale_y=subnasale_y,
        chin_y=chin_y
    )

def get_forehead_roi(
    raw_face: RawFace,
    vertical_facepoints : VerticalFacePoints
):
    left_eye_outer = get_pixel_point(raw_face,226)
    right_eye_outer = get_pixel_point(raw_face,446)

    left_x = int(min(left_eye_outer.x, right_eye_outer.x))
    right_x = int(max(left_eye_outer.x, right_eye_outer.x))
    bottom_y = int(vertical_facepoints.glabella_y)

    middle_distance = abs(vertical_facepoints.subnasale_y - vertical_facepoints.glabella_y)
    lower_distance = abs(vertical_facepoints.chin_y - vertical_facepoints.subnasale_y)

    check_height_y = max(middle_distance, lower_distance) * 1.2

    top_y = max(0, int(vertical_facepoints.glabella_y - check_height_y))

    return HairlineROI(
        left_x=left_x,
        right_x=right_x,
        top_y=top_y,
        bottom_y=bottom_y
    )


def calculate_skin_ratio_profile(
    category_mask_2d: np.ndarray,
    roi_info: HairlineROI,
    skin_class_id: int = 3
):
    roi = category_mask_2d[
        roi_info.top_y:roi_info.bottom_y,
        roi_info.left_x:roi_info.right_x
    ]

    skin_ratios = []
    roi_width = roi.shape[1]

    for y in range(roi.shape[0]):
        row = roi[y]

        skin_count = np.sum(row == skin_class_id)
        skin_ratio = skin_count / roi_width

        skin_ratios.append(skin_ratio)

    return skin_ratios

def get_skin_hair_boundary_points(
    category_mask_2d: np.ndarray,
    roi_info: HairlineROI,
    skin_class_id: int = 3,
    hair_class_id: int = 1,
):
    boundary_points = []

    for x in range(roi_info.left_x, roi_info.right_x):
        found_skin = False

        for y in range(
            roi_info.bottom_y - 1,
            roi_info.top_y - 1,
            -1
        ):
            current_class = category_mask_2d[y, x]

            # 먼저 피부 영역을 확인
            if current_class == skin_class_id:
                found_skin = True
                continue

            # 피부를 지난 뒤 처음 만나는 머리카락을 경계로 사용
            if found_skin and current_class == hair_class_id:
                boundary_points.append((x, y))
                break

    return boundary_points

def calculate_boundary_difference_ratios(
    boundary_points,
    estimated_hairline_y,
    vertical_facepoints,
):
    middle_face_length = (
        vertical_facepoints.subnasale_y
        - vertical_facepoints.glabella_y
    )

    difference_ratios = []

    for _, boundary_y in boundary_points:
        difference_ratio = (
            boundary_y - estimated_hairline_y
        ) / middle_face_length

        difference_ratios.append(difference_ratio)

    return difference_ratios


