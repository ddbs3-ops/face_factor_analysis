from main import load_image, detect_face, create_raw_face
from core.mediapipe_tasks import create_face_landmarker, create_selfie_segmenter
from visualization import draw_face_landmarks
import cv2

TEST_IMAGE_PATH = "data/raw/20221017_ID0252_C_01_N00030.png"
SELFIE_MODEL_PATH = 'models/selfie_multiclass_256x256.tflite'
FACE_LANDMARKER_MODEL_PATH = 'models/face_landmarker.task' 


face_landmarker = create_face_landmarker(
        FACE_LANDMARKER_MODEL_PATH
    )

selfie_segmenter = create_selfie_segmenter(
        SELFIE_MODEL_PATH
    )

img, mp_image, img_height, img_width = load_image(TEST_IMAGE_PATH)
detection_result = detect_face(mp_image, face_landmarker, selfie_segmenter)

if detection_result is not None:
    face_landmark_result, _ = detection_result

    raw_face = create_raw_face(
        face_landmark_result,
        img_width,
        img_height,
    )

    result = draw_face_landmarks(
        img,
        raw_face
    )

    cv2.imshow("landmarks", result)
    cv2.waitKey(0)