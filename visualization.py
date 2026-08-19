import cv2
import numpy as np

from config import landmark_indices as landmark
from core.face_features import fit_line_to_points, get_pixel_point
from core.schemas import FaceMeasurements, HairlineResult, RawFace


def _get_pixel_position(
    raw_face: RawFace,
    landmark_index: int,
) -> tuple[int, int]:
    point = get_pixel_point(raw_face, landmark_index)

    return (
        int(point.x),
        int(point.y),
    )


def _draw_horizontal_line(
    image: np.ndarray,
    y: float | None,
    color: tuple[int, int, int],
    thickness: int,
) -> None:
    if y is None:
        return

    y_position = int(y)
    cv2.line(
        image,
        (0, y_position),
        (image.shape[1] - 1, y_position),
        color,
        thickness,
    )


def _draw_landmark_points(
    image: np.ndarray,
    raw_face: RawFace,
    landmark_indices: tuple[int, ...],
    color: tuple[int, int, int],
) -> None:
    for index in landmark_indices:
        position = _get_pixel_position(raw_face, index)
        cv2.circle(image, position, 4, color, -1)
        cv2.putText(
            image,
            str(index),
            (position[0] + 4, position[1] - 4),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.35,
            color,
            1,
            cv2.LINE_AA,
        )


def _draw_fitted_line(
    image: np.ndarray,
    raw_face: RawFace,
    landmark_indices: tuple[int, ...],
    color: tuple[int, int, int],
) -> None:
    slope, intercept = fit_line_to_points(
        landmarks_number=landmark_indices,
        raw_face=raw_face,
    )

    x_values = []
    for index in landmark_indices:
        x, _ = _get_pixel_position(raw_face, index)
        x_values.append(x)

    x_start = max(0, min(x_values) - 10)
    x_end = min(image.shape[1] - 1, max(x_values) + 10)

    y_start = int(slope * x_start + intercept)
    y_end = int(slope * x_end + intercept)

    cv2.line(
        image,
        (x_start, y_start),
        (x_end, y_end),
        color,
        2,
        cv2.LINE_AA,
    )
    _draw_landmark_points(image, raw_face, landmark_indices, color)


def _draw_angle_label(
    image: np.ndarray,
    raw_face: RawFace,
    anchor_index: int,
    label: str,
    angle_deg: float,
    color: tuple[int, int, int],
) -> None:
    x, y = _get_pixel_position(raw_face, anchor_index)
    text = f"{label}: {angle_deg:.2f} deg"

    text_width, text_height = cv2.getTextSize(
        text,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        1,
    )[0]

    text_x = max(5, min(x - text_width // 2, image.shape[1] - text_width - 5))
    text_y = max(text_height + 5, min(y + 25, image.shape[0] - 5))

    cv2.putText(
        image,
        text,
        (text_x, text_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        color,
        1,
        cv2.LINE_AA,
    )


def _draw_original_guides(
    image: np.ndarray,
    raw_face: RawFace,
    hairline_result: HairlineResult,
) -> None:
    _draw_horizontal_line(image, hairline_result.final_y, (0, 0, 255), 3)
    _draw_horizontal_line(image, hairline_result.detected_y, (0, 255, 0), 2)
    _draw_horizontal_line(image, hairline_result.estimated_y, (255, 0, 0), 2)

    glabella_y = int(
        ((raw_face.points[8].y + raw_face.points[9].y) / 2)
        * raw_face.image_height
    )
    subnose_y = int(raw_face.points[94].y * raw_face.image_height)
    chin_y = int(raw_face.points[152].y * raw_face.image_height)

    _draw_horizontal_line(image, glabella_y, (0, 0, 255), 2)
    _draw_horizontal_line(image, subnose_y, (0, 0, 255), 2)
    _draw_horizontal_line(image, chin_y, (0, 0, 255), 2)

    cv2.line(
        image,
        _get_pixel_position(raw_face, 234),
        _get_pixel_position(raw_face, 454),
        (0, 255, 255),
        2,
    )


def _draw_jaw_angles(
    image: np.ndarray,
    raw_face: RawFace,
    face_measurements: FaceMeasurements,
) -> None:
    chin_color = (255, 0, 255)
    left_jaw_color = (0, 165, 255)
    right_jaw_color = (255, 255, 0)

    line_groups = (
        (landmark.CHIN_LEFT_LINE_INDICES, chin_color),
        (landmark.CHIN_RIGHT_LINE_INDICES, chin_color),
        (landmark.LEFT_JAW_UPPER_LINE_INDICES, left_jaw_color),
        (landmark.LEFT_JAW_LOWER_LINE_INDICES, left_jaw_color),
        (landmark.RIGHT_JAW_UPPER_LINE_INDICES, right_jaw_color),
        (landmark.RIGHT_JAW_LOWER_LINE_INDICES, right_jaw_color),
    )

    for indices, color in line_groups:
        _draw_fitted_line(image, raw_face, indices, color)

    _draw_angle_label(
        image,
        raw_face,
        152,
        "Chin",
        face_measurements.jaw.chin_angle_deg,
        chin_color,
    )
    _draw_angle_label(
        image,
        raw_face,
        172,
        "Left jaw",
        face_measurements.jaw.left_jaw_angle_deg,
        left_jaw_color,
    )
    _draw_angle_label(
        image,
        raw_face,
        397,
        "Right jaw",
        face_measurements.jaw.right_jaw_angle_deg,
        right_jaw_color,
    )


def show_face_analysis(
    image: np.ndarray,
    raw_face: RawFace,
    hairline_result: HairlineResult,
    face_measurements: FaceMeasurements,
) -> None:
    result_image = image.copy()

    _draw_original_guides(result_image, raw_face, hairline_result)
    _draw_jaw_angles(result_image, raw_face, face_measurements)

    cv2.imshow("Face analysis", result_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def draw_face_landmarks(
    image,
    raw_face,
):
    output = image.copy()

    for point in raw_face.points:
        x = int(point.x * raw_face.image_width)
        y = int(point.y * raw_face.image_height)

        cv2.circle(output, (x, y), 1, (0, 255, 0), -1)

    return output