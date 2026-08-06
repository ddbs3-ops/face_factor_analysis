from core.schemas import RawFace

def calculate_distance(
        raw_face : RawFace,
        index1 : int,
        index2 : int,
):
    x_distance = abs(raw_face.points[index1].x - raw_face.points[index2].x)
    y_distance = abs(raw_face.points[index1].y - raw_face.points[index2].y)

    distance = ((x_distance * raw_face.image_width)**2 + (y_distance * raw_face.image_height)**2 ) ** 0.5

    return distance