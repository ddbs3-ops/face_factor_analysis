
import numpy as np
import cv2
import mediapipe as mp

from core.frontality import evaluate_frontality
from core.mediapipe_tasks import launch_facelandmark, launch_segment_selfie, prepare_mp_image
from core.hairline import detect_hairline_y, estimate_hairline_y ,get_vertical_landmark_y
from scipy.spatial.transform import Rotation
from core.face_features import *

from core.schemas import *

from config import landmark_indices as landmark

SELFIE_MODEL_PATH = 'models/selfie_multiclass_256x256.tflite'
FACE_LANDMARKER_MODEL_PATH = 'models/face_landmarker.task' 

IMAGE_PATH = "data/raw/test_face.jpg"


def main():

    img, mp_image, img_height, img_width = load_image(IMAGE_PATH)

    detection_result = detect_face(mp_image)

    if detection_result is None:
        return
    
    face_landmarker_result, segmented_masks_result = detection_result

    #-------------------------------------------------------------------------------------------------------------------
    # 정면성 검사 시작
    check_frontality(face_landmarker_result) #일단 쓰이지 않으므로 함수 호출만 함 return도 없음

    raw_face = create_raw_face(face_landmarker_result, img_width, img_height)
    vertical_facepoints = get_vertical_landmark_y(raw_face) #이거 좀 불편하네 어떻게 하긴 해야할듯
    #---------------------------------------------------------------------------------------------------------
    # 헤어라인 검출 시작 
    hairline_result = analyze_hairline(
        segmented_masks_result=segmented_masks_result, 
        raw_face=raw_face,
        vertical_facepoints=vertical_facepoints
        )

    #----------------------요소 검출
    face_measurements = analyze_face_measurements(raw_face=raw_face, 
        vertical_facepoints=vertical_facepoints,
        hairline_y= hairline_result.final_y)

    print(face_measurements.width_to_height_ratio)

    print(face_measurements.vertical_ratios.upper)
    print(face_measurements.vertical_ratios.middle)
    print(face_measurements.vertical_ratios.lower)

    print(face_measurements.jaw.chin_angle_deg)
    print(face_measurements.jaw.left_jaw_angle_deg)
    print(face_measurements.jaw.right_jaw_angle_deg) # 180 - deg 해야할듯

    print(face_measurements.jaw.chin_contour_angles_deg)
    print(face_measurements.jaw.left_jaw_contour_angles_deg)
    print(face_measurements.jaw.right_jaw_contour_angles_deg)


    




    show_img_third(img = img,hairline_y=hairline_result.final_y,detected_y=hairline_result.detected_y,
                   estimated_y=hairline_result.estimated_y, raw_face=raw_face)





def show_img_third(
        img,
        hairline_y,
        detected_y,
        estimated_y,
        raw_face 
):  
    
    cv2.line(img, (0, int(hairline_y)), (raw_face.image_width-1, int(hairline_y)), (0,0,255),3)
    cv2.line(img, (0, int(detected_y)), (raw_face.image_width-1, int(detected_y)), (0,255,0),2)
    cv2.line(img, (0, int(estimated_y)), (raw_face.image_width-1, int(estimated_y)), (255,0,0),2)
    
    glabella_y = int(((raw_face.points[8].y+raw_face.points[9].y)/2)*raw_face.image_height)
    subnose_y = int(raw_face.points[94].y*raw_face.image_height)
    chin_y = int(raw_face.points[152].y*raw_face.image_height)
    cv2.line(img, (0, glabella_y), (raw_face.image_width-1, glabella_y), (0,0,255),2)
    cv2.line(img, (0, subnose_y), (raw_face.image_width-1, subnose_y), (0,0,255),2)
    cv2.line(img, (0, chin_y), (raw_face.image_width-1, chin_y), (0,0,255),2)

    left_zygion = raw_face.points[234]
    right_zygion = raw_face.points[454]

    cv2.line(
        img,
        (
        int(left_zygion.x * raw_face.image_width),
        int(left_zygion.y * raw_face.image_height),
        ),
        (
        int(right_zygion.x * raw_face.image_width),
        int(right_zygion.y * raw_face.image_height),
        ),
        (0, 255, 255),
        2,
    )
    

    cv2.imshow("Image",img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    

def create_raw_face(
        face_landmark_result,
        image_width: int,
        image_height: int,
):
    landmarks = face_landmark_result.face_landmarks[0]

    points_list = []

    for landmark in landmarks:
        new_point = Point3D(
            x=landmark.x,
            y=landmark.y,
            z=landmark.z,
        )
        points_list.append(new_point)

    points = tuple(points_list)

    return RawFace(
        points=points,
        image_height=image_height,
        image_width=image_width,
    )

def load_image(
    path : str,
):
    img_path = path
    img = cv2.imread(img_path)
    mp_image, img_height, img_width = prepare_mp_image(img_path)    #image 불러오기 type(img) == numpy.ndarray

    return img, mp_image, img_height, img_width


def detect_face(mp_image):
    face_landmarker_result = launch_facelandmark(FACE_LANDMARKER_MODEL_PATH, mp_image)
    segmented_masks_result = launch_segment_selfie(SELFIE_MODEL_PATH, mp_image)


    face_count = len(face_landmarker_result.face_landmarks) 
    
    if face_count > 1:
        print("2명 이상의 사람이 검출되었습니다.")
        return None

    elif face_count == 0:
        print("사진에서 사람을 검출하지 못했습니다.")
        return None
    
    return face_landmarker_result, segmented_masks_result


def check_frontality(
    face_landmarker_result
):
    trans_matrix = np.array(face_landmarker_result.facial_transformation_matrixes[0], dtype=np.float64)
    frontality_result=evaluate_frontality(trans_matrix)

    if frontality_result.is_frontal:
        print("정면성 기준을 통과했습니다.")
    else:
        for message in frontality_result.messages:
            print(message)
        for reason in frontality_result.reasons:
            print(reason)
    
        print("그렇지 않으면 향후 검출 값이 오류를 발생할 수 있습니다.")


def analyze_hairline(
    segmented_masks_result,
    raw_face,
    vertical_facepoints,
):
    category_mask = segmented_masks_result.category_mask.numpy_view()
    category_mask_2d = np.squeeze(category_mask)

    detected_hairline = detect_hairline_y(raw_face, category_mask_2d)
    estimated_hairline = estimate_hairline_y(raw_face, vertical_facepoints)

    if detected_hairline is None:
        hairline_y = estimate_hairline_y(
            raw_face,
            vertical_facepoints
        )
    else:
        difference = abs(detected_hairline - estimated_hairline)
        allowed_difference = (raw_face.image_height * 0.08)

        if difference > allowed_difference:
            hairline_y = estimated_hairline
            print("앞머리로 인한 추정치 입니다.")
        else:
            hairline_y = detected_hairline
            print("영역분리 기준 헤어 라인")
    hairline_result = HairlineResult(
        detected_y=detected_hairline,
        estimated_y=estimated_hairline,
        final_y=hairline_y,
    )

    return hairline_result

def analyze_face_measurements(
    raw_face : RawFace,
    hairline_y,
    vertical_facepoints
):
    face_ratios = calculate_vertical_face_ratios(hairline_y, vertical_facepoints) # 3,4,5 상중하안부 비율

    face_width_height_ratio = calculate_face_width_height_ratio(hairline_y, raw_face) # 1 얼굴 가로 세로 종횡비
    jaw_cheekbone_width_ratio = calculate_jaw_to_cheekbone_width_ratio(raw_face) # 2 턱/ 광대 폭 비율

    chin_contour = calculate_face_contour_local_angles(landmark.CHIN_CONTOUR_INDICES, raw_face) #턱끝 중글기
    left_jaw_contour = calculate_face_contour_local_angles(landmark.LEFT_JAW_CONTOUR_INDICES, raw_face) # 왼쪽 하악각 둥글기
    right_jaw_contour = calculate_face_contour_local_angles(landmark.RIGHT_JAW_CONTOUR_INDICES, raw_face) # 오른쪽 하악각 둥글기
    
    
    chin_angle = calculate_angle_between_landmark_lines(
        raw_face,
        landmark.CHIN_LEFT_LINE_INDICES,
        landmark.CHIN_RIGHT_LINE_INDICES,
    ) # 턱 끝 각도

    left_jaw_angle = calculate_angle_between_landmark_lines(
        raw_face,
        landmark.LEFT_JAW_UPPER_LINE_INDICES,
        landmark.LEFT_JAW_LOWER_LINE_INDICES,
    ) # 왼쪽 하악각 각도

    right_jaw_angle = calculate_angle_between_landmark_lines(
        raw_face,
        landmark.RIGHT_JAW_UPPER_LINE_INDICES,
        landmark.RIGHT_JAW_LOWER_LINE_INDICES,
    ) # 오른쪽 하악각 각도

    jaw_measurements = JawMeasurements(
        jaw_to_cheekbone_width_ratio=jaw_cheekbone_width_ratio,
        chin_contour_angles_deg=chin_contour,
        left_jaw_contour_angles_deg=left_jaw_contour,
        right_jaw_contour_angles_deg=right_jaw_contour,
        chin_angle_deg=chin_angle,
        left_jaw_angle_deg=left_jaw_angle,
        right_jaw_angle_deg=right_jaw_angle,
    )
    
    return FaceMeasurements(
        width_to_height_ratio=face_width_height_ratio,
        vertical_ratios=face_ratios,
        jaw=jaw_measurements,
    )



if __name__ == "__main__":
    main()
