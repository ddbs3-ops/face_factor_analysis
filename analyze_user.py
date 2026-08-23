from unittest import result

from core.analysis_pipeline import analyze_image
from core.mediapipe_tasks import (
    create_face_landmarker,
    create_selfie_segmenter,
)
from core.hair_rules import (
    get_hair_rules,
    merge_hair_rules,
    build_hair_recommendation,
)

from config.settings import (
    SELFIE_MODEL_PATH,
    FACE_LANDMARKER_MODEL_PATH,
    REFERENCE_DB_PATH,
)

import sqlite3
import pandas as pd



def analyze_user_image(image_path):
    face_landmarker = create_face_landmarker(
        FACE_LANDMARKER_MODEL_PATH
    )

    selfie_segmenter = create_selfie_segmenter(
        SELFIE_MODEL_PATH
    )

    try:
        image_analysis = analyze_image(
            image_path,
            face_landmarker,
            selfie_segmenter,
        )

        if image_analysis is None:
            return None

    finally:
        face_landmarker.close()
        selfie_segmenter.close()

    reference_data = load_reference_db()

    measurement_top_percentiles = calculate_measurement_top_percentiles(
        reference_data,
        image_analysis.face_measurements,
    )

    quantized_measurements = {
        key: quantize_top_percent(value)
        for key, value in measurement_top_percentiles.items()
    }

    hair_rules = get_hair_rules(
        image_analysis.face_measurements,
        quantized_measurements,
    )

    hair_result = merge_hair_rules(hair_rules)

    recommendations = build_hair_recommendation(
        hair_result["merged_adjustments"]
    )

    final_result = {
        "frontality_result": image_analysis.frontality_result,
        "face_measurements": image_analysis.face_measurements,
        "measurement_top_percentiles": measurement_top_percentiles,
        "quantized_measurements": quantized_measurements,
        "rules": hair_result["rules"],
        "merged_adjustments": hair_result["merged_adjustments"],
        "recommendations": recommendations,
    }

    return final_result


def load_reference_db():
    conn = sqlite3.connect(REFERENCE_DB_PATH)

    query = """
    SELECT
        height_to_width_ratio,
        upper_ratio,
        middle_ratio,
        lower_ratio,
        jaw_to_cheekbone_width_ratio,
        chin_angle,
        left_jaw_angle,
        right_jaw_angle
    FROM face_measurements
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df


def calculate_top_percentile(series, target_value):
    above_count = (series > target_value).sum()
    top_percent = above_count / len(series) * 100

    return top_percent


def calculate_measurement_top_percentiles(
    reference_data,
    face_measurements,
):
    height_to_width_top_percent = calculate_top_percentile(
        reference_data["height_to_width_ratio"],
        face_measurements.height_to_width_ratio,
    )

    upper_top_percent = calculate_top_percentile(
        reference_data["upper_ratio"],
        face_measurements.vertical_ratios.upper,
    )

    middle_top_percent = calculate_top_percentile(
        reference_data["middle_ratio"],
        face_measurements.vertical_ratios.middle,
    )

    lower_top_percent = calculate_top_percentile(
        reference_data["lower_ratio"],
        face_measurements.vertical_ratios.lower,
    )

    jaw_to_cheekbone_top_percent = calculate_top_percentile(
        reference_data["jaw_to_cheekbone_width_ratio"],
        face_measurements.jaw.jaw_to_cheekbone_width_ratio,
    )

    chin_angle_top_percent = calculate_top_percentile(
        reference_data["chin_angle"],
        face_measurements.jaw.chin_angle_deg,
    )

    left_jaw_angle_top_percent = calculate_top_percentile(
        reference_data["left_jaw_angle"],
        face_measurements.jaw.left_jaw_angle_deg,
    )

    right_jaw_angle_top_percent = calculate_top_percentile(
        reference_data["right_jaw_angle"],
        face_measurements.jaw.right_jaw_angle_deg,
    )

    return {
        "height_to_width_ratio": round(height_to_width_top_percent, 2),
        "upper_ratio": round(upper_top_percent, 2),
        "middle_ratio": round(middle_top_percent, 2),
        "lower_ratio": round(lower_top_percent, 2),
        "jaw_to_cheekbone_width_ratio": round(
            jaw_to_cheekbone_top_percent,
            2,
        ),
        "chin_angle": round(chin_angle_top_percent, 2),
        "left_jaw_angle": round(left_jaw_angle_top_percent, 2),
        "right_jaw_angle": round(right_jaw_angle_top_percent, 2),
    }


def quantize_top_percent(top_percent):
    if top_percent <= 20:
        return 2
    elif top_percent <= 40:
        return 1
    elif top_percent <= 60:
        return 0
    elif top_percent <= 80:
        return -1
    else:
        return -2


def print_analysis_result(final_result):
    print("\n[얼굴 특징]")

    for rule in final_result["rules"]:
        print("-", rule["feature"])

    print("\n[헤어 추천]")

    for recommendation in final_result["recommendations"]:
        print(
            f"- {recommendation['text']} "
            f"(score: {recommendation['score']})"
        )


def main():
    image_path = (
        r"C:\Users\eun\Downloads\sp_data\20220930_ID0161_C_02_N00002.png"
    )

    result = analyze_user_image(image_path)

    if result is None:
        print("얼굴 분석 실패")
        return

    print_analysis_result(result)


if __name__ == "__main__":
    main()