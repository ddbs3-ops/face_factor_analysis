import { useEffect, useState } from "react"
import "./App.css"
import AnalysisResultView from "./components/AnalysisResult"
import ImageUpload from "./components/ImageUpload"
import type { AnalysisResult, AnalysisStatus } from "./types/analysis"

const ANALYZE_API_URL = "http://127.0.0.1:8000/analyze"

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [analysisStatus, setAnalysisStatus] = useState<AnalysisStatus>("idle")
  const [errorMessage, setErrorMessage] = useState("")

  useEffect(() => {
    if (!selectedFile) {
      setPreviewUrl(null)
      return
    }
    const objectUrl = URL.createObjectURL(selectedFile)
    setPreviewUrl(objectUrl)
    return () => URL.revokeObjectURL(objectUrl)
  }, [selectedFile])

  function handleFileChange(file: File | null) {
    setSelectedFile(file)
    setAnalysisResult(null)
    setAnalysisStatus("idle")
    setErrorMessage("")
  }

  async function handleAnalyze() {
    if (!selectedFile || analysisStatus === "loading") return

    const formData = new FormData()
    formData.append("file", selectedFile)
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
      setAnalysisStatus("success")
    } catch {
      setAnalysisResult(null)
      setAnalysisStatus("error")
      setErrorMessage("이미지를 분석하지 못했습니다. 잠시 후 다시 시도해주세요.")
    }
  }

  const isLoading = analysisStatus === "loading"

  return (
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
          </div>
        </div>

        <ImageUpload selectedFile={selectedFile} previewUrl={previewUrl}
          disabled={isLoading} onFileChange={handleFileChange} />

        <button className="analyze-button" type="button"
          disabled={!selectedFile || isLoading} onClick={handleAnalyze}>
          {isLoading ? "분석 중..." : "얼굴 분석하기"}
        </button>

        <div className="status-message" aria-live="polite">
          {isLoading && <p>얼굴 특징을 분석하고 있습니다.</p>}
          {analysisStatus === "error" && (
            <p className="error-message" role="alert">{errorMessage}</p>
          )}
        </div>
      </section>

      {analysisStatus === "success" && analysisResult && (
        <AnalysisResultView result={analysisResult} />
      )}
    </main>
  )
}

export default App
