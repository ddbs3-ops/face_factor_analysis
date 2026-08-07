from core.schemas import *

def calculate_distance(
        point1 : Point2D,
        point2 : Point2D
):
    x_distance = abs(point1.x - point2.x)
    y_distance = abs(point1.y - point2.y)

    distance = ((x_distance)**2 + (y_distance)**2 ) ** 0.5

    return distance