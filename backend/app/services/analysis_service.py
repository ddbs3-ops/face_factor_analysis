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

        raw_face = result["raw_face"]

        left_cheekbone = raw_face.points[234]
        right_cheekbone = raw_face.points[454]

        left_jaw = raw_face.points[172]
        right_jaw = raw_face.points[397]

        jaw = result["face_measurements"].jaw

        left_visual = jaw.left_jaw_visual_points
        right_visual = jaw.right_jaw_visual_points

        chin_visual = jaw.chin_visual_points

        face_height_to_width_visual = result["height_width_ratio_visual_points"]
        frontality = result["frontality_result"]


        return {
            
            "frontality_result": {
                "is_frontal": frontality.is_frontal,
                "pose": {
                    "yaw_deg": frontality.pose.yaw_deg,
                    "pitch_deg": frontality.pose.pitch_deg,
                    "roll_deg": frontality.pose.roll_deg,
                },
                "messages": list(frontality.messages),
                "reasons": list(frontality.reasons),
            },

            "rules": result["rules"],
            "merged_adjustments": result["merged_adjustments"],
            "recommendations": result["recommendations"],
            "measurement_stats": result["measurement_stats"],
            "vertical_ratios": {
                "upper" : result["face_measurements"].vertical_ratios.upper,
                "middle" : result["face_measurements"].vertical_ratios.middle,
                "lower" : result["face_measurements"].vertical_ratios.lower,              
            },

            "vertical_points": {
                "hairline": hairline_y_ratio,
                "glabella": (
                    result["vertical_facepoints"].glabella_y
                    / result["image_height"]
                ),
                "subnasale": (
                    result["vertical_facepoints"].subnasale_y
                    / result["image_height"]
                ),
                "chin": (
                    result["vertical_facepoints"].chin_y
                    / result["image_height"]
                ),
            },

            "jaw_width_ratio": (
                result["face_measurements"]
                .jaw
                .jaw_to_cheekbone_width_ratio
            ),

            "jaw_width_points": {
                "left_cheekbone": {
                    "x": left_cheekbone.x,
                    "y": left_cheekbone.y,
                },
                "right_cheekbone": {
                    "x": right_cheekbone.x,
                    "y": right_cheekbone.y,
                },
                "left_jaw": {
                    "x": left_jaw.x,
                    "y": left_jaw.y,
                },
                "right_jaw": {
                    "x": right_jaw.x,
                    "y": right_jaw.y,
                },
            },

            "jaw_angle_points": {
                "left": {
                    "intersection": {
                        "x": left_visual.intersection.x / result["image_width"],
                        "y": left_visual.intersection.y / result["image_height"],
                    },
                    "upper_end": {
                        "x": left_visual.upper_end.x / result["image_width"],
                        "y": left_visual.upper_end.y / result["image_height"],
                    },
                    "lower_end": {
                        "x": left_visual.lower_end.x / result["image_width"],
                        "y": left_visual.lower_end.y / result["image_height"],
                    },
                },
                "right": {
                    "intersection": {
                        "x": right_visual.intersection.x / result["image_width"],
                        "y": right_visual.intersection.y / result["image_height"],
                    },
                    "upper_end": {
                        "x": right_visual.upper_end.x / result["image_width"],
                        "y": right_visual.upper_end.y / result["image_height"],
                    },
                    "lower_end": {
                        "x": right_visual.lower_end.x / result["image_width"],
                        "y": right_visual.lower_end.y / result["image_height"],
                    },
                },
            },

            "chin_angle_points": {
                "intersection": {
                    "x": chin_visual.intersection.x / result["image_width"],
                    "y": chin_visual.intersection.y / result["image_height"],
                },
                "left_end": {
                    "x": chin_visual.upper_end.x / result["image_width"],
                    "y": chin_visual.upper_end.y / result["image_height"],
                },
                "right_end": {
                    "x": chin_visual.lower_end.x / result["image_width"],
                    "y": chin_visual.lower_end.y / result["image_height"],
                },
            },

            "height_width_ratio_visual_points": {
                "top": {
                    "x": face_height_to_width_visual.top.x / result["image_width"],
                    "y": face_height_to_width_visual.top.y / result["image_height"],
                },
                "bottom": {
                    "x": face_height_to_width_visual.bottom.x / result["image_width"],
                    "y": face_height_to_width_visual.bottom.y / result["image_height"],
                },
            },
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