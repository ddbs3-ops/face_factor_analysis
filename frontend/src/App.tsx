import { useEffect, useState } from "react"
import "./App.css"
import AnalysisResultView from "./components/AnalysisResult"
import ImageUpload from "./components/ImageUpload"
import type { AnalysisResult, AnalysisStatus } from "./types/analysis"

const ANALYZE_API_URL = "http://127.0.0.1:8000/analyze"
const MEASURE_API_URL = "http://127.0.0.1:8000/measure"

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null) // 선택된 이미지 파일
  const [previewUrl, setPreviewUrl] = useState<string | null>(null) // 이미지 미리보기 URL
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null) // 분석 결과 JSON
  const [analysisStatus, setAnalysisStatus] = useState<AnalysisStatus>("idle") // 분석 상태: "idle" | "loading" | "success" | "error"
  const [errorMessage, setErrorMessage] = useState("")
  const [hairlineYRatio, setHairlineYRatio] = useState<number | null>(null)

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
    }
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

        <ImageUpload
          selectedFile={selectedFile}
          previewUrl={previewUrl}
          disabled={isLoading}
          hairlineYRatio={hairlineYRatio}
          onFileChange={handleFileChange}
        />

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
