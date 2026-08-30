import type { AnalysisResult } from "../types/analysis"
import { useState, useEffect } from "react"
import { useLocation } from "react-router-dom"

type ConsultationLocationState = {
  result: AnalysisResult
  previewUrl: string | null
}

function ConsultationResult() {
  const location = useLocation()  
  const state = location.state as ConsultationLocationState
  const [summary, setSummary] = useState("")
  const [keyRequests, setKeyRequests] = useState<string[]>([])
  const [consultationText, setConsultationText] = useState("")

  const API_BASE_URL = import.meta.env.VITE_API_URL
  const CONSULTATION_API_URL = `${API_BASE_URL}/consultation`

  async function fetchConsultation() {
    const response = await fetch(CONSULTATION_API_URL, {
        method: "POST",
        headers: {
        "Content-Type": "application/json",
        },
        body: JSON.stringify({
        recommendations: state.result.recommendations,
        }),
    })

    if (!response.ok) {
        throw new Error("상담문 생성에 실패했습니다.")
    }

    const data = await response.json()
    setSummary(data.summary)
    setKeyRequests(data.key_requests)
    setConsultationText(data.consultation_text)
  }

  useEffect(() => {
    fetchConsultation()
  }, []) //처음 한번만 실행

  return (
    <main className="app-shell consultation-page">
    <header className="consultation-header">
      <p className="eyebrow">CONSULTATION GUIDE</p>
      <h1>헤어 상담 가이드</h1>
    </header>

    <div className="consultation-grid">
    <section className="consultation-card consultation-summary-card">
        <h2>추천 방향 요약</h2>
        <p className="consultation-card-copy">{summary}</p>
    </section>

    <section className="consultation-card consultation-requests-card">
        <h2>핵심 요청사항</h2>

        <ul className="consultation-request-list">
        {keyRequests.map((request) => (
            <li key={request}>{request}</li>
        ))}
        </ul>
    </section>

    <section className="consultation-card consultation-script-card">
        <h2>미용사에게 이렇게 말해보세요</h2>
        <p className="consultation-script">{consultationText}</p>
    </section>
    </div>
    </main>
  )
}

export default ConsultationResult
