import { useEffect, useRef, useState } from "react"

type QuestionOption = {
  value: string
  label: string
  next?: string
}

type QuestionNode = {
  id: string
  type: "single" | "multi" | "text" | "complete"
  text?: string
  options?: QuestionOption[]
  next?: string
}

type FlowDefinition = {
  version: string
  root: string
  nodes: Record<string, QuestionNode>
}

type AnswerValue = string | string[]

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
  }, [])

  useEffect(() => {
    if (history.length > 1) {
      latestQuestionRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      })
    }
  }, [history.length, latestQuestionId])

  function handleSingleAnswer(
    nodeId: string,
    value: string,
    nextId?: string,
  ) {
    if (!flow) return

    const nodeIndex = history.indexOf(nodeId)

    if (nodeIndex === -1) return

    // 현재 질문까지의 경로만 남김
    const newHistory = history.slice(0, nodeIndex + 1)

    // 기존 answers 복사
    const newAnswers = { ...answers }

    // 현재 질문보다 뒤에 있던 답변들은 삭제
    const removedNodeIds = history.slice(nodeIndex + 1)

    removedNodeIds.forEach((oldNodeId) => {
      delete newAnswers[oldNodeId]
    })

    // 현재 질문의 새 답변 저장
    newAnswers[nodeId] = value

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

  function handleTextAnswer(nodeId: string, nextId?: string) {
    if (!flow) return

    const value = textInputs[nodeId]?.trim()

    if (!value) return

    const nodeIndex = history.indexOf(nodeId)

    if (nodeIndex === -1) return

    const newHistory = history.slice(0, nodeIndex + 1)
    const newAnswers = { ...answers }

    history.slice(nodeIndex + 1).forEach((oldNodeId) => {
      delete newAnswers[oldNodeId]
    })

    newAnswers[nodeId] = value

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

  function toggleMultiAnswer(nodeId: string, value: string) {
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
    if (!flow) return

    const values = multiInputs[nodeId] ?? []

    if (values.length === 0) return

    const nodeIndex = history.indexOf(nodeId)

    if (nodeIndex === -1) return

    const newHistory = history.slice(0, nodeIndex + 1)
    const newAnswers = { ...answers }

    history.slice(nodeIndex + 1).forEach((oldNodeId) => {
      delete newAnswers[oldNodeId]
    })

    newAnswers[nodeId] = values

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

                <button
                  className="consultation-next-button"
                  type="button"
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
