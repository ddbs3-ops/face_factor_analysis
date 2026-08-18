import cv2
import mediapipe as mp



def prepare_mp_image(
        img_path : str
):
    img = cv2.imread(img_path)

    if img is None:
            raise FileNotFoundError( f"사진을 불러오지 못했습니다: {img_path}" )

    height, width = img.shape[:2]

    rgb_img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)          #cv2.imread 는 (B,G,R) but mediapipe는 (R,G,B) 원함
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_img)


    return mp_image, height, width

def create_face_landmarker(model_path: str):
    BaseOptions = mp.tasks.BaseOptions
    FaceLandmarker = mp.tasks.vision.FaceLandmarker
    FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.IMAGE,
        output_facial_transformation_matrixes=True,
    )

    return FaceLandmarker.create_from_options(options)

def create_selfie_segmenter(model_path: str):
    BaseOptions = mp.tasks.BaseOptions
    ImageSegmenter = mp.tasks.vision.ImageSegmenter
    ImageSegmenterOptions = mp.tasks.vision.ImageSegmenterOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    options = ImageSegmenterOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.IMAGE,
        output_category_mask=True,
    )

    return ImageSegmenter.create_from_options(options)

def launch_facelandmark(landmarker, mp_image):
    return landmarker.detect(mp_image)


def launch_segment_selfie(segmenter, mp_image):
    return segmenter.segment(mp_image)

