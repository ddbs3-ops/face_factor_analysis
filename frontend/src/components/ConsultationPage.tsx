import { useState } from "react"
import { useLocation } from "react-router-dom"
import ConsultationFlow from "./ConsultationFlow"
import ConsultationResult from "./ConsultationResult"

type ConsultationMode = "quick" | "guided"

type ConsultationLocationState = {
  mode?: ConsultationMode
}

type GuidedAnswers = Record<string, string | string[]>

function ConsultationPage() {
  const location = useLocation()

  const state =
    location.state as ConsultationLocationState | null

  const mode = state?.mode

  const [guidedAnswers, setGuidedAnswers] =
    useState<GuidedAnswers | null>(null)

  function handleGuidedComplete(
    answers: GuidedAnswers,
  ) {
    setGuidedAnswers(answers)
  }

  if (mode === "guided") {
    if (guidedAnswers) {
      return (
        <ConsultationResult
          guidedAnswers={guidedAnswers}
        />
      )
    }

    return (
      <ConsultationFlow
        onComplete={handleGuidedComplete}
      />
    )
  }

  if (mode === "quick") {
    return <ConsultationResult />
  }

  return <div>상담 방식을 확인할 수 없습니다.</div>
}

export default ConsultationPage