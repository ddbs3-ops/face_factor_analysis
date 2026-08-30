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
    return <p>상담 결과를 불러오는 중...</p>
  }

  return (
    <main className="app-shell">
      <h1>헤어 상담 요청</h1>

      <section>
        <h2>추천 방향</h2>
        <p>{consultation.summary}</p>
      </section>

      <section>
        <h2>핵심 요청사항</h2>
        <ul>
          {consultation.key_requests.map((request: any) => (
            <li key={`${request.element}-${request.score}`}>
              {request.text}
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h2>상담 내용</h2>
        <p>{consultation.consultation_text}</p>
      </section>
    </main>
  )
}

export default SharedConsultation
