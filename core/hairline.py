import numpy as np  # 마스크 배열에서 중앙값을 계산하기 위해 numpy를 가져옵니다.

from core.schemas import RawFace,VerticalFacePoints,HairlineROI  # 얼굴 랜드마크와 이미지 크기를 담은 RawFace 타입을 가져옵니다.
from core.face_features import get_pixel_point

def detect_hairline_y(  
    raw_face: RawFace,  
    category_mask_2d: np.ndarray,  
    hair_class_id: int = 1,  
) -> float | None:  
    left_cheek = raw_face.points[234]  
    right_cheek = raw_face.points[454]  
    forehead_top = raw_face.points[10]  

    face_center_x_ratio = (left_cheek.x + right_cheek.x) / 2  # 양쪽 볼의 중간값으로 얼굴 중앙 x 비율을 구합니다.
    face_width_ratio = abs(right_cheek.x - left_cheek.x)  # 양쪽 볼 사이 거리로 얼굴 너비 비율을 구합니다.
    search_half_width_ratio = face_width_ratio * 0.12  # 얼굴 중앙 주변만 보도록 얼굴 너비의 12%를 반쪽 탐색 폭으로 정합니다.

    center_x = int(face_center_x_ratio * raw_face.image_width)  # 얼굴 중앙 x 비율을 실제 픽셀 x 좌표로 바꿉니다.
    start_y = int(forehead_top.y * raw_face.image_height)  # 탐색 시작 y 비율을 실제 픽셀 y 좌표로 바꿉니다.
    half_width = int(search_half_width_ratio * raw_face.image_width)  # 반쪽 탐색 폭 비율을 실제 픽셀 너비로 바꿉니다.

    mask_height, mask_width = category_mask_2d.shape  # 마스크의 높이와 너비를 가져옵니다.
    if mask_width != raw_face.image_width or mask_height != raw_face.image_height:
        raise ValueError("원본 이미지와 마스크 크기가 다릅니다.")
    
    center_x = max(0, min(center_x, mask_width - 1))  # 중앙 x가 마스크 범위를 벗어나지 않게 제한합니다.
    start_y = max(0, min(start_y, mask_height - 1))  # 시작 y가 마스크 범위를 벗어나지 않게 제한합니다.
    left_x = max(0, center_x - half_width)  # 검사할 가장 왼쪽 x 좌표를 정합니다.
    right_x = min(mask_width - 1, center_x + half_width)  # 검사할 가장 오른쪽 x 좌표를 정합니다.

    found_y_values = []  # 각 x 위치에서 처음 발견한 머리카락 y값을 모을 리스트를 만듭니다.

    for x in range(left_x, right_x + 1):  # 얼굴 중앙 기준의 좁은 x 범위를 왼쪽부터 오른쪽까지 검사합니다.
        for y in range(start_y, -1, -1):  # 시작 y에서 이미지 위쪽 방향으로 한 칸씩 올라갑니다.
            if category_mask_2d[y, x] == hair_class_id:  # 현재 위치가 머리카락 클래스인지 확인합니다.
                found_y_values.append(y)  # 머리카락을 처음 찾은 y 좌표를 저장합니다.
                break  # 이 x에서는 첫 머리카락을 찾았으므로 더 위로 올라가지 않습니다.

    if not found_y_values:  # 어떤 x에서도 머리카락을 찾지 못했는지 확인합니다.
        return None  # 검출에 실패했으므로 None을 반환합니다.

    hairline_y = int(np.median(found_y_values)) 

    

     # 찾은 y값들의 중앙값을 최종 헤어라인 y로 정합니다.
    return hairline_y  # 최종 헤어라인 y 픽셀 좌표를 반환합니다.

def estimate_hairline_y(
    raw_face: RawFace,
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

    estimated_upper_face_length = (
        middle_face_length + lower_face_length
    ) / 2

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
    category_mask_2d : np.ndarray,
    vertical_facepoints : VerticalFacePoints
):
    left_eye_outer = get_pixel_point(raw_face,226)
    right_eye_outer = get_pixel_point(raw_face,446)

    left_x = int(left_eye_outer.x)
    right_x = int(right_eye_outer.x)
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
        boundary_y = None

        for y in range(roi_info.bottom_y - 1, roi_info.top_y - 1, -1):
            current_class = category_mask_2d[y, x]

            if current_class == hair_class_id:
                boundary_y = y
                break

        if boundary_y is not None:
            boundary_points.append((x, boundary_y))

    return boundary_points