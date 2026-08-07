from core.schemas import RawFace,VerticalFacePoints,VerticalFaceRatios

def ratio_calculate(
    hairline_y : float,
    vertical_facepoints : VerticalFacePoints,
    
):
    face_vertical_length = vertical_facepoints.chin_y - hairline_y

    upper_floor_ratio = (vertical_facepoints.glabella_y - hairline_y) / face_vertical_length
    middle_floor_ratio = (vertical_facepoints.subnasale_y - vertical_facepoints.glabella_y) / face_vertical_length
    lower_floor_ratio = (vertical_facepoints.chin_y - vertical_facepoints.subnasale_y) / face_vertical_length

    return VerticalFaceRatios(
        upper=upper_floor_ratio,
        middle=middle_floor_ratio,
        lower=lower_floor_ratio
    ) # 나중에 class 로 만들어 저장하기 
    