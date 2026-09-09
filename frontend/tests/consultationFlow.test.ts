import assert from "node:assert/strict"
import { readFileSync } from "node:fs"
import test from "node:test"
import {
  canSubmitMulti,
  clearNodeAnswers,
  collectMultiAnswers,
  getSelectedCustomInputs,
  toggleMultiSelection,
} from "../src/utils/consultationFlow.ts"
import type { FlowDefinition, QuestionNode } from "../src/utils/consultationFlow.ts"

const flow: FlowDefinition = JSON.parse(readFileSync(
  new URL("../../backend/app/data/consultation_flow.json", import.meta.url), "utf8",
))
const tools = flow.nodes.styling_tools
const products = flow.nodes.styling_products

test("required custom input is validated only when its option is selected", () => {
  assert.equal(canSubmitMulti(tools, [], {}), false)
  assert.equal(canSubmitMulti(tools, ["hair_dryer"], {}), true)
  assert.equal(canSubmitMulti(tools, ["hair_dryer", "other"], {}), false)
  assert.equal(canSubmitMulti(tools, ["other"], { styling_tools_custom: " \t " }), false)
  assert.equal(canSubmitMulti(tools, ["other"], { styling_tools_custom: "매직 롤" }), true)
  assert.equal(canSubmitMulti(products, ["other"], { styling_tools_custom: "매직 롤" }), false)
})

test("custom inputs are configured by option metadata, including optional inputs", () => {
  const optionalNode: QuestionNode = {
    id: "optional", type: "multi",
    options: [{ value: "custom", label: "직접 입력", custom_input: {
      answer_key: "optional_note", label: "설명", required: false,
    } }],
  }
  assert.deepEqual(getSelectedCustomInputs(optionalNode, []), [])
  assert.equal(canSubmitMulti(optionalNode, ["custom"], {}), true)
  assert.deepEqual(collectMultiAnswers(optionalNode, ["custom"], {}), { optional: ["custom"] })
})

test("tool and product input values are trimmed and saved separately", () => {
  const drafts = { styling_tools_custom: " 매직 롤 ", styling_products_custom: " 헤어 젤 " }
  assert.deepEqual({
    ...collectMultiAnswers(tools, ["hair_dryer", "other"], drafts),
    ...collectMultiAnswers(products, ["wax", "other"], drafts),
  }, {
    styling_tools: ["hair_dryer", "other"], styling_tools_custom: "매직 롤",
    styling_products: ["wax", "other"], styling_products_custom: "헤어 젤",
  })
})

test("deselecting other removes its committed answer without submitting a retained draft", () => {
  const drafts = { styling_tools_custom: "매직 롤" }
  const saved = {
    service_type: "cut",
    ...collectMultiAnswers(tools, ["hair_dryer", "other"], drafts),
  }
  const remaining = clearNodeAnswers(saved, flow.nodes, [tools.id])
  assert.deepEqual(remaining, { service_type: "cut" })
  assert.deepEqual({ ...remaining, ...collectMultiAnswers(tools, ["hair_dryer"], drafts) }, {
    service_type: "cut", styling_tools: ["hair_dryer"],
  })
  assert.equal(saved.styling_tools_custom, "매직 롤")
  assert.equal(collectMultiAnswers(tools, ["other"], drafts).styling_tools_custom, "매직 롤")
})

test("changing an earlier path removes descendant answers and all owned custom keys", () => {
  const saved = {
    service_type: "cut", styling_method: "active_styling",
    styling_tools: ["hair_dryer"], styling_tools_custom: "stale tool",
    styling_products: ["other"], styling_products_custom: "헤어 젤",
  }
  assert.deepEqual(clearNodeAnswers(saved, flow.nodes, ["styling_method", tools.id, products.id]), {
    service_type: "cut",
  })
  assert.deepEqual(clearNodeAnswers({
    cut_style_custom: "리프컷", styling_tools_custom: "매직 롤", styling_products_custom: "헤어 젤",
  }, flow.nodes, [tools.id, products.id]), { cut_style_custom: "리프컷" })
  assert.deepEqual(clearNodeAnswers({ [tools.id]: ["other"], [products.id]: ["other"] },
    flow.nodes, [tools.id, products.id]), {})
})

test("editing a later question preserves committed custom answers of earlier questions", () => {
  const saved = {
    ...collectMultiAnswers(tools, ["other"], { styling_tools_custom: "매직 롤" }),
    ...collectMultiAnswers(products, ["other"], { styling_products_custom: "헤어 젤" }),
  }
  assert.deepEqual(clearNodeAnswers(saved, flow.nodes, [products.id]), {
    styling_tools: ["other"], styling_tools_custom: "매직 롤",
  })
})

test("existing standalone text answers are still cleaned up by node id", () => {
  assert.deepEqual(clearNodeAnswers({ service_type: "cut", cut_style_custom: "리프컷" },
    flow.nodes, ["cut_style_custom"]), { service_type: "cut" })
})

test("none is exclusive, and selecting a normal consideration clears none", () => {
  const node = flow.nodes.cut_hair_considerations
  assert.deepEqual(toggleMultiSelection(node, ["hair_density", "other"], "none"), ["none"])
  assert.deepEqual(toggleMultiSelection(node, ["none"], "hair_density"), ["hair_density"])
  assert.deepEqual(toggleMultiSelection(node, ["none"], "other"), ["other"])
  assert.deepEqual(toggleMultiSelection(node, ["none"], "none"), [])
  assert.deepEqual(toggleMultiSelection(node, ["hair_density"], "hair_texture"), ["hair_density", "hair_texture"])
})

test("consideration custom input is required only when selected and cleaned on path changes", () => {
  const node = flow.nodes.cut_hair_considerations
  const drafts = { cut_hair_considerations_custom: "뒤쪽에 가마가 두 개 있어요" }
  assert.equal(canSubmitMulti(node, ["none"], {}), true)
  assert.equal(canSubmitMulti(node, ["other"], {}), false)
  assert.equal(canSubmitMulti(node, ["other"], drafts), true)
  const committed = collectMultiAnswers(node, ["other"], drafts)
  const remaining = clearNodeAnswers(committed, flow.nodes, [node.id])
  assert.deepEqual({ ...remaining, ...collectMultiAnswers(node, ["none"], drafts) }, {
    cut_hair_considerations: ["none"],
  })
  assert.deepEqual(clearNodeAnswers({
    cut_style_knowledge: "dont_know", cut_growing_hair_undecided: "yes", ...committed,
  }, flow.nodes, ["cut_growing_hair_undecided", node.id]), { cut_style_knowledge: "dont_know" })
})

test("changing a perm style clears its custom text and later answers and drafts", () => {
  assert.equal(flow.nodes.perm_style_custom.type, "text")
  assert.equal(flow.nodes.perm_style_custom.next, "perm_part_preference")
  const removedNodes = [
    "perm_style_select", "perm_style_custom", "perm_part_preference",
    "perm_curl_intensity", "perm_down_perm",
  ]
  assert.deepEqual(clearNodeAnswers({
    service_type: "perm", perm_style_knowledge: "know_name",
    perm_style_select: "other", perm_style_custom: "스핀스왈로펌",
    perm_part_preference: "parted", perm_curl_intensity: "defined", perm_down_perm: "yes",
  }, flow.nodes, removedNodes), { service_type: "perm", perm_style_knowledge: "know_name" })
  assert.deepEqual(clearNodeAnswers({
    perm_style_custom: "스핀스왈로펌",
  }, flow.nodes, removedNodes), {})
})

test("perm avoid styles support multi-select and conditional required custom input", () => {
  const node = flow.nodes.perm_avoid_styles
  const drafts = { perm_avoid_styles_custom: " 뿌리가 너무 눌리는 느낌 " }
  assert.equal(canSubmitMulti(node, [], {}), false)
  assert.equal(canSubmitMulti(node, ["strong_curls"], {}), true)
  assert.equal(canSubmitMulti(node, ["strong_curls", "other"], {}), false)
  assert.equal(canSubmitMulti(node, ["other"], { perm_avoid_styles_custom: "  " }), false)
  assert.equal(canSubmitMulti(node, ["strong_curls", "other"], drafts), true)
  assert.deepEqual(toggleMultiSelection(node, ["strong_curls"], "other"), ["strong_curls", "other"])
  const committed = collectMultiAnswers(node, ["strong_curls", "other"], drafts)
  assert.deepEqual(committed, {
    perm_avoid_styles: ["strong_curls", "other"],
    perm_avoid_styles_custom: "뿌리가 너무 눌리는 느낌",
  })
  const remaining = clearNodeAnswers(committed, flow.nodes, [node.id])
  const deselected = toggleMultiSelection(node, ["strong_curls", "other"], "other")
  assert.deepEqual({ ...remaining, ...collectMultiAnswers(node, deselected, drafts) }, {
    perm_avoid_styles: ["strong_curls"],
  })
  assert.deepEqual(clearNodeAnswers({ service_type: "perm", ...committed }, flow.nodes, [node.id]), {
    service_type: "perm",
  })
  assert.deepEqual(clearNodeAnswers(drafts, flow.nodes, [node.id]), {})
})

test("undecided perm avoid styles validate custom input and keep none exclusive", () => {
  const node = flow.nodes.perm_avoid_styles_undecided
  const drafts = { perm_avoid_styles_undecided_custom: " 눈을 가리는 앞머리 " }
  assert.equal(canSubmitMulti(node, [], {}), false)
  assert.equal(canSubmitMulti(node, ["none"], {}), true)
  assert.equal(canSubmitMulti(node, ["strong_curls", "overstyled"], {}), true)
  assert.equal(canSubmitMulti(node, ["strong_curls", "other"], {}), false)
  assert.equal(canSubmitMulti(node, ["other"], { perm_avoid_styles_undecided_custom: "  " }), false)
  assert.equal(canSubmitMulti(node, ["strong_curls", "other"], drafts), true)
  assert.deepEqual(toggleMultiSelection(node, ["strong_curls", "other"], "none"), ["none"])
  assert.deepEqual(toggleMultiSelection(node, ["none"], "other"), ["other"])
  assert.deepEqual(toggleMultiSelection(node, ["none"], "strong_curls"), ["strong_curls"])
  const committed = collectMultiAnswers(node, ["strong_curls", "other"], drafts)
  assert.deepEqual(committed, {
    perm_avoid_styles_undecided: ["strong_curls", "other"],
    perm_avoid_styles_undecided_custom: "눈을 가리는 앞머리",
  })
  const remaining = clearNodeAnswers(committed, flow.nodes, [node.id])
  for (const selection of [["none"], ["strong_curls"]]) {
    assert.deepEqual({ ...remaining, ...collectMultiAnswers(node, selection, drafts) }, {
      perm_avoid_styles_undecided: selection,
    })
  }
})

test("leaving undecided perm path clears every descendant answer and custom draft", () => {
  const node = flow.nodes.perm_avoid_styles_undecided
  const removedNodes = [
    "perm_style_knowledge", node.id, "perm_reason", "perm_part_preference_undecided",
    "perm_down_perm_undecided", "perm_change_level", "styling_method", tools.id, products.id,
  ]
  const drafts = {
    perm_avoid_styles_undecided_custom: "너무 강한 컬", styling_tools_custom: "롤빗",
    styling_products_custom: "헤어 젤",
  }
  assert.deepEqual(clearNodeAnswers({
    service_type: "perm", perm_style_knowledge: "dont_know",
    ...collectMultiAnswers(node, ["other"], drafts), perm_reason: "easy_styling",
    perm_part_preference_undecided: "either", perm_down_perm_undecided: "no",
    perm_change_level: "subtle", styling_method: "active_styling",
    ...collectMultiAnswers(tools, ["other"], drafts),
    ...collectMultiAnswers(products, ["other"], drafts),
  }, flow.nodes, removedNodes), { service_type: "perm" })
  assert.deepEqual(clearNodeAnswers(drafts, flow.nodes, removedNodes), {})
})

test("cut avoid styles validate and clean custom text without changing the path", () => {
  const node = flow.nodes.cut_avoid_styles
  const drafts = { cut_avoid_styles_custom: " 눈을 가리는 앞머리 " }
  assert.equal(node.next, "cut_growing_hair_undecided")
  assert.equal(canSubmitMulti(node, ["too_short"], {}), true)
  assert.equal(canSubmitMulti(node, ["too_short", "other"], {}), false)
  assert.equal(canSubmitMulti(node, ["other"], { cut_avoid_styles_custom: "  " }), false)
  assert.equal(canSubmitMulti(node, ["other"], drafts), true)
  const selected = toggleMultiSelection(node, ["too_short"], "other")
  assert.deepEqual(selected, ["too_short", "other"])
  const committed = collectMultiAnswers(node, selected, drafts)
  assert.deepEqual(committed, {
    cut_avoid_styles: ["too_short", "other"], cut_avoid_styles_custom: "눈을 가리는 앞머리",
  })
  const remaining = clearNodeAnswers(committed, flow.nodes, [node.id])
  assert.deepEqual({
    ...remaining,
    ...collectMultiAnswers(node, toggleMultiSelection(node, selected, "other"), drafts),
  }, { cut_avoid_styles: ["too_short"] })
  assert.deepEqual(clearNodeAnswers({ service_type: "cut", ...committed }, flow.nodes, [node.id]), {
    service_type: "cut",
  })
  assert.deepEqual(clearNodeAnswers(drafts, flow.nodes, [node.id]), {})
})

test("existing tool selections still allow ordinary multi-selection", () => {
  assert.deepEqual(toggleMultiSelection(tools, ["hair_dryer"], "other"), ["hair_dryer", "other"])
  assert.deepEqual(toggleMultiSelection(tools, ["hair_dryer", "other"], "other"), ["hair_dryer"])
})

test("changing the perm path clears shared styling answers and custom drafts", () => {
  const removedNodes = ["perm_avoid_styles", "styling_method", tools.id, products.id]
  const drafts = { styling_tools_custom: "롤빗", styling_products_custom: "헤어 젤" }
  assert.deepEqual(clearNodeAnswers({
    service_type: "perm", perm_avoid_styles: ["strong_curls"],
    styling_method: "active_styling",
    ...collectMultiAnswers(tools, ["other"], drafts),
    ...collectMultiAnswers(products, ["other"], drafts),
  }, flow.nodes, removedNodes), { service_type: "perm" })
  assert.deepEqual(clearNodeAnswers(drafts, flow.nodes, removedNodes), {})
})
