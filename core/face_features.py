from core.schemas import *
from core.geometric import *

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

    return round(face_height / face_width, 4)

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

