import type { AnalysisResult } from "../types/analysis"
import { useState, useEffect } from "react"
import { useLocation } from "react-router-dom"
import { QRCodeSVG } from "qrcode.react"

type ConsultationLocationState = {
  result: AnalysisResult
  previewUrl: string | null
}

type ConsultationKeyRequest = {
  element: string
  score: number
  text: string
}

function ConsultationResult() {
  const location = useLocation()  
  const state = location.state as ConsultationLocationState
  const [summary, setSummary] = useState("")
  const [keyRequests, setKeyRequests] =
  useState<ConsultationKeyRequest[]>([])
  const [consultationText, setConsultationText] = useState("")
  const [shareId, setShareId] = useState("")
  const [personalRequest, setPersonalRequest] = useState("")
  const [isSharing, setIsSharing] = useState(false)

  const shareUrl = shareId
  ? `${window.location.origin}/share/${shareId}`
  : ""

  const API_BASE_URL = import.meta.env.VITE_API_URL
  const GENERATE_API_URL = `${API_BASE_URL}/consultation/generate`
  const SHARE_API_URL = `${API_BASE_URL}/consultation/share`

  async function fetchConsultation() {
    const response = await fetch(GENERATE_API_URL, {
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

  async function shareConsultation() {
  if (isSharing || shareId) {
    return
  }

  setIsSharing(true)

  try {
    const response = await fetch(SHARE_API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        summary: summary,
        key_requests: keyRequests,
        consultation_text: consultationText,
        personal_request: personalRequest || null,
      }),
    })

    if (!response.ok) {
      throw new Error("상담 공유에 실패했습니다.")
    }

    const data = await response.json()
    setShareId(data.share_id)

  } finally {
    setIsSharing(false)
  }
}

async function copyShareLink() {
  await navigator.clipboard.writeText(shareUrl)
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
            <li key={`${request.element}-${request.score}`}>
                {request.text}
            </li>
            ))}
        </ul>
    </section>

    <section className="consultation-card consultation-script-card">
        <h2>미용사에게 이렇게 말해보세요</h2>
        <p className="consultation-script">{consultationText}</p>
    </section>
    </div>
    
    <section className="consultation-card">
      <h2>추가 요청사항</h2>

      <textarea
        className="consultation-personal-request"
        value={personalRequest}
        onChange={(e) => setPersonalRequest(e.target.value)}
        placeholder="ex: 앞머리 기장은 꼭 눈썹 가리도록 해주세요."
      />
    </section>
    
    <button 
      className="consultation-share-button"
      onClick={shareConsultation}
      disabled={isSharing || !!shareId}>
      {isSharing
        ? "공유 준비 중..."
        : shareId
          ? "공유 링크 생성 완료"
          : "공유하기"}
    </button>

    {shareUrl && (
    <section className="consultation-share-card">
        <div className="consultation-share-header">
        <h2>미용사에게 공유하기</h2>
        <p>
            QR 코드를 스캔하면 상담 내용을 바로 확인할 수 있어요.
        </p>
        </div>

        <div className="consultation-qr-frame">
        <QRCodeSVG
            value={shareUrl}
            size={180}
        />
        </div>

        <div className="consultation-share-link">
          <p>{shareUrl}</p>
        </div>

        <button
          type="button"
          onClick={copyShareLink}
        >
          링크 복사
        </button>
    </section>
    )}
    
    </main>
  )
}

export default ConsultationResult
