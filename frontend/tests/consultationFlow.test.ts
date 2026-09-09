import assert from "node:assert/strict"
import { readFileSync } from "node:fs"
import test from "node:test"
import {
  canSubmitMulti,
  clearNodeAnswers,
  collectMultiAnswers,
  getSelectedCustomInputs,
} from "../src/utils/consultationFlow.ts"
import type { FlowDefinition, QuestionNode } from "../src/utils/consultationFlow.ts"

const flow: FlowDefinition = JSON.parse(readFileSync(
  new URL("../../backend/app/data/consultation_flow.json", import.meta.url), "utf8",
))
const tools = flow.nodes.cut_styling_tools
const products = flow.nodes.cut_styling_products

test("required custom input is validated only when its option is selected", () => {
  assert.equal(canSubmitMulti(tools, [], {}), false)
  assert.equal(canSubmitMulti(tools, ["hair_dryer"], {}), true)
  assert.equal(canSubmitMulti(tools, ["hair_dryer", "other"], {}), false)
  assert.equal(canSubmitMulti(tools, ["other"], { cut_styling_tools_custom: " \t " }), false)
  assert.equal(canSubmitMulti(tools, ["other"], { cut_styling_tools_custom: "매직 롤" }), true)
  assert.equal(canSubmitMulti(products, ["other"], { cut_styling_tools_custom: "매직 롤" }), false)
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
  const drafts = { cut_styling_tools_custom: " 매직 롤 ", cut_styling_products_custom: " 헤어 젤 " }
  assert.deepEqual({
    ...collectMultiAnswers(tools, ["hair_dryer", "other"], drafts),
    ...collectMultiAnswers(products, ["wax", "other"], drafts),
  }, {
    cut_styling_tools: ["hair_dryer", "other"], cut_styling_tools_custom: "매직 롤",
    cut_styling_products: ["wax", "other"], cut_styling_products_custom: "헤어 젤",
  })
})

test("deselecting other removes its committed answer without submitting a retained draft", () => {
  const drafts = { cut_styling_tools_custom: "매직 롤" }
  const saved = {
    service_type: "cut",
    ...collectMultiAnswers(tools, ["hair_dryer", "other"], drafts),
  }
  const remaining = clearNodeAnswers(saved, flow.nodes, [tools.id])
  assert.deepEqual(remaining, { service_type: "cut" })
  assert.deepEqual({ ...remaining, ...collectMultiAnswers(tools, ["hair_dryer"], drafts) }, {
    service_type: "cut", cut_styling_tools: ["hair_dryer"],
  })
  assert.equal(saved.cut_styling_tools_custom, "매직 롤")
  assert.equal(collectMultiAnswers(tools, ["other"], drafts).cut_styling_tools_custom, "매직 롤")
})

test("changing an earlier path removes descendant answers and all owned custom keys", () => {
  const saved = {
    service_type: "cut", cut_styling_method: "active_styling",
    cut_styling_tools: ["hair_dryer"], cut_styling_tools_custom: "stale tool",
    cut_styling_products: ["other"], cut_styling_products_custom: "헤어 젤",
  }
  assert.deepEqual(clearNodeAnswers(saved, flow.nodes, ["cut_styling_method", tools.id, products.id]), {
    service_type: "cut",
  })
  assert.deepEqual(clearNodeAnswers({
    cut_style_custom: "리프컷", cut_styling_tools_custom: "매직 롤", cut_styling_products_custom: "헤어 젤",
  }, flow.nodes, [tools.id, products.id]), { cut_style_custom: "리프컷" })
  assert.deepEqual(clearNodeAnswers({ [tools.id]: ["other"], [products.id]: ["other"] },
    flow.nodes, [tools.id, products.id]), {})
})

test("editing a later question preserves committed custom answers of earlier questions", () => {
  const saved = {
    ...collectMultiAnswers(tools, ["other"], { cut_styling_tools_custom: "매직 롤" }),
    ...collectMultiAnswers(products, ["other"], { cut_styling_products_custom: "헤어 젤" }),
  }
  assert.deepEqual(clearNodeAnswers(saved, flow.nodes, [products.id]), {
    cut_styling_tools: ["other"], cut_styling_tools_custom: "매직 롤",
  })
})

test("existing standalone text answers are still cleaned up by node id", () => {
  assert.deepEqual(clearNodeAnswers({ service_type: "cut", cut_style_custom: "리프컷" },
    flow.nodes, ["cut_style_custom"]), { service_type: "cut" })
})
