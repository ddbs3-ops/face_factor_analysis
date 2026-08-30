import { useParams } from "react-router-dom"
import { useEffect, useState } from "react"

function SharedConsultation() {
  const { shareId } = useParams()

  const [consultation, setConsultation] = useState<any>(null)

  const API_BASE_URL = import.meta.env.VITE_API_URL

  useEffect(() => {
    async function fetchSharedConsultation() {
      const response = await fetch(
        `${API_BASE_URL}/consultations/${shareId}`
      )

      if (!response.ok) {
        throw new Error("상담 결과를 불러오지 못했습니다.")
      }

      const data = await response.json()
      setConsultation(data)
    }

    fetchSharedConsultation()
  }, [shareId])

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
