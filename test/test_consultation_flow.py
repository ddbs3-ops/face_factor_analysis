import unittest

from backend.app.services.consultation_flow_service import (
    build_guided_consultation_sentences,
    load_consultation_flow,
    resolve_guided_answers,
)


class CustomInputAnswersTest(unittest.TestCase):
    def test_cut_avoid_styles_support_custom_text_alone_or_with_options(self):
        node = load_consultation_flow()["nodes"]["cut_avoid_styles"]
        self.assertEqual(node["type"], "multi")
        self.assertEqual(node["next"], "cut_growing_hair_undecided")
        for selected, expected in [
            (["other"], []),
            (["too_short", "other"], ["너무 짧은 머리 같은 스타일은 피하고 싶어요."]),
        ]:
            with self.subTest(selected=selected):
                resolved = resolve_guided_answers({
                    "cut_avoid_styles": selected,
                    "cut_avoid_styles_custom": " 앞머리가 눈을 가리는 건 싫어요. ",
                })
                self.assertEqual(resolved["cut_avoid_styles_custom"], "앞머리가 눈을 가리는 건 싫어요.")
                self.assertEqual(build_guided_consultation_sentences(resolved), expected + [
                    "피하고 싶은 내용을 직접 적었어요: “앞머리가 눈을 가리는 건 싫어요.”",
                ])

    def test_cut_avoid_styles_ignore_deselected_or_orphan_custom_text(self):
        resolved = resolve_guided_answers({
            "cut_avoid_styles": ["too_short"], "cut_avoid_styles_custom": "이전 입력",
        })
        self.assertEqual(resolved, {"cut_avoid_styles": ["너무 짧은 머리"]})
        self.assertEqual(build_guided_consultation_sentences(resolved), [
            "너무 짧은 머리 같은 스타일은 피하고 싶어요.",
        ])
        self.assertEqual(resolve_guided_answers({"cut_avoid_styles_custom": "이전 입력"}), {})

    def test_tools_and_products_are_resolved_and_included_in_sentences(self):
        resolved = resolve_guided_answers({
            "styling_tools": ["hair_dryer", "other"],
            "styling_tools_custom": " 매직 롤 ",
            "styling_products": ["wax", "other"],
            "styling_products_custom": " 헤어 젤 ",
        })
        self.assertEqual(resolved["styling_tools"], ["드라이기", "매직 롤"])
        self.assertEqual(resolved["styling_products"], ["왁스", "헤어 젤"])
        self.assertEqual(resolved["styling_tools_custom"], "매직 롤")
        self.assertEqual(resolved["styling_products_custom"], "헤어 젤")
        self.assertEqual(build_guided_consultation_sentences(resolved), [
            "평소 손질할 때 드라이기, 매직 롤 등을 사용해요.",
            "헤어 제품은 왁스, 헤어 젤 등을 사용해요.",
        ])

    def test_deselected_other_does_not_resolve_stale_custom_text(self):
        resolved = resolve_guided_answers({
            "styling_tools": ["hair_dryer"],
            "styling_tools_custom": "매직 롤",
            "styling_products": ["wax"],
            "styling_products_custom": "헤어 젤",
        })
        self.assertEqual(resolved, {
            "styling_tools": ["드라이기"], "styling_products": ["왁스"],
        })

    def test_orphan_custom_answers_are_ignored(self):
        self.assertEqual(resolve_guided_answers({
            "styling_tools_custom": "매직 롤", "styling_products_custom": "헤어 젤",
        }), {})

    def test_blank_or_non_text_custom_answer_keeps_option_label(self):
        for value in ["   ", ["unexpected"]]:
            with self.subTest(value=value):
                self.assertEqual(resolve_guided_answers({
                    "styling_products": ["other"], "styling_products_custom": value,
                }), {"styling_products": ["기타"]})

    def test_existing_single_and_text_questions_still_resolve(self):
        resolved = resolve_guided_answers({
            "cut_style_select": "other", "cut_style_custom": "원하는 커트",
        })
        self.assertEqual(resolved, {
            "cut_style_select": "여기에 없어요", "cut_style_custom": "원하는 커트",
        })
        self.assertEqual(build_guided_consultation_sentences(resolved), ["원하는 커트 스타일을 원해요."])


class UndecidedStyleFlowTest(unittest.TestCase):
    def test_undecided_style_has_its_own_growing_hair_and_considerations_path(self):
        nodes = load_consultation_flow()["nodes"]
        option = next(option for option in nodes["cut_style_knowledge"]["options"]
                      if option["value"] == "dont_know")
        concern_node = nodes[option["next"]]
        self.assertEqual(concern_node["id"], "cut_dont_know")
        self.assertEqual(concern_node["type"], "single")
        for concern in concern_node["options"]:
            with self.subTest(concern=concern["value"]):
                self.assertEqual(concern["next"], "cut_avoid_styles")
                avoid_node = nodes[concern["next"]]
                self.assertEqual(avoid_node["type"], "multi")
                self.assertEqual(avoid_node["next"], "cut_growing_hair_undecided")
                growing_node = nodes[avoid_node["next"]]
                self.assertEqual(growing_node["type"], "single")
                for answer in growing_node["options"]:
                    self.assertEqual(answer["next"], "cut_hair_considerations")
                self.assertEqual(nodes["cut_hair_considerations"]["next"], "cut_change_level")
                resolved = resolve_guided_answers({"cut_dont_know": concern["value"]})
                self.assertEqual(build_guided_consultation_sentences(resolved), [
                    "현재 머리에서 특별히 불편한 점은 없어요."
                    if concern["value"] == "dont_know" else f"{concern['label']}.",
                ])

    def test_multiple_avoid_styles_are_included_before_growing_hair_preference(self):
        resolved = resolve_guided_answers({
            "cut_dont_know": "hard_to_style",
            "cut_avoid_styles": ["too_short", "high_maintenance"],
            "cut_growing_hair_undecided": "yes",
        })
        self.assertEqual(build_guided_consultation_sentences(resolved), [
            "손질이 어려워요.",
            "너무 짧은 머리, 손질이 많이 필요한 스타일 같은 스타일은 피하고 싶어요.",
            "현재 머리를 기르고 있어서 전체 길이는 최대한 유지하고 싶어요.",
        ])

    def test_growing_hair_is_reported_for_both_paths(self):
        for node_id in ["cut_growing_hair", "cut_growing_hair_undecided"]:
            with self.subTest(node=node_id):
                self.assertEqual(build_guided_consultation_sentences(resolve_guided_answers({node_id: "yes"})), [
                    "현재 머리를 기르고 있어서 전체 길이는 최대한 유지하고 싶어요.",
                ])
                self.assertEqual(build_guided_consultation_sentences(resolve_guided_answers({node_id: "no"})), [])

    def test_original_growing_hair_still_leads_to_bangs(self):
        nodes = load_consultation_flow()["nodes"]
        for option in nodes["cut_growing_hair"]["options"]:
            self.assertEqual(option["next"], "cut_bangs_style")
        for option in nodes["cut_style_select"]["options"]:
            self.assertIn(option["next"], ["cut_growing_hair", "cut_style_custom"])

    def test_considerations_and_custom_text_are_included_in_consultation(self):
        resolved = resolve_guided_answers({
            "cut_hair_considerations": ["hair_density", "other"],
            "cut_hair_considerations_custom": " 뒤쪽에 가마가 두 개 있어요 ",
        })
        self.assertEqual(build_guided_consultation_sentences(resolved), [
            "머리숱 같은 특징을 고려해서 커트해 주세요.",
            "이 부분도 함께 고려해 주세요: “뒤쪽에 가마가 두 개 있어요”",
        ])

    def test_no_considerations_excludes_conflicting_and_stale_custom_answers(self):
        resolved = resolve_guided_answers({
            "cut_hair_considerations": ["none", "hair_density", "other"],
            "cut_hair_considerations_custom": "이전 입력",
        })
        self.assertEqual(resolved, {"cut_hair_considerations": ["특별히 없어요"]})
        self.assertEqual(build_guided_consultation_sentences(resolved), [
            "머리 특징과 관련해 특별히 고려해 주실 부분은 없어요.",
        ])

    def test_all_change_levels_rejoin_styling_and_are_included_in_consultation(self):
        nodes = load_consultation_flow()["nodes"]
        node = nodes[nodes["cut_hair_considerations"]["next"]]
        self.assertEqual(node["id"], "cut_change_level")
        self.assertEqual(node["type"], "single")
        for option in node["options"]:
            with self.subTest(value=option["value"]):
                self.assertEqual(option["next"], "styling_method")
                resolved = resolve_guided_answers({
                    "cut_change_level": option["value"],
                    "styling_method": "dry_only",
                })
                self.assertEqual(build_guided_consultation_sentences(resolved), [
                    f"{option['label']}.",
                    "평소에는 머리만 말려요.",
                ])

    def test_all_question_paths_reach_complete_without_missing_nodes_or_cycles(self):
        flow = load_consultation_flow()

        def walk(node_id, path):
            if node_id == "complete":
                return
            self.assertIn(node_id, flow["nodes"])
            self.assertNotIn(node_id, path)
            node = flow["nodes"][node_id]
            targets = ([option["next"] for option in node["options"]]
                       if node["type"] == "single" else [node["next"]])
            self.assertTrue(targets)
            for target in targets:
                walk(target, path | {node_id})

        walk(flow["root"], set())


class PermStyleFlowTest(unittest.TestCase):
    def test_cut_and_perm_share_styling_nodes_and_finish_at_products(self):
        nodes = load_consultation_flow()["nodes"]
        self.assertEqual(nodes["perm_avoid_styles"]["next"], "styling_method")
        for option in nodes["cut_change_level"]["options"]:
            self.assertEqual(option["next"], "styling_method")
        self.assertEqual({option["value"]: option["next"] for option in nodes["styling_method"]["options"]}, {
            "dry_only": "complete", "blow_dry_only": "complete",
            "blow_dry_and_product": "styling_products", "active_styling": "styling_tools",
        })
        self.assertEqual(nodes["styling_tools"]["next"], "styling_products")
        self.assertEqual(nodes["styling_products"]["next"], "complete")
        for node_id in ["styling_method", "styling_tools", "styling_products"]:
            self.assertEqual(nodes[node_id]["id"], node_id)
            self.assertNotIn(f"cut_{node_id}", nodes)
        for node_id in ["styling_tools", "styling_products"]:
            other = next(option for option in nodes[node_id]["options"] if option["value"] == "other")
            self.assertEqual(other["custom_input"]["answer_key"], f"{node_id}_custom")

    def test_perm_starts_with_style_knowledge_and_reserves_next_questions(self):
        nodes = load_consultation_flow()["nodes"]
        service_option = next(option for option in nodes["service_type"]["options"]
                              if option["value"] == "perm")
        self.assertEqual(service_option["next"], "perm_style_knowledge")
        node = nodes[service_option["next"]]
        self.assertEqual(node["id"], "perm_style_knowledge")
        self.assertEqual(node["type"], "single")
        self.assertEqual(node["text"], "원하는 펌 스타일이 정해져 있나요?")
        self.assertEqual({option["value"]: option["next"] for option in node["options"]}, {
            "know_name": "perm_style_select",
            "know_feeling": "perm_part_preference",
            "dont_know": "perm_avoid_styles_undecided",
        })
        for option in node["options"]:
            with self.subTest(value=option["value"]):
                self.assertEqual(resolve_guided_answers({node["id"]: option["value"]}), {
                    node["id"]: option["label"],
                })

    def test_perm_style_options_follow_the_requested_branches(self):
        nodes = load_consultation_flow()["nodes"]
        node = nodes["perm_style_select"]
        self.assertEqual(node["id"], "perm_style_select")
        self.assertEqual(node["type"], "single")
        self.assertEqual({option["value"]: option["next"] for option in node["options"]}, {
            "other": "perm_style_custom",
            "hippie_perm": "perm_part_preference",
            "volume_perm": "perm_part_preference",
            "shadow_perm": "perm_curl_intensity",
            "leaf_perm": "perm_curl_intensity",
            "gail_perm": "perm_curl_intensity",
            "aez_perm": "perm_curl_intensity",
            "parted_perm": "perm_curl_intensity",
        })
        for option in node["options"]:
            with self.subTest(value=option["value"]):
                self.assertEqual(resolve_guided_answers({node["id"]: option["value"]}), {
                    node["id"]: option["label"],
                })

    def test_all_part_preferences_rejoin_the_intensity_question(self):
        nodes = load_consultation_flow()["nodes"]
        node = nodes["perm_part_preference"]
        self.assertEqual(node["id"], "perm_part_preference")
        self.assertEqual(node["type"], "single")
        self.assertEqual({option["value"] for option in node["options"]}, {
            "parted", "no_part", "dont_know",
        })
        for option in node["options"]:
            self.assertEqual(option["next"], "perm_curl_intensity")
            self.assertEqual(resolve_guided_answers({node["id"]: option["value"]}), {
                node["id"]: option["label"],
            })
        self.assertIn("perm_curl_intensity", nodes)
        self.assertIn("perm_avoid_styles", nodes)
        self.assertNotIn("perm_style_feeling", nodes)

    def test_custom_perm_style_uses_a_text_node_before_part_preference(self):
        nodes = load_consultation_flow()["nodes"]
        node = nodes["perm_style_custom"]
        self.assertEqual(node["id"], "perm_style_custom")
        self.assertEqual(node["type"], "text")
        self.assertEqual(node["next"], "perm_part_preference")
        self.assertEqual(resolve_guided_answers({
            "perm_style_select": "other", "perm_style_custom": "스핀스왈로펌",
        }), {
            "perm_style_select": "여기에 없어요", "perm_style_custom": "스핀스왈로펌",
        })

    def test_intensity_and_down_perm_rejoin_avoid_styles(self):
        nodes = load_consultation_flow()["nodes"]
        for node_id, values, next_id in [
            ("perm_curl_intensity", {"subtle", "natural", "defined"}, "perm_down_perm"),
            ("perm_down_perm", {"stylist_recommendation", "yes", "no"}, "perm_avoid_styles"),
        ]:
            with self.subTest(node_id=node_id):
                node = nodes[node_id]
                self.assertEqual(node["id"], node_id)
                self.assertEqual(node["type"], "single")
                self.assertEqual({option["value"] for option in node["options"]}, values)
                for option in node["options"]:
                    self.assertEqual(option["next"], next_id)
                    self.assertEqual(resolve_guided_answers({node_id: option["value"]}), {
                        node_id: option["label"],
                    })
        self.assertIn("perm_avoid_styles", nodes)

    def test_avoid_styles_allow_multiple_options_and_custom_text(self):
        node = load_consultation_flow()["nodes"]["perm_avoid_styles"]
        self.assertEqual(node["type"], "multi")
        self.assertEqual(node["next"], "styling_method")
        self.assertEqual({option["value"] for option in node["options"]}, {
            "other", "high_maintenance", "overcurled_bangs", "strong_curls",
            "too_bulky", "sides_stick_out", "long_lasting_strong_perm",
        })
        self.assertEqual(resolve_guided_answers({
            "perm_avoid_styles": ["high_maintenance", "strong_curls", "other"],
            "perm_avoid_styles_custom": " 뿌리가 너무 눌리는 느낌 ",
        }), {
            "perm_avoid_styles": ["뿌리가 너무 눌리는 느낌", "손질이 너무 어려운 스타일", "컬이 너무 강하게 나오는 것"],
            "perm_avoid_styles_custom": "뿌리가 너무 눌리는 느낌",
        })

    def test_completed_perm_answers_are_included_in_customer_wishes(self):
        resolved = resolve_guided_answers({
            "service_type": "perm", "perm_style_select": "other",
            "perm_style_custom": "스핀스왈로펌", "perm_part_preference": "dont_know",
            "perm_curl_intensity": "natural", "perm_down_perm": "no",
            "perm_avoid_styles": ["too_bulky", "other"],
            "perm_avoid_styles_custom": " 앞머리가 눈을 가리는 건 싫어요. ",
            "styling_method": "active_styling",
            "styling_tools": ["other"], "styling_tools_custom": "롤빗",
            "styling_products": ["other"], "styling_products_custom": "헤어 젤",
        })
        self.assertEqual(build_guided_consultation_sentences(resolved), [
            "스핀스왈로펌 스타일을 원해요.",
            "가르마는 어떻게 할지 아직 잘 모르겠어요.",
            "펌은 펌한 느낌이 자연스럽게 보이게 해주세요.",
            "다운펌은 하지 않을게요.",
            "너무 부풀어 보이는 것 등은 피하고 싶어요.",
            "피하고 싶은 내용을 직접 적었어요: “앞머리가 눈을 가리는 건 싫어요.”",
            "평소에는 고데기나 여러 제품을 써서 적극적으로 스타일링해요.",
            "평소 손질할 때 롤빗 등을 사용해요.",
            "헤어 제품은 헤어 젤 등을 사용해요.",
        ])

    def test_undecided_perm_path_finishes_after_shared_styling(self):
        resolved = resolve_guided_answers({
            "perm_style_knowledge": "dont_know", "perm_avoid_styles_undecided": ["other"],
            "perm_avoid_styles_undecided_custom": "너무 뻗치는 머리",
            "perm_reason": "easy_styling", "perm_part_preference_undecided": "either",
            "perm_down_perm_undecided": "stylist_recommendation", "perm_change_level": "subtle",
            "styling_method": "dry_only",
        })
        self.assertEqual(build_guided_consultation_sentences(resolved), [
            "피하고 싶은 내용을 직접 적었어요: “너무 뻗치는 머리”",
            "손질을 더 쉽게 하고 싶어요.",
            "가르마 유무는 상관없어요.",
            "다운펌 여부는 미용사님 추천에 맡길게요.",
            "거의 티 나지 않게 자연스럽게 해주세요.",
            "평소에는 머리만 말려요.",
        ])

    def test_avoid_styles_ignore_deselected_and_orphan_custom_text(self):
        self.assertEqual(resolve_guided_answers({
            "perm_avoid_styles": ["too_bulky"],
            "perm_avoid_styles_custom": "이전 입력",
        }), {"perm_avoid_styles": ["너무 부풀어 보이는 것"]})
        self.assertEqual(resolve_guided_answers({"perm_avoid_styles_custom": "이전 입력"}), {})


class UndecidedPermFlowTest(unittest.TestCase):
    def test_question_order_and_option_values_match_the_undecided_path(self):
        nodes = load_consultation_flow()["nodes"]
        stages = [
            ("perm_avoid_styles_undecided", "multi", ["strong_curls", "too_bulky", "overcurled_bangs", "overstyled", "high_maintenance", "none", "other"], "perm_reason"),
            ("perm_reason", "single", ["natural_movement", "add_volume", "shape_bangs", "easy_styling", "change_mood", "stylist_recommendation"], "perm_part_preference_undecided"),
            ("perm_part_preference_undecided", "single", ["yes", "no", "either"], "perm_down_perm_undecided"),
            ("perm_down_perm_undecided", "single", ["yes", "no", "stylist_recommendation"], "perm_change_level"),
            ("perm_change_level", "single", ["subtle", "small_change", "defined", "big_change"], "styling_method"),
        ]
        for node_id, node_type, values, next_id in stages:
            with self.subTest(node=node_id):
                node = nodes[node_id]
                self.assertEqual(node["id"], node_id)
                self.assertEqual(node["type"], node_type)
                self.assertEqual([option["value"] for option in node["options"]], values)
                if node_type == "multi":
                    self.assertEqual(node["next"], next_id)
                else:
                    for option in node["options"]:
                        self.assertEqual(option["next"], next_id)

    def test_selected_avoid_styles_and_custom_text_are_delivered_together(self):
        resolved = resolve_guided_answers({
            "perm_avoid_styles_undecided": ["strong_curls", "overstyled", "other"],
            "perm_avoid_styles_undecided_custom": " 앞머리가 눈을 가리는 건 싫어요. ",
        })
        self.assertEqual(build_guided_consultation_sentences(resolved), [
            "컬이 너무 강한 것, 너무 꾸민 느낌 등은 피하고 싶어요.",
            "피하고 싶은 내용을 직접 적었어요: “앞머리가 눈을 가리는 건 싫어요.”",
        ])
        self.assertEqual(resolved["perm_avoid_styles_undecided_custom"], "앞머리가 눈을 가리는 건 싫어요.")

    def test_none_excludes_other_selections_and_remains_visible(self):
        resolved = resolve_guided_answers({
            "perm_avoid_styles_undecided": ["strong_curls", "none", "other"],
            "perm_avoid_styles_undecided_custom": "이전 입력",
        })
        self.assertEqual(resolved, {"perm_avoid_styles_undecided": ["특별히 없음"]})
        self.assertEqual(build_guided_consultation_sentences(resolved), ["특별히 피하고 싶은 펌 느낌은 없어요."])

    def test_unselected_custom_text_is_ignored(self):
        for selection in [[], ["strong_curls"]]:
            resolved = resolve_guided_answers({
                "perm_avoid_styles_undecided": selection,
                "perm_avoid_styles_undecided_custom": "이전 입력",
            })
            self.assertNotIn("perm_avoid_styles_undecided_custom", resolved)
        self.assertEqual(resolve_guided_answers({"perm_avoid_styles_undecided_custom": "이전 입력"}), {})

    def test_every_single_option_produces_a_contextual_sentence(self):
        nodes = load_consultation_flow()["nodes"]
        expected = {
            "perm_reason": [f"{option['label']}." for option in nodes["perm_reason"]["options"]],
            "perm_part_preference_undecided": ["가르마가 있는 스타일도 좋아요.", "가르마가 없는 스타일이 좋아요.", "가르마 유무는 상관없어요."],
            "perm_down_perm_undecided": ["다운펌도 함께 하고 싶어요.", "다운펌은 하지 않을게요.", "다운펌 여부는 미용사님 추천에 맡길게요."],
            "perm_change_level": ["거의 티 나지 않게 자연스럽게 해주세요.", "조금은 새로운 느낌이 나게 해주세요.", "펌한 느낌이 확실히 나게 해주세요.", "크게 바뀌어도 괜찮아요."],
        }
        for node_id, sentences in expected.items():
            for option, sentence in zip(nodes[node_id]["options"], sentences):
                with self.subTest(node=node_id, value=option["value"]):
                    self.assertEqual(build_guided_consultation_sentences(resolve_guided_answers({
                        node_id: option["value"],
                    })), [sentence])


class ConsultationWordingTest(unittest.TestCase):
    def test_bangs_weight_and_length_are_separate_natural_sentences(self):
        resolved = resolve_guided_answers({
            "cut_bangs_style": "down",
            "cut_bangs_down_style": "light",
            "cut_bangs_length": "dont_know",
        })
        self.assertEqual(build_guided_consultation_sentences(resolved), [
            "앞머리는 내림머리 스타일로 하고 싶어요.",
            "앞머리 무게감은 숱을 많이 쳐서 가볍게 해주세요.",
            "앞머리 길이는 아직 잘 모르겠어요.",
        ])

    def test_keep_current_bangs_length_is_not_described_as_a_measurement(self):
        resolved = resolve_guided_answers({
            "cut_bangs_style": "parted", "cut_bangs_part_style": "gail_style",
            "cut_bangs_length": "keep_current_length",
        })
        self.assertEqual(build_guided_consultation_sentences(resolved), [
            "앞머리는 가르마 스타일로 하고 싶어요.",
            "앞머리는 가일 스타일로 연출하고 싶어요.",
            "앞머리는 현재 길이를 최대한 유지해 주세요.",
        ])

    def test_side_back_and_down_perm_include_context(self):
        resolved = resolve_guided_answers({
            "cut_side_section_style": "two_block", "cut_two_block_length": "9mm",
            "cut_down_perm": "stylist_recommendation",
            "cut_back_short_style": "match_side_length",
        })
        self.assertEqual(build_guided_consultation_sentences(resolved), [
            "옆머리는 투블럭 (~15mm) 스타일로, 길이는 9mm로 정리해 주세요.",
            "다운펌이 필요할지는 미용사님과 상의하고 싶어요.",
            "뒷머리는 옆머리와 길이를 맞춘 스타일로 해주세요.",
        ])

    def test_custom_only_consideration_is_preserved_without_noun_suffix(self):
        resolved = resolve_guided_answers({
            "cut_hair_considerations": ["other"],
            "cut_hair_considerations_custom": " 정수리 쪽이 잘 떠요. ",
        })
        self.assertEqual(build_guided_consultation_sentences(resolved), [
            "이 부분도 함께 고려해 주세요: “정수리 쪽이 잘 떠요.”",
        ])

    def test_sentence_endings_are_not_duplicated(self):
        self.assertEqual(build_guided_consultation_sentences({
            "cut_dont_know": "손질이 어려워요.",
            "cut_change_level": "새로운 스타일도 괜찮아요!",
            "styling_method": "머리만 말려요.",
        }), ["손질이 어려워요.", "새로운 스타일도 괜찮아요!", "평소에는 머리만 말려요."])


if __name__ == "__main__":
    unittest.main()
