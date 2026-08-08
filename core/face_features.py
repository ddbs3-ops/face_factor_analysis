from core.schemas import *
from core.geometric import *    
import math
import numpy as np
def calculate_vertical_face_ratios(
    hairline_y : float,
    vertical_facepoints : VerticalFacePoints,
    
):
    face_vertical_length = vertical_facepoints.chin_y - hairline_y

    upper_floor_ratio = (vertical_facepoints.glabella_y - hairline_y) / face_vertical_length
    middle_floor_ratio = (vertical_facepoints.subnasale_y - vertical_facepoints.glabella_y) / face_vertical_length
    lower_floor_ratio = (vertical_facepoints.chin_y - vertical_facepoints.subnasale_y) / face_vertical_length

    return VerticalFaceRatios(
        upper=round(upper_floor_ratio,4),
        middle=round(middle_floor_ratio,4),
        lower=round(lower_floor_ratio,4)
    ) 

def calculate_face_width_height_ratio(
    hairlne_y : float,
    raw_face : RawFace
):

    chin = get_pixel_point(raw_face, 152)
    left_cheekbone = get_pixel_point(raw_face, 234)
    right_cheekbone = get_pixel_point(raw_face, 454)
    
    face_height = abs(hairlne_y - chin.y)
    face_width = abs(right_cheekbone.x - left_cheekbone.x)

    return round(face_width / face_height , 4)

def calculate_face_widths(
        raw_face : RawFace
):
    left_cheekbone = get_pixel_point(raw_face, 234)
    right_cheekbone = get_pixel_point(raw_face, 454)

    left_jaw = get_pixel_point(raw_face, 172)
    right_jaw = get_pixel_point(raw_face, 397)

    cheekbone_distance = calculate_distance(left_cheekbone, right_cheekbone)
    jaw_distance = calculate_distance(left_jaw, right_jaw)

    return round(jaw_distance / cheekbone_distance, 4)

def get_pixel_point(
    raw_face : RawFace,
    index : int,
):
    points=raw_face.points[index]

    return Point2D(
        x= points.x * raw_face.image_width,
        y= points.y * raw_face.image_height
    )

def calculate_local_angle(
    p_prev : Point2D,
    p_curr : Point2D,
    p_next : Point2D
):
    v1_x = p_prev.x - p_curr.x
    v1_y = p_prev.y - p_curr.y

    v2_x = p_next.x - p_curr.x
    v2_y = p_next.y - p_curr.y

    dot = v1_x * v2_x + v1_y * v2_y

    v1_norm = math.hypot(v1_x, v1_y)
    v2_norm = math.hypot(v2_x, v2_y)

    if v1_norm == 0 or v2_norm == 0 :
        raise ValueError("서로 다른 3점이 필요합니다.")
    
    cosine_theta = dot / (v1_norm * v2_norm)
    cosine_theta = max(-1.0, min(1.0, cosine_theta))
    
    theta = math.degrees(math.acos(cosine_theta))

    return round(theta,2)

def calculate_face_contour_local_angles(
    landmarks_number : tuple[int, ...],
    raw_face : RawFace
):

    angles =[]
    for i in range(len(landmarks_number)-2):
        points_prev = get_pixel_point(raw_face, landmarks_number[i])
        points_curr = get_pixel_point(raw_face, landmarks_number[i+1])
        points_next = get_pixel_point(raw_face, landmarks_number[i+2])

        angle = calculate_local_angle(points_prev, points_curr, points_next)

        angles += [angle]

    return tuple(angles)

def fit_line_to_points(
    raw_face : RawFace,
    landmarks_number : tuple[int, ...]
):
    
    points = []
    points = [
        get_pixel_point(raw_face, index)
        for index in landmarks_number
    ]

    x_values = []
    y_values = []

    for point in points:
        x_values.append(point.x)
        y_values.append(point.y)

    slope, intercept = np.polyfit(x_values, y_values, 1) #향후에 2차식으로 한다음에 턱선에서 접선기울기 구해서 해보기

    return slope, intercept

def slope_to_vector(
    slope: float
):
    return (1,slope)
    

def calculate_angle_between_vector(
    vector1 : tuple,
    vector2 : tuple
):
    dot = vector1[0] * vector2[0] + vector1[1] * vector2[1]

    vector1_norm = math.hypot(vector1[0],vector1[1])
    vector2_norm = math.hypot(vector2[0],vector2[1])

    if vector1_norm == 0 or vector2_norm == 0:
        raise ValueError("영벡터의 각도는 계산 할 수 없습니다.")

    cosine_theta = dot / (vector1_norm * vector2_norm)
    theta = math.acos(cosine_theta)

    return round(math.degrees(theta), 2)



    
