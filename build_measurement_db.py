
from core.analysis_pipeline import analyze_image
from core.mediapipe_tasks import (
    create_face_landmarker,
    create_selfie_segmenter,
)
from core.dataset_loader import (
    find_json_files,
    select_first_frontal_samples,
)
from database.database import (
    create_table,
    face_measurement_exists,
    save_face_measurement,
)

from config.settings import (
    SELFIE_MODEL_PATH,
    FACE_LANDMARKER_MODEL_PATH,
    LABELING_DATA_FOLDER,
    RAW_DATA_FOLDER,
)


def main():
    create_table()

    json_files = find_json_files(LABELING_DATA_FOLDER)
    samples = select_first_frontal_samples(
        json_files,
        RAW_DATA_FOLDER,
    )

    face_landmarker = create_face_landmarker(
        FACE_LANDMARKER_MODEL_PATH
    )

    selfie_segmenter = create_selfie_segmenter(
        SELFIE_MODEL_PATH
    )

    try:
        for sample in samples[:3]:
            image_path_string = str(sample.image_path)

            if face_measurement_exists(image_path_string):
                print(f"이미 분석됨: {sample.image_path.name}")
                continue

            result = analyze_image(
                image_path_string,
                face_landmarker,
                selfie_segmenter,
            )
            if result is None:
                continue

            

            save_face_measurement(
                image_path=image_path_string,
                person_id=sample.person_id,
                gt_yaw=sample.gt_yaw,
                gt_pitch=sample.gt_pitch,
                gt_roll=sample.gt_roll,
                frontality_result=result.frontality_result,
                face_measurements=result.face_measurements,
            )

    finally:
        face_landmarker.close()
        selfie_segmenter.close()

if __name__ == "__main__":
    main()