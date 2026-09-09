import unittest

from backend.app.services.consultation_flow_service import (
    build_guided_consultation_sentences,
    resolve_guided_answers,
)


class CustomInputAnswersTest(unittest.TestCase):
    def test_tools_and_products_are_resolved_and_included_in_sentences(self):
        resolved = resolve_guided_answers({
            "cut_styling_tools": ["hair_dryer", "other"],
            "cut_styling_tools_custom": " 매직 롤 ",
            "cut_styling_products": ["wax", "other"],
            "cut_styling_products_custom": " 헤어 젤 ",
        })
        self.assertEqual(resolved["cut_styling_tools"], ["드라이기", "매직 롤"])
        self.assertEqual(resolved["cut_styling_products"], ["왁스", "헤어 젤"])
        self.assertEqual(resolved["cut_styling_tools_custom"], "매직 롤")
        self.assertEqual(resolved["cut_styling_products_custom"], "헤어 젤")
        self.assertEqual(build_guided_consultation_sentences(resolved), [
            "주로 사용하는 도구는 드라이기, 매직 롤예요.",
            "주로 사용하는 제품은 왁스, 헤어 젤예요.",
        ])

    def test_deselected_other_does_not_resolve_stale_custom_text(self):
        resolved = resolve_guided_answers({
            "cut_styling_tools": ["hair_dryer"],
            "cut_styling_tools_custom": "매직 롤",
            "cut_styling_products": ["wax"],
            "cut_styling_products_custom": "헤어 젤",
        })
        self.assertEqual(resolved, {
            "cut_styling_tools": ["드라이기"], "cut_styling_products": ["왁스"],
        })

    def test_orphan_custom_answers_are_ignored(self):
        self.assertEqual(resolve_guided_answers({
            "cut_styling_tools_custom": "매직 롤", "cut_styling_products_custom": "헤어 젤",
        }), {})

    def test_blank_or_non_text_custom_answer_keeps_option_label(self):
        for value in ["   ", ["unexpected"]]:
            with self.subTest(value=value):
                self.assertEqual(resolve_guided_answers({
                    "cut_styling_products": ["other"], "cut_styling_products_custom": value,
                }), {"cut_styling_products": ["기타"]})

    def test_existing_single_and_text_questions_still_resolve(self):
        resolved = resolve_guided_answers({
            "cut_style_select": "other", "cut_style_custom": "원하는 커트",
        })
        self.assertEqual(resolved, {
            "cut_style_select": "여기에 없어요", "cut_style_custom": "원하는 커트",
        })
        self.assertEqual(build_guided_consultation_sentences(resolved), ["원하는 커트 스타일을 원해요."])


if __name__ == "__main__":
    unittest.main()
