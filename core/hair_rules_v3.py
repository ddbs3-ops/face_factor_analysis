HAIR_ELEMENTS = [
    "top_volume",
    "side_volume",
    "forehead_exposure",
    "bangs_length",
    "bangs_weight",
    "parting_asymmetry",
    "curl_strength",
]


def get_hair_rules(
    face_measurements,
    quantized_measurements,
):
    rules = []

    face_height_rule = get_face_height_ratio_rule(
        quantized_measurements
    )

    if face_height_rule is not None:
        rules.append(face_height_rule)


    vertical_ratios_rule = get_vertical_ratio_rule(
        face_measurements,
        quantized_measurements,
    )

    if vertical_ratios_rule is not None:
        rules.append(vertical_ratios_rule)


    lower_face_rule = get_jaw_cheekbone_rule(
        quantized_measurements
    )

    if lower_face_rule is not None:
        rules.append(lower_face_rule)


    jaw_angle_rule = get_jaw_angle_rule(
        quantized_measurements
    )

    if jaw_angle_rule is not None:
        rules.append(jaw_angle_rule)


    chin_angle_rule = get_chin_angle_rule(
        quantized_measurements
    )

    if chin_angle_rule is not None:
        rules.append(chin_angle_rule)

    return rules


def get_face_height_ratio_rule(
    quantized_measurements,
):
    height_level = quantized_measurements[
        "height_to_width_ratio"
    ]

    if height_level >= 1:
        return {
            "source": "face_ratio",
            "face_type": "long",
            "feature": "세로 비율이 상대적으로 큰 긴 얼굴",
            "feature_level": height_level,

            "contributions": [
                {
                    "element": "top_volume",
                    "value": -1,
                    "reason": (
                        "윗머리의 높이를 줄여 얼굴의 세로 길이가 "
                        "더 강조되는 것을 막기 위해서예요."
                    ),
                    "evidence_strength": "direct",
                },
                {
                    "element": "side_volume",
                    "value": 1,
                    "reason": (
                        "옆머리 볼륨을 살려 시선을 가로 방향으로 분산하고 "
                        "긴 얼굴의 세로 비율을 보완하기 위해서예요."
                    ),
                    "evidence_strength": "direct",
                },
                {
                    "element": "forehead_exposure",
                    "value": -1,
                    "reason": (
                        "이마 노출을 줄여 얼굴 위쪽의 세로 길이가 "
                        "더 길어 보이는 것을 막기 위해서예요."
                    ),
                    "evidence_strength": "direct",
                },
                {
                    "element": "bangs_length",
                    "value": 1,
                    "reason": (
                        "앞머리 기장을 확보해 노출되는 얼굴의 세로 길이를 줄이고 "
                        "긴 인상을 완화하기 위해서예요."
                    ),
                    "evidence_strength": "direct",
                },
            ],

            "effect": (
                "윗머리 높이와 이마 노출을 줄이고 "
                "옆머리 볼륨과 앞머리 기장을 활용해 "
                "얼굴의 세로 강조를 완화"
            ),
        }

    elif height_level <= -1:
        return {
            "source": "face_ratio",
            "face_type": "short",
            "feature": "가로 비율이 상대적으로 큰 짧은 얼굴",
            "feature_level": height_level,

            "contributions": [
                {
                    "element": "top_volume",
                    "value": 1,
                    "reason": (
                        "윗머리 볼륨을 살려 얼굴의 세로 비율을 늘리고 "
                        "둥글고 눌린 인상을 완화하기 위해서예요."
                    ),
                    "evidence_strength": "direct",
                },
                {
                    "element": "forehead_exposure",
                    "value": 1,
                    "reason": (
                        "이마를 드러내 얼굴의 세로 노출을 늘리고 "
                        "가로로 넓어 보이는 비율을 보완하기 위해서예요."
                    ),
                    "evidence_strength": "direct",
                },
                {
                    "element": "side_volume",
                    "value": -1,
                    "reason": (
                        "옆머리의 부피를 줄여 얼굴의 가로 폭이 "
                        "더 넓어 보이는 것을 막기 위해서예요."
                    ),
                    "evidence_strength": "direct",
                },
                {
                    "element": "curl_strength",
                    "value": -1,
                    "reason": (
                        "과한 곡선감을 줄이고 보다 직선적이고 샤프한 질감을 활용해 "
                        "둥근 인상이 더 강조되지 않도록 하기 위해서예요."
                    ),
                    "evidence_strength": "direct",
                },
            ],

            "effect": (
                "이마 노출과 윗머리 볼륨으로 세로 비율을 늘리고 "
                "옆머리 부피와 과한 곡선감을 줄여 "
                "가로로 넓고 둥근 인상을 완화"
            ),
        }

    else:
        return {
            "source": "face_ratio",
            "face_type": "average",
            "feature": "세로·가로 비율이 평균적인 얼굴",
            "feature_level": height_level,
            "contributions": [],
            "effect": (
                "얼굴의 세로·가로 비율이 평균 범위이므로 "
                "종횡비에 대한 특별한 보정은 필요하지 않음"
            ),
        }
    


def get_vertical_ratio_rule(
    face_measurements,
    quantized_measurements,
):
    vertical_ratios = {
        "upper": face_measurements.vertical_ratios.upper,
        "middle": face_measurements.vertical_ratios.middle,
        "lower": face_measurements.vertical_ratios.lower,
    }

    # 현재는 가장 큰 영역 하나를 dominant region으로 선택한다.
    # 향후 upper/middle/lower 각각의 reference percentile을
    # 독립적으로 해석하는 방식도 검토할 수 있음.
    dominant_region = max(
        vertical_ratios,
        key=vertical_ratios.get,
    )

    dominant_level = quantized_measurements[
        f"{dominant_region}_ratio"
    ]

    if dominant_region == "upper":
        return {
            "source": "vertical_ratio",
            "dominant_region": "upper",
            "feature": "상안부 비율이 상대적으로 큰 얼굴",
            "feature_level": dominant_level,

            "contributions": [
                {
                    "element": "forehead_exposure",
                    "value": -1,
                    "reason": (
                        "이마 노출을 줄여 넓은 상안부의 면적과 "
                        "세로 길이가 더 강조되지 않도록 하기 위해서예요."
                    ),
                    "evidence_strength": "direct",
                },
                {
                    "element": "bangs_weight",
                    "value": -1,
                    "reason": (
                        "이마는 자연스럽게 가리되 무거운 풀뱅보다 "
                        "가벼운 앞머리 질감을 사용해 답답한 인상을 줄이기 위해서예요."
                    ),
                    "evidence_strength": "direct",
                },
                {
                    "element": "parting_asymmetry",
                    "value": 1,
                    "reason": (
                        "정가르마가 만드는 중앙의 수직선을 피하고 "
                        "시선을 분산해 상안부의 세로 강조를 줄이기 위해서예요."
                    ),
                    "evidence_strength": "direct",
                },
            ],

            "effect": (
                "이마 노출을 줄이고 가벼운 앞머리와 비대칭 가르마를 활용해 "
                "상안부의 넓은 면적과 세로 강조를 완화"
            ),
        }

    elif dominant_region == "middle":
        return {
            "source": "vertical_ratio",
            "dominant_region": "middle",
            "feature": "중안부 비율이 상대적으로 큰 얼굴",
            "feature_level": dominant_level,

            "contributions": [
                {
                    "element": "bangs_length",
                    "value": 1,
                    "reason": (
                        "앞머리 기장을 충분히 확보해 중안부 주변에 "
                        "시선이 고립되는 것을 줄이기 위해서예요."
                    ),
                    "evidence_strength": "direct",
                },
                {
                    "element": "side_volume",
                    "value": 1,
                    "reason": (
                        "옆머리 볼륨을 살려 세로로 집중되는 시선을 "
                        "가로 방향으로 분산하기 위해서예요."
                    ),
                    "evidence_strength": "direct",
                },
                {
                    "element": "forehead_exposure",
                    "value": 1,
                    "reason": (
                        "이마를 완전히 가려 중안부와 하관에 시선이 "
                        "집중되는 것을 피하고 시선을 위쪽으로 분산하기 위해서예요."
                    ),
                    "evidence_strength": "direct",
                },
                {
                    "element": "curl_strength",
                    "value": 1,
                    "reason": (
                        "곡선적인 헤어 질감을 활용해 중안부의 "
                        "직선적인 세로 인상을 분산하기 위해서예요."
                    ),
                    "evidence_strength": "direct",
                },
            ],

            "effect": (
                "앞머리 기장과 옆머리 볼륨, 적절한 이마 노출과 곡선감을 활용해 "
                "중안부에 집중되는 시선을 위와 좌우 방향으로 분산"
            ),
        }

    else:
        return {
            "source": "vertical_ratio",
            "dominant_region": "lower",
            "feature": "하안부 비율이 상대적으로 큰 얼굴",
            "feature_level": dominant_level,

            "contributions": [
                {
                    "element": "forehead_exposure",
                    "value": 1,
                    "reason": (
                        "이마를 드러내 시선을 얼굴 위쪽으로 끌어올리고 "
                        "긴 하안부와 턱에 시선이 집중되는 것을 줄이기 위해서예요."
                    ),
                    "evidence_strength": "direct",
                },
            ],

            "effect": (
                "이마를 드러내 시선을 상단으로 유도해 "
                "긴 하안부에 집중되는 시선을 분산"
            ),
        }
    

def get_jaw_cheekbone_rule(
    quantized_measurements,
):
    jaw_width_level = quantized_measurements[
        "jaw_to_cheekbone_width_ratio"
    ]

    if jaw_width_level >= 1:
        return {
            "source": "jaw_width",
            "feature": "광대 대비 턱 폭이 넓은 편",
            "feature_level": jaw_width_level,

            "contributions": [
                {
                    "element": "forehead_exposure",
                    "value": 1,
                    "reason": (
                        "이마를 드러내 시선을 얼굴 위쪽으로 분산하고 "
                        "넓은 하관에 시선이 집중되는 것을 줄이기 위해서예요."
                    ),
                    "evidence_strength": "direct",
                },
                {
                    "element": "side_volume",
                    "value": -1,
                    "reason": (
                        "옆머리와 구렛나루의 부피를 줄여 "
                        "넓은 하관의 가로 폭이 더 강조되지 않도록 하기 위해서예요."
                    ),
                    "evidence_strength": "direct",
                },
                {
                    "element": "curl_strength",
                    "value": 1,
                    "reason": (
                        "곡선적인 헤어 질감을 활용해 "
                        "넓고 강하게 보일 수 있는 하관 윤곽을 부드럽게 완화하기 위해서예요."
                    ),
                    "evidence_strength": "direct",
                },
            ],

            "effect": (
                "이마를 열어 시선을 위쪽으로 분산하고 "
                "옆머리의 과도한 부피를 줄이며 "
                "곡선적인 질감으로 넓은 하관 윤곽을 부드럽게 보완"
            ),
        }

    elif jaw_width_level <= -1:
        return {
            "source": "jaw_width",
            "feature": "광대 대비 턱 폭이 좁은 편",
            "feature_level": jaw_width_level,

            "contributions": [
                {
                    "element": "side_volume",
                    "value": -1,
                    "reason": (
                        "옆머리의 부피를 줄여 상부와 하부의 폭 차이가 "
                        "더 크게 강조되지 않도록 하기 위해서예요."
                    ),
                    "evidence_strength": "direct",
                },
                {
                    "element": "forehead_exposure",
                    "value": -1,
                    "reason": (
                        "이마를 과하게 드러내면 광대에서 턱으로 좁아지는 "
                        "윤곽이 더 직접적으로 드러날 수 있어 이를 완화하기 위해서예요."
                    ),
                    "evidence_strength": "direct",
                },
                {
                    "element": "curl_strength",
                    "value": 1,
                    "reason": (
                        "곡선적인 헤어 질감을 활용해 광대에서 턱으로 "
                        "급격하게 좁아지는 윤곽을 부드럽게 완화하기 위해서예요."
                    ),
                    "evidence_strength": "direct",
                },
            ],

            "effect": (
                "옆머리의 과도한 부피와 이마 노출을 줄이고 "
                "곡선적인 질감을 활용해 광대에서 턱으로 좁아지는 "
                "윤곽의 대비를 완화"
            ),
        }

    else:
        return {
            "source": "jaw_width",
            "feature": "광대 대비 턱 폭이 평균적인 얼굴",
            "feature_level": jaw_width_level,
            "contributions": [],
            "effect": (
                "광대 대비 턱 폭이 평균 범위이므로 "
                "턱 폭에 대한 특별한 보정은 필요하지 않음"
            ),
        }


def get_jaw_angle_rule(
    quantized_measurements,
):
    jaw_angle_level = quantized_measurements["jaw_angle"]

    # 현재는 좌우 하악각의 평균적인 경향만 사용.
    # TODO: 좌우 차이는 향후 asymmetry 규칙에서 별도 처리.

    if jaw_angle_level >= 1:
        return {
            "source": "jaw_angle",
            "feature": "하악각이 상대적으로 각진 얼굴",
            "feature_level": jaw_angle_level,

            "contributions": [
                {
                    "element": "bangs_weight",
                    "value": -1,
                    "reason": (
                        "무거운 일자 앞머리가 만드는 가로 프레임이 "
                        "각진 하악선으로 시선을 집중시키는 것을 줄이기 위해서예요."
                    ),
                    "evidence_strength": "direct",
                },
                {
                    "element": "curl_strength",
                    "value": 1,
                    "reason": (
                        "자연스러운 곡선 질감을 활용해 "
                        "직선적이고 각진 하악선을 부드럽게 완화하기 위해서예요."
                    ),
                    "evidence_strength": "direct",
                },
            ],

            "effect": (
                "무거운 앞머리의 프레임을 줄이고 "
                "자연스러운 곡선 질감을 활용해 "
                "각진 하악선을 부드럽게 보완"
            ),
        }

    elif jaw_angle_level <= -1:
        return {
            "source": "jaw_angle",
            "feature": "하악각이 상대적으로 완만한 얼굴",
            "feature_level": jaw_angle_level,
            "contributions": [],
            "effect": (
                "하악각이 비교적 완만한 편이며 "
                "현재 수집된 근거만으로는 별도의 보정 방향을 적용하지 않음"
            ),
        }

    else:
        return {
            "source": "jaw_angle",
            "feature": "하악각이 평균적인 얼굴",
            "feature_level": jaw_angle_level,
            "contributions": [],
            "effect": (
                "하악각이 평균 범위이므로 "
                "하악각에 대한 특별한 보정은 필요하지 않음"
            ),
        }
        


def get_chin_angle_rule(
    quantized_measurements,
):
    chin_angle_level = quantized_measurements["chin_angle"]

    if chin_angle_level >= 1:
        return {
            "source": "chin_angle",
            "feature": "턱끝이 상대적으로 뭉툭한 얼굴",
            "feature_level": chin_angle_level,

            "contributions": [
                {
                    "element": "top_volume",
                    "value": 1,
                    "reason": (
                        "윗머리에 높이와 시각적 포인트를 만들어 "
                        "둥글고 흐릿한 턱끝에 시선이 집중되는 것을 줄이기 위해서예요."
                    ),
                    "evidence_strength": "direct",
                },
                {
                    "element": "curl_strength",
                    "value": -1,
                    "reason": (
                        "과한 둥근 컬을 줄이고 보다 플랫한 질감을 활용해 "
                        "턱끝의 둥글고 뭉툭한 인상이 더 강조되지 않도록 하기 위해서예요."
                    ),
                    "evidence_strength": "direct",
                },
            ],

            "effect": (
                "윗머리로 시선을 끌어올리고 "
                "과도한 둥근 질감을 줄여 "
                "뭉툭한 턱끝의 인상을 완화"
            ),
        }

    elif chin_angle_level <= -1:
        return {
            "source": "chin_angle",
            "feature": "턱끝이 상대적으로 뾰족한 얼굴",
            "feature_level": chin_angle_level,

            "contributions": [
                {
                    "element": "top_volume",
                    "value": -1,
                    "reason": (
                        "윗머리의 높이를 과도하게 키우지 않아 "
                        "뾰족한 턱끝과 얼굴 상단의 세로 대비가 "
                        "더 강조되지 않도록 하기 위해서예요."
                    ),
                    "evidence_strength": "direct",
                },
                {
                    "element": "curl_strength",
                    "value": 1,
                    "reason": (
                        "부드러운 곡선 질감을 활용해 "
                        "뾰족하고 날카로운 턱끝의 인상을 "
                        "완화하기 위해서예요."
                    ),
                    "evidence_strength": "direct",
                },
            ],

            "effect": (
                "윗머리 높이를 과도하게 키우지 않고 "
                "부드러운 곡선 질감을 활용해 "
                "뾰족한 턱끝의 날카로운 인상을 완화"
            ),
        }

    else:
        return {
            "source": "chin_angle",
            "feature": "턱끝 각도가 평균적인 얼굴",
            "feature_level": chin_angle_level,
            "contributions": [],
            "effect": (
                "턱끝 각도가 평균 범위이므로 "
                "턱끝에 대한 특별한 보정은 필요하지 않음"
            ),
        }


def merge_hair_rules(rules):
    merged = {
        element: {
            "score": 0,
            "contributions": [],
        }
        for element in HAIR_ELEMENTS
    }

    for rule in rules:
        for contribution in rule["contributions"]:
            element = contribution["element"]
            value = contribution["value"]

            merged[element]["score"] += value

            merged[element]["contributions"].append({
                "source": rule["source"],
                "feature": rule["feature"],
                "feature_level": rule["feature_level"],
                "value": value,
                "reason": contribution["reason"],
                "evidence_strength": contribution["evidence_strength"],
            })

    return merged

def build_hair_recommendation(merged_rules):
    recommendations = []

    recommendation_texts = {
        "top_volume": {
            "positive": "윗머리 볼륨을 살리는 방향",
            "negative": "윗머리 볼륨을 낮추는 방향",
        },
        "side_volume": {
            "positive": "옆머리 볼륨을 살리는 방향",
            "negative": "옆머리 볼륨을 줄이는 방향",
        },
        "forehead_exposure": {
            "positive": "이마를 더 드러내는 방향",
            "negative": "이마 노출을 줄이는 방향",
        },
        "bangs_length": {
            "positive": "앞머리를 길게 가져가는 방향",
            "negative": "앞머리를 짧게 가져가는 방향",
        },
        "bangs_weight": {
            "positive": "앞머리에 무게감을 주는 방향",
            "negative": "앞머리를 가볍게 가져가는 방향",
        },
        "parting_asymmetry": {
            "positive": "가르마를 비대칭적으로 가져가는 방향",
            "negative": "가르마를 대칭적으로 가져가는 방향",
        },
        "curl_strength": {
            "positive": "컬감을 살리는 방향",
            "negative": "컬을 줄이고 직선적인 느낌을 살리는 방향",
        },
    }
    
    for element, data in merged_rules.items():
        score = data["score"]

        if score == 0:
            continue

        if score > 0:
            direction = "positive"
            filtered_contributions = [
                contribution
                for contribution in data["contributions"]
                if contribution["value"] > 0
            ]
        else:
            direction = "negative"
            filtered_contributions = [
                contribution
                for contribution in data["contributions"]
                if contribution["value"] < 0
            ]

        reasons = []

        for contribution in filtered_contributions:
            reasons.append({
                "source": contribution["source"],
                "feature": contribution["feature"],
                "feature_level": contribution["feature_level"],
                "contribution": contribution["value"],
                "reason": contribution["reason"],
                "evidence_strength": contribution["evidence_strength"],
            })

        recommendations.append({
            "element": element,
            "score": score,
            "text": recommendation_texts[element][direction],
            "reasons": reasons,
        })

    return recommendations