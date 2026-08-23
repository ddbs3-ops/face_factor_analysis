
import cv2
import numpy as np

from config import landmark_indices as landmark
from core.face_features import (
    calculate_angle_between_landmark_lines,
    calculate_face_contour_local_angles,
    calculate_face_height_to_width_ratio,
    calculate_jaw_to_cheekbone_width_ratio,
    calculate_vertical_face_ratios,
)
from core.frontality import evaluate_frontality
from core.hairline import (
    detect_hairline_y,
    estimate_hairline_y,
    get_vertical_landmark_y,
)
from core.mediapipe_tasks import (
    launch_facelandmark,
    launch_segment_selfie,
    prepare_mp_image,
)
from core.schemas import (
    FaceMeasurements,
    HairlineResult,
    ImageAnalysisResult,
    ImageMeasurementResult,
    JawMeasurements,
    Point3D,
    RawFace,
)
  

    
def analyze_image(
    image_path,
    face_landmarker,
    selfie_segmenter,
    hairline_y_ratio=None,
):
    measurement = measure_image(
        image_path,
        face_landmarker,
        selfie_segmenter,
    )

    if measurement is None:
        return None

    if hairline_y_ratio is not None:
        hairline_y = (
            hairline_y_ratio
            * measurement.image_height
        )
    else:
        hairline_y = (
            measurement.hairline_result.final_y
        )

    face_measurements = analyze_face_measurements(
        raw_face=measurement.raw_face,
        vertical_facepoints=measurement.vertical_facepoints,
        hairline_y=hairline_y,
    )

    return ImageAnalysisResult(
        frontality_result=measurement.frontality_result,
        face_measurements=face_measurements,
        hairline_result=measurement.hairline_result,
        image_width=measurement.image_width,
        image_height=measurement.image_height,
    )

def measure_image(image_path, face_landmarker, selfie_segmenter):
    img, mp_image, img_height, img_width = load_image(image_path)
    detection_result = detect_face(mp_image, face_landmarker, selfie_segmenter)

    if detection_result is None:
        return None
    
    face_landmarker_result, segmented_masks_result = detection_result

    # 정면성 검사 시작
    frontality_result = check_frontality(face_landmarker_result) #일단 쓰이지 않으므로 함수 호출만 함 return도 없음

    raw_face = create_raw_face(face_landmarker_result, img_width, img_height)
    vertical_facepoints = get_vertical_landmark_y(raw_face) 

    # 헤어라인 검출 시작 
    hairline_result = analyze_hairline(
        segmented_masks_result=segmented_masks_result, 
        raw_face=raw_face,
        vertical_facepoints=vertical_facepoints
        )

    return ImageMeasurementResult(
        frontality_result=frontality_result,
        raw_face=raw_face,
        vertical_facepoints=vertical_facepoints,
        hairline_result=hairline_result,
        image_width=img_width,
        image_height=img_height,
    )

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


def detect_face(
        mp_image,
        face_landmarker,
        selfie_segmenter):
    face_landmarker_result = launch_facelandmark(face_landmarker, mp_image)
    segmented_masks_result = launch_segment_selfie(selfie_segmenter, mp_image)


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

    return frontality_result


HAIRLINE_DIFFERENCE_THRESHOLD = 0.30


def analyze_hairline(
    segmented_masks_result,
    raw_face,
    vertical_facepoints,
):
    category_mask = segmented_masks_result.category_mask.numpy_view()
    category_mask_2d = np.squeeze(category_mask)

    detected_hairline = detect_hairline_y(
        raw_face,
        category_mask_2d,
    )

    estimated_hairline = estimate_hairline_y(
        vertical_facepoints
    )

    if detected_hairline is None:
        hairline_y = estimated_hairline

    else:
        middle_face_length = (
            vertical_facepoints.subnasale_y
            - vertical_facepoints.glabella_y
        )

        difference_ratio = (
            abs(detected_hairline - estimated_hairline)
            / middle_face_length
        )

        if difference_ratio > HAIRLINE_DIFFERENCE_THRESHOLD:
            hairline_y = estimated_hairline
            print("앞머리로 인한 추정치입니다.")
        else:
            hairline_y = detected_hairline
            print("영역분리 기준 헤어라인입니다.")

    return HairlineResult(
        detected_y=detected_hairline,
        estimated_y=estimated_hairline,
        final_y=hairline_y,
    )

def analyze_face_measurements(
    raw_face : RawFace,
    hairline_y,
    vertical_facepoints
):
    face_ratios = calculate_vertical_face_ratios(hairline_y, vertical_facepoints) # 3,4,5 상중하안부 비율

    face_height_width_ratio = calculate_face_height_to_width_ratio(hairline_y, raw_face) # 1 얼굴 세로/가로 종횡비
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
        height_to_width_ratio=face_height_width_ratio,
        vertical_ratios=face_ratios,
        jaw=jaw_measurements,
    )
 
