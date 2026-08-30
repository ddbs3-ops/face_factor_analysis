import { useEffect, useState } from "react"
import "./App.css"
import AnalysisResultView from "./components/AnalysisResult"
import ImageUpload from "./components/ImageUpload"
import type { AnalysisResult, AnalysisStatus } from "./types/analysis"
import { Routes, Route, useNavigate } from "react-router-dom"
import ConsultationResult from "./components/ConsultationResult"
import SharedConsultation from "./components/SharedConsultation"

const API_BASE_URL = import.meta.env.VITE_API_URL

const ANALYZE_API_URL = `${API_BASE_URL}/analyze`
const MEASURE_API_URL = `${API_BASE_URL}/measure`

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null) // 선택된 이미지 파일
  const [previewUrl, setPreviewUrl] = useState<string | null>(null) // 이미지 미리보기 URL
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null) // 분석 결과 JSON
  const [analysisStatus, setAnalysisStatus] = useState<AnalysisStatus>("idle") // 분석 상태: "idle" | "loading" | "success" | "error"
  const [errorMessage, setErrorMessage] = useState("")
  const [hairlineYRatio, setHairlineYRatio] = useState<number | null>(null)
  const [isMeasuring, setIsMeasuring] = useState(false)
  const [showFrontalityWarning, setShowFrontalityWarning] = useState(false)

  const navigate = useNavigate()

  useEffect(() => {
    if (!selectedFile) { // 선택된 파일이 없으면 미리보기 URL을 null로 설정
      setPreviewUrl(null)
      return
    }
    const objectUrl = URL.createObjectURL(selectedFile)// 선택된 파일을 브라우저에서 미리보기할 수 있는 URL 객체 생성
    setPreviewUrl(objectUrl)
    return () => URL.revokeObjectURL(objectUrl) // 선택된 파일이 변경되거나 컴포넌트가 언마운트될 때 URL 객체를 해제하여 메모리 누수를 방지
  }, [selectedFile])

  function handleFileChange(file: File | null) {
    setSelectedFile(file)
    setAnalysisResult(null)
    setAnalysisStatus("idle")
    setErrorMessage("")
    setHairlineYRatio(null)

    if (file) {
      measureHairline(file)
    }
  }

  async function measureHairline(file: File) {
    const formData = new FormData()
    formData.append("file", file)

    setIsMeasuring(true)

    try {
      const response = await fetch(MEASURE_API_URL, {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        throw new Error("헤어라인 측정에 실패했습니다.")
      }

      const result = await response.json()

      setHairlineYRatio(result.hairline_y_ratio)

      console.log("자동 헤어라인:", result.hairline_y_ratio)
    } catch {
      setHairlineYRatio(null)
      setErrorMessage("헤어라인을 찾지 못했습니다. 얼굴이 정면으로 잘 보이는 다른 사진을 선택해주세요.")
    } finally {
      setIsMeasuring(false)
    }
  }

  async function handleAnalyze() {
    if (
      !selectedFile ||
      hairlineYRatio === null ||
      analysisStatus === "loading"
    ) return

    const formData = new FormData()
    formData.append("file", selectedFile)
    formData.append("hairline_y_ratio", String(hairlineYRatio))
    setAnalysisStatus("loading")
    setErrorMessage("")

    try {
      const response = await fetch(ANALYZE_API_URL, {
        method: "POST",
        body: formData,
      })
      if (!response.ok) throw new Error("분석 요청에 실패했습니다.")

      const result: AnalysisResult = await response.json()
      setAnalysisResult(result)
      if (!result.frontality_result.is_frontal) {
        setShowFrontalityWarning(true)
      }
      setAnalysisStatus("success")
    } catch {
      setAnalysisResult(null)
      setAnalysisStatus("error")
      setErrorMessage("이미지를 분석하지 못했습니다. 잠시 후 다시 시도해주세요.")
    }
  }

  const isLoading = analysisStatus === "loading"

  return (
    <Routes>
      <Route 
        path = "/"
        element = {
          <main className="app-shell">
            <section className="hero" aria-labelledby="page-title">
              <p className="eyebrow">FACE FACTOR ANALYSIS</p>
              <h1 id="page-title">내 얼굴에 어울리는 헤어 방향 찾기</h1>
              <p className="hero-description">
                정면 사진 한 장으로 얼굴의 비율과 특징을 분석하고, 균형을 살리는
                헤어스타일 방향을 확인해보세요.
              </p>
            </section>

            <section className="upload-card" aria-labelledby="upload-title">
              <div className="section-heading">
                <span className="step-number" aria-hidden="true">01</span>
                <div>
                  <h2 id="upload-title">사진 업로드</h2>
                  <p>얼굴이 정면으로 잘 보이는 밝은 사진을 선택해주세요.</p>
                  <p>자동으로 표시된 선이 실제 헤어라인과 다르면 위아래로 조정해주세요.</p>
                </div>
                {isMeasuring && (
                  <p>헤어라인을 찾는 중...</p>
                )}
              </div>

              <ImageUpload
                selectedFile={selectedFile}
                previewUrl={previewUrl}
                disabled={isLoading}
                hairlineYRatio={hairlineYRatio}
                onHairlineChange={setHairlineYRatio}
                onFileChange={handleFileChange}
              />

              <button className="analyze-button" type="button"
                disabled={!selectedFile || isLoading || isMeasuring || hairlineYRatio === null} 
                onClick={handleAnalyze}>
                {isMeasuring
                  ? "헤어라인 찾는 중..."
                  : isLoading
                    ? "분석 중..."
                    : "얼굴 분석하기"}
              </button>

              <div className="status-message" aria-live="polite">
                {isLoading && <p>얼굴 특징을 분석하고 있습니다.</p>}
                {analysisStatus === "error" && (
                  <p className="error-message" role="alert">{errorMessage}</p>
                )}
              </div>
            </section>
            {showFrontalityWarning && analysisResult && (
              <div className="frontality-warning-backdrop">
                <div className="frontality-warning-modal">
                  <h3>사진이 조금 기울어져 있어요 🙈</h3>

                  <ul className="frontality-warning-list">
                    {analysisResult.frontality_result.messages.map((message) => (
                      <li key={message}>{message}</li>
                    ))}
                  </ul>

                  <p>
                    정면 사진일수록 더 정확하게 분석할 수 있어요.
                    <br />
                    현재 사진은 일부 측정값에 오차가 있을 수 있어요.
                  </p>

                  <div className="frontality-warning-actions">
                    <button
                      type="button"
                      onClick={() => {
                        setShowFrontalityWarning(false)
                        setSelectedFile(null)
                        setAnalysisResult(null)
                        setAnalysisStatus("idle")
                      }}
                    >
                      다른 사진 선택
                    </button>

                    <button
                      type="button"
                      onClick={() => setShowFrontalityWarning(false)}
                    >
                      그래도 결과 보기
                    </button>
                  </div>
                </div>
              </div>
            )}

            {analysisStatus === "success" && analysisResult && (
              <AnalysisResultView result={analysisResult} previewUrl={previewUrl} />
            )}

            {analysisStatus === "success" && analysisResult && (
              <button
                className="consultation-create-button"
                type="button"
                onClick={() => navigate("/consultation",{
                  state: {
                    result:analysisResult,
                    previewUrl: previewUrl,
                  },
                }
                )}
              >
                상담문 생성하기
              </button>
            )}            
          </main>
        }
      />  
      <Route
        path="/consultation"
        element={
          <ConsultationResult />
        }
      />
      <Route
        path="/share/:shareId"
        element={<SharedConsultation />}
      />
    </Routes>  
  )
}

export default App
