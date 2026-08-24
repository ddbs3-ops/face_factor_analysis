import os
import tempfile

from fastapi import UploadFile

from analyze_user import analyze_user_image
from core.analysis_pipeline import measure_image
from core.mediapipe_tasks import (
    create_face_landmarker,
    create_selfie_segmenter,
)

from config.settings import (
    SELFIE_MODEL_PATH,
    FACE_LANDMARKER_MODEL_PATH,
)


async def analyze_uploaded_image(
        file: UploadFile,
        hairline_y_ratio: float):
    suffix = os.path.splitext(file.filename)[1]

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    ) as temp_file:
        temp_file.write(await file.read())
        temp_path = temp_file.name

    try:
        result = analyze_user_image(temp_path, hairline_y_ratio)

        if result is None:
            return None

        return {
            "rules": result["rules"],
            "merged_adjustments": result["merged_adjustments"],
            "recommendations": result["recommendations"],
        }

    finally:
        os.remove(temp_path)


async def measure_uploaded_image(file: UploadFile):
    suffix = os.path.splitext(file.filename)[1]

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    ) as temp_file:
        temp_file.write(await file.read())
        temp_path = temp_file.name

    face_landmarker = create_face_landmarker(
        FACE_LANDMARKER_MODEL_PATH
    )

    selfie_segmenter = create_selfie_segmenter(
        SELFIE_MODEL_PATH
    )

    try:
        measurement = measure_image(
            temp_path,
            face_landmarker,
            selfie_segmenter,
        )

        if measurement is None:
            return None

        hairline_y_ratio = (
            measurement.hairline_result.final_y
            / measurement.image_height
        )

        return {
            "hairline_y_ratio": hairline_y_ratio
        }

    finally:
        face_landmarker.close()
        selfie_segmenter.close()
        os.remove(temp_path)