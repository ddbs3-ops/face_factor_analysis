export type CustomInput = {
  answer_key: string
  label: string
  placeholder?: string
  required?: boolean
}

export type QuestionOption = {
  value: string
  label: string
  next?: string
  custom_input?: CustomInput
}

export type QuestionNode = {
  id: string
  type: "single" | "multi" | "text" | "complete"
  text?: string
  options?: QuestionOption[]
  next?: string
}

export type FlowDefinition = {
  version: string
  root: string
  nodes: Record<string, QuestionNode>
}

export type AnswerValue = string | string[]

// Direct-input answer keys belong to their question, even though they aren't nodes.
export function clearNodeAnswers<T>(
  values: Record<string, T>,
  nodes: FlowDefinition["nodes"],
  nodeIds: string[],
): Record<string, T> {
  const remaining = { ...values }
  for (const nodeId of nodeIds) {
    delete remaining[nodeId]
    for (const option of nodes[nodeId]?.options ?? []) {
      if (option.custom_input) {
        delete remaining[option.custom_input.answer_key]
      }
    }
  }
  return remaining
}

export function getSelectedCustomInputs(node: QuestionNode, selected: string[]): CustomInput[] {
  return (node.options ?? []).flatMap((option) =>
    selected.includes(option.value) && option.custom_input ? [option.custom_input] : [],
  )
}

export function canSubmitMulti(
  node: QuestionNode,
  selected: string[],
  drafts: Record<string, string>,
): boolean {
  return selected.length > 0 && getSelectedCustomInputs(node, selected).every(
    (input) => !input.required || Boolean(drafts[input.answer_key]?.trim()),
  )
}

export function collectMultiAnswers(
  node: QuestionNode,
  selected: string[],
  drafts: Record<string, string>,
): Record<string, AnswerValue> {
  const collected: Record<string, AnswerValue> = { [node.id]: selected }
  for (const input of getSelectedCustomInputs(node, selected)) {
    const value = drafts[input.answer_key]?.trim()
    if (value) collected[input.answer_key] = value
  }
  return collected
}
