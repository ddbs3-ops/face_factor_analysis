from main import load_image, detect_face, create_raw_face
from core.mediapipe_tasks import create_face_landmarker, create_selfie_segmenter
from core.hairline import *
import matplotlib.pyplot as plt

TEST_IMAGE_PATH = "data/raw/20221020_ID0280_C_02_N00001.png"
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
    face_landmark_result, segmented_masks_result = detection_result

    raw_face = create_raw_face(
        face_landmark_result,
        img_width,
        img_height
    )

    vertical_facepoints = get_vertical_landmark_y(raw_face)

    estimated_y = estimate_hairline_y(
        raw_face,
        vertical_facepoints
    )

    category_mask = segmented_masks_result.category_mask.numpy_view()
    category_mask_2d = category_mask.squeeze()

    roi_info = get_forehead_roi(
        raw_face,
        category_mask_2d,
        vertical_facepoints,
    )

    skin_ratios = calculate_skin_ratio_profile(
        category_mask_2d,
        roi_info,
    )

    y_values = range(
        roi_info.top_y,
       roi_info.top_y + len(skin_ratios)
    )
    boundary_points = get_skin_hair_boundary_points(
        category_mask_2d,
        roi_info,
    )

    x_values = [point[0] for point in boundary_points]
    y_values = [point[1] for point in boundary_points]

    plt.scatter(x_values, y_values, s=5)

    plt.axhline(
        y=estimated_y,
        linestyle="--",
        label="Estimated hairline"
    )

    plt.gca().invert_yaxis()
    plt.xlabel("Image x")
    plt.ylabel("Boundary y")
    plt.title("Skin-Hair Boundary")
    plt.show()









    

