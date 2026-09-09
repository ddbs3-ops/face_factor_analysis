import { useEffect, useRef, useState } from "react"
import {
  canSubmitMulti,
  clearNodeAnswers,
  collectMultiAnswers,
  getSelectedCustomInputs,
} from "../utils/consultationFlow"
import type { AnswerValue, FlowDefinition } from "../utils/consultationFlow"

type ConsultationFlowProps = {
  onComplete: (answers: Record<string, AnswerValue>) => void
}

function ConsultationFlow({ onComplete }: ConsultationFlowProps) {
  const [flow, setFlow] = useState<FlowDefinition | null>(null)

  const [history, setHistory] = useState<string[]>([])

  const [answers, setAnswers] = useState<Record<string, AnswerValue>>({})

  const [textInputs, setTextInputs] = useState<Record<string, string>>({})
  const [multiInputs, setMultiInputs] = useState<Record<string, string[]>>({})
  const latestQuestionRef = useRef<HTMLDivElement>(null)
  const latestQuestionId = history[history.length - 1]

  const API_BASE_URL = import.meta.env.VITE_API_URL
  const FLOW_API_URL = `${API_BASE_URL}/consultation/flow`


  useEffect(() => {
    fetch(FLOW_API_URL)
      .then((response) => {
        if (!response.ok) {
          throw new Error("상담 질문을 불러오지 못했습니다.")
        }

        return response.json()
      })
      .then((data: FlowDefinition) => {
        setFlow(data)
        setHistory([data.root])
      })
      .catch((error) => {
        console.error(error)
      })
  }, [FLOW_API_URL])

  useEffect(() => {
    if (history.length > 1) {
      latestQuestionRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      })
    }
  }, [history.length, latestQuestionId])

  function prepareQuestion(nodeId: string) {
    if (!flow) return

    const nodeIndex = history.indexOf(nodeId)

    if (nodeIndex === -1) return

    const newHistory = history.slice(0, nodeIndex + 1)
    const removedNodeIds = history.slice(nodeIndex + 1)
    const newAnswers = clearNodeAnswers(answers, flow.nodes, [nodeId, ...removedNodeIds])

    // Keep the current question's drafts for reselection; discard abandoned paths.
    setTextInputs((prev) => clearNodeAnswers(prev, flow.nodes, removedNodeIds))
    setMultiInputs((prev) => clearNodeAnswers(prev, flow.nodes, removedNodeIds))
    setAnswers(newAnswers)
    setHistory(newHistory)
    return { newHistory, newAnswers }
  }

  function submitAnswer(
    nodeId: string,
    submittedAnswers: Record<string, AnswerValue>,
    nextId?: string,
  ) {
    const prepared = prepareQuestion(nodeId)
    if (!prepared) return
    const newAnswers = { ...prepared.newAnswers, ...submittedAnswers }
    const newHistory = [...prepared.newHistory]

    // complete가 아니면 다음 질문 추가
    if (nextId === "complete") {
      setAnswers(newAnswers)
      setHistory(newHistory)
      onComplete(newAnswers)
      return
    }

    if (nextId) {
      newHistory.push(nextId)
    }

    setAnswers(newAnswers)
    setHistory(newHistory)
  }

  function handleSingleAnswer(nodeId: string, value: string, nextId?: string) {
    submitAnswer(nodeId, { [nodeId]: value }, nextId)
  }

  function handleTextAnswer(nodeId: string, nextId?: string) {
    const value = textInputs[nodeId]?.trim()
    if (!value) return
    submitAnswer(nodeId, { [nodeId]: value }, nextId)
  }

  function toggleMultiAnswer(nodeId: string, value: string) {
    if (!prepareQuestion(nodeId)) return
    setMultiInputs((prev) => {
      const currentValues = prev[nodeId] ?? []

      const exists = currentValues.includes(value)

      const nextValues = exists
        ? currentValues.filter((item) => item !== value)
        : [...currentValues, value]

      return {
        ...prev,
        [nodeId]: nextValues,
      }
    })
  }

  function handleMultiAnswer(nodeId: string, nextId?: string) {
    const node = flow?.nodes[nodeId]
    if (!node) return
    const values = multiInputs[nodeId] ?? []
    if (!canSubmitMulti(node, values, textInputs)) return
    submitAnswer(nodeId, collectMultiAnswers(node, values, textInputs), nextId)
  }

  function handleCustomInput(nodeId: string, answerKey: string, value: string) {
    if (!prepareQuestion(nodeId)) return
    setTextInputs((prev) => ({ ...prev, [answerKey]: value }))
  }

  if (!flow) {
    return <div className="consultation-flow-loading">상담 질문을 불러오는 중...</div>
  }

  return (
    <div className="consultation-flow">
      {history.map((nodeId, index) => {
        const node = flow.nodes[nodeId]

        if (!node) {
          return null
        }

        return (
          <div
            className="consultation-question-card"
            key={node.id}
            ref={index === history.length - 1 ? latestQuestionRef : undefined}
          >
            {node.text && <h2>{node.text}</h2>}

            {node.type === "single" && (
              <div className="consultation-option-list">
                {node.options?.map((option) => {
                  const isSelected =
                    answers[node.id] === option.value

                  return (
                    <button
                      className={`consultation-option-button${isSelected ? " is-selected" : ""}`}
                      key={option.value}
                      type="button"
                      onClick={() =>
                        handleSingleAnswer(
                          node.id,
                          option.value,
                          option.next,
                        )
                      }
                    >
                      {option.label}
                      {isSelected ? " ✓" : ""}
                    </button>
                  )
                })}
              </div>
            )}

            {node.type === "text" && (
              <div className="consultation-text-answer">
                <input
                  className="consultation-answer-input"
                  type="text"
                  value={textInputs[node.id] ?? ""}
                  onChange={(event) =>
                    setTextInputs((prev) => ({
                      ...prev,
                      [node.id]: event.target.value,
                    }))
                  }
                />

                <button
                  className="consultation-next-button"
                  type="button"
                  onClick={() => handleTextAnswer(node.id, node.next)}
                >
                  다음
                </button>
              </div>
            )}

            {node.type === "multi" && (
              <div className="consultation-multi-answer">
                <div className="consultation-option-list">
                  {node.options?.map((option) => {
                    const selectedValues =
                      multiInputs[node.id] ?? []

                    const isSelected =
                      selectedValues.includes(option.value)

                    return (
                      <button
                        className={`consultation-option-button${isSelected ? " is-selected" : ""}`}
                        key={option.value}
                        type="button"
                        onClick={() =>
                          toggleMultiAnswer(
                            node.id,
                            option.value,
                          )
                        }
                      >
                        {option.label}
                        {isSelected ? " ✓" : ""}
                      </button>
                    )
                  })}
                </div>

                {getSelectedCustomInputs(node, multiInputs[node.id] ?? []).map((input) => {
                  const inputId = `custom-input-${node.id}-${input.answer_key}`
                  return (
                    <div className="consultation-custom-input" key={input.answer_key}>
                      <label htmlFor={inputId}>
                        {input.label}
                        {input.required && <span className="consultation-input-required"> (필수)</span>}
                      </label>
                      <input
                        id={inputId}
                        className="consultation-answer-input"
                        type="text"
                        placeholder={input.placeholder}
                        required={input.required}
                        value={textInputs[input.answer_key] ?? ""}
                        onChange={(event) => handleCustomInput(node.id, input.answer_key, event.target.value)}
                      />
                    </div>
                  )
                })}

                <button
                  className="consultation-next-button"
                  type="button"
                  disabled={!canSubmitMulti(node, multiInputs[node.id] ?? [], textInputs)}
                  onClick={() =>
                    handleMultiAnswer(
                      node.id,
                      node.next,
                    )
                  }
                >
                  다음
                </button>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

export default ConsultationFlow
