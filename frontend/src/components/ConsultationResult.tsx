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

type ConsultationResultProps = {
  guidedAnswers?: Record<string, string | string[]>
}

function ConsultationResult({ guidedAnswers }: ConsultationResultProps) {
  const location = useLocation()  
  const state = location.state as ConsultationLocationState
  const [summary, setSummary] = useState("")
  const [keyRequests, setKeyRequests] =
  useState<ConsultationKeyRequest[]>([])
  const [consultationText, setConsultationText] = useState("")
  const [shareId, setShareId] = useState("")
  const [personalRequest, setPersonalRequest] = useState("")
  const [isSharing, setIsSharing] = useState(false)
  const [referenceImage, setReferenceImage] = useState<File | null>(null)
  const [referenceImagePreview, setReferenceImagePreview] = useState<string | null>(null)
  const [shareError, setShareError] = useState("")

  const shareUrl = shareId
  ? `${window.location.origin}/share/${shareId}`
  : ""

  const API_BASE_URL = import.meta.env.VITE_API_URL
  const GENERATE_API_URL = `${API_BASE_URL}/consultation/generate`
  const SHARE_API_URL = `${API_BASE_URL}/consultation/share`

  function handleReferenceImageChange(event: React.ChangeEvent<HTMLInputElement>,) {
    const file = event.target.files?.[0]

    if (!file) {
      return
    }

    const previewUrl = URL.createObjectURL(file)

    setReferenceImage(file)
    setReferenceImagePreview(previewUrl)
  }

  function handleRemoveReferenceImage() {
    if (referenceImagePreview) {
      URL.revokeObjectURL(referenceImagePreview)
    }

    setReferenceImage(null)
    setReferenceImagePreview(null)
  }

  async function uploadReferenceImage(file: File) {
    const formData = new FormData()

    formData.append("image", file)

    const response = await fetch(
      `${API_BASE_URL}/consultation/reference-image`,
      {
        method: "POST",
        body: formData,
      },
    )

    if (!response.ok) {
      throw new Error("참고 이미지 업로드에 실패했습니다.")
    }

    const data = await response.json()

    return data.blob_name
  }

  async function fetchConsultation() {
    const response = await fetch(GENERATE_API_URL, {
        method: "POST",
        headers: {
        "Content-Type": "application/json",
        },
        body: JSON.stringify({
        recommendations: state.result.recommendations,
        guided_answers: guidedAnswers,
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
      let referenceImageBlobName: string | null = null

      if (referenceImage) {
        referenceImageBlobName =
          await uploadReferenceImage(referenceImage)
      }

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
          reference_image_blob_name: referenceImageBlobName,
        }),
      })

      if (!response.ok) {
        throw new Error("상담 공유에 실패했습니다.")
      }

      const data = await response.json()
      setShareId(data.share_id)

    } catch (error) {
      console.error(error)
      setShareError("상담 공유에 실패했습니다. 다시 시도해주세요.")
    } finally {
      setIsSharing(false)
    }
  }

async function copyShareLink() {
  await navigator.clipboard.writeText(shareUrl)
}
  useEffect(() => {
    if (!referenceImagePreview) {
      return
    }

    return () => {
      URL.revokeObjectURL(referenceImagePreview)
    }
  }, [referenceImagePreview])

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
        <section className="consultation-card consultation-requests-card">
            <h2>AI 추천 요청사항</h2>

            <ul className="consultation-request-list">
                {keyRequests.map((request) => (
                <li key={`${request.element}-${request.score}`}>
                    {request.text}
                </li>
                ))}
            </ul>
        </section>

        {guidedAnswers && (
          <section className="consultation-card consultation-script-card">
            <h2>고객 희망사항</h2>
            <p className="consultation-script">{consultationText}</p>
          </section>
        )}
      </div>
      
      <section className="reference-image-section">
        <h2>참고 헤어사진</h2>

        <p>
          원하는 헤어스타일이 있다면 사진 1장을 추가해주세요.
        </p>

        <input
          type="file"
          accept="image/jpeg,image/png,image/webp"
          onChange={handleReferenceImageChange}
          disabled={isSharing || !!shareId}
        />

        {referenceImagePreview && (
          <div className="reference-image-preview">
            <img
              src={referenceImagePreview}
              alt="참고 헤어스타일 미리보기"
            />

            <button
              type="button"
              onClick={handleRemoveReferenceImage}
              disabled={isSharing || !!shareId}
            >
              사진 삭제
            </button>
          </div>
        )}
      </section>


      <section className="consultation-card consultation-personal-card">
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

      {shareError && (
        <p className="consultation-share-error">
          {shareError}
        </p>
      )}

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
