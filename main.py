"""Opencv로 이미지를 읽는다.
# 사용할 모델 경로, 실행 모드, 검출할 얼굴 수를 설정한다.
얼굴 랜드마크를 검출한다.
분석 파이프라인에 결과를 넘긴다.
계산된 얼굴 지표를 출력한다."""

import numpy as np
import cv2
import mediapipe as mp

from core.frontality import evaluate_frontality

from scipy.spatial.transform import Rotation

from core.schemas import HeadPose
from core.schemas import FrontalityResult

def main():

    img = cv2.imread("data/raw/test_face1.jpg")     #image 불러오기 type(img) == numpy.ndarray
    
    if img is None:
        print("사진을 불러오지 못했습니다.")        
        return
    
    rgb_img = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2RGB           #cv2.imread 는 (B,G,R) but mediapipe는 (R,G,B) 원함
    )

    model_path = 'models/face_landmarker.task' 

    BaseOptions = mp.tasks.BaseOptions
    FaceLandmarker = mp.tasks.vision.FaceLandmarker
    FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode


    options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.IMAGE,
        output_facial_transformation_matrixes=True)         #yaw,roll,deg를 추출하기 위한 변환행렬 가져오는 옵션 

    with FaceLandmarker.create_from_options(options) as landmarker:
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_img)
        face_landmarker_result = landmarker.detect(mp_image)        #mediapipe로 image에서 랜드마크 좌표 추출

    len(face_landmarker_result.face_landmarks) 

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

    
    

    




if __name__ == "__main__":
    main()