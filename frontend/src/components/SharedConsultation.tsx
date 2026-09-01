import { useParams } from "react-router-dom"
import { useEffect, useState } from "react"

function SharedConsultation() {
  const { shareId } = useParams()

  const [consultation, setConsultation] = useState<any>(null)
  const [error, setError] = useState("")

  const API_BASE_URL = import.meta.env.VITE_API_URL

  useEffect(() => {
    async function fetchSharedConsultation() {
      try {
        const response = await fetch(
          `${API_BASE_URL}/consultations/${shareId}`
        )
        
        if(response.status === 404) {
          setError("존재하지 않거나 만료된 상담 입니다.")
        }
        if (!response.ok) {
          setError("상담 결과를 불러오지 못했습니다.")
        }

        const data = await response.json()
        setConsultation(data)

      } catch {
        setError("서버에 연결할 수 없습니다.")
      }
    }

    fetchSharedConsultation()
  }, [shareId])

  if (error) {
    return (
      <main className="shared-consultation-page shared-consultation-error">
        <section className="shared-error-card">
          <div className="shared-error-icon" aria-hidden="true">
            !
          </div>

          <p className="shared-eyebrow">HAIR CONSULTATION</p>

          <h1>상담 결과를 확인할 수 없습니다</h1>

          <p className="shared-error-message">
            {error}
          </p>

          <p className="shared-error-guide">
            공유 링크를 다시 확인하거나 상담을 생성한 사용자에게
            새로운 링크를 요청해주세요.
          </p>
        </section>
      </main>
  )
}

  if (!consultation) {
    return (
      <main className="shared-consultation-page shared-consultation-loading">
        <p>상담 결과를 불러오는 중...</p>
      </main>
    )
  }

  return (
    <main className="shared-consultation-page">
        <header className="shared-header">
        <p className="shared-eyebrow">HAIR CONSULTATION</p>
        <h1>헤어 상담 요청</h1>
        <p className="shared-header-description">
            고객이 원하는 헤어 방향을 확인해주세요.
        </p>
        </header>

        <section
        className="shared-primary-card"
        aria-labelledby="shared-requests-title"
        >
        <div className="shared-section-heading">
            <h2 id="shared-requests-title">핵심 요청사항</h2>
        </div>

        <div className="shared-request-list">
            {consultation.key_requests.map((request: any) => (
            <div
                className="shared-request-item"
                key={`${request.element}-${request.score}`}
            >
                <span className="shared-request-category">
                {request.element.replaceAll("_", " ")}
                </span>

                <p>{request.text}</p>
            </div>
            ))}
        </div>
        </section>
    </main>
    )
}

export default SharedConsultation
