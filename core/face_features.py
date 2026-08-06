from core.schemas import RawFace

def ratio_calculate(
    raw_face : RawFace,
    hairline_y : float
):
    glabella = 8
    subnose = 94
    chin = 152

    glabella_img_y = raw_face.points[glabella].y * raw_face.image_height
    subnose_img_y = raw_face.points[subnose].y * raw_face.image_height
    chin_img_y = raw_face.points[chin].y * raw_face.image_height

    face_horizontal = abs(raw_face.points[chin].y * raw_face.image_height - hairline_y)

    Upper_floor_ratio = (glabella_img_y - hairline_y) / face_horizontal
    middle_floor_ratio = (subnose_img_y - glabella_img_y) / face_horizontal
    lower_floor_ratio = (chin_img_y - subnose_img_y) / face_horizontal

    return Upper_floor_ratio, middle_floor_ratio, lower_floor_ratio # 나중에 class 로 만들어 저장하기 
    