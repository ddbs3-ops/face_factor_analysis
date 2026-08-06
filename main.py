
import numpy as np
import cv2
import mediapipe as mp

from core.frontality import evaluate_frontality
from core.mediapipe_tasks import launch_facelandmark, launch_segment_selfie, prepare_mp_image
from core.hairline import detect_hairline_y, estimate_hairline_y, calculate_vertical_face_lengths
from scipy.spatial.transform import Rotation
from core.face_features import ratio_calculate

from core.schemas import HeadPose, FrontalityResult, Point3D, RawFace

selfiemulticlass_model_path = 'models/selfie_multiclass_256x256.tflite'
launch_facelandmark_model_path = 'models/face_landmarker.task' 



def main():

    img_path = "data/raw/test_face1.jpg"
    mp_image, img_height, img_width = prepare_mp_image(img_path)    #image 불러오기 type(img) == numpy.ndarray
    
    face_landmarker_result = launch_facelandmark(launch_facelandmark_model_path, mp_image)
    segmented_masks_result = launch_segment_selfie(selfiemulticlass_model_path, mp_image)


    len(face_landmarker_result.face_landmarks) 
    print(type(mp_image))
    if len(face_landmarker_result.face_landmarks) > 1:
        print("2명 이상의 사람이 검출되었습니다.")
    elif len(face_landmarker_result.face_landmarks) == 0:
        print("사진에서 사람을 검출하지 못했습니다.")
        return

    #-------------------------------------------------------------------------------------------------------------------
    # 정면성 검사 시작

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

    print(type(segmented_masks_result.category_mask))

    raw_face = create_raw_face(face_landmarker_result, img_width, img_height)
    #---------------------------------------------------------------------------------------------------------
    # 헤어라인 검출 시작 
    category_mask = segmented_masks_result.category_mask.numpy_view()
    category_mask_2d = np.squeeze(category_mask)

    detected_hairline = detect_hairline_y(raw_face, category_mask_2d)
    estimated_hairline = estimate_hairline_y(raw_face)



    if detected_hairline is None:
        hairline_y = estimate_hairline_y(
            raw_face
        )
    else:
        difference = abs(detected_hairline - estimated_hairline)
        allowed_difference = (raw_face.image_height * 0.08)

        if difference > allowed_difference:
            hairline_y = estimated_hairline
        else:
            hairline_y = detected_hairline

    #----------------------요소 검출

    Upper_floor_ratio, middle_floor_ratio, lower_floor_ratio = ratio_calculate(raw_face, hairline_y)
      
    print(Upper_floor_ratio, middle_floor_ratio, lower_floor_ratio)
    
    
    

    # 가로새로 종횡비

    
    
    

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





    

if __name__ == "__main__":
    main()