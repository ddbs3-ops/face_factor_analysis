import { useState } from "react"

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)

  async function handleAnalyze() {
    if (!selectedFile) {
      return
    }

    const formData = new FormData()
    formData.append("file", selectedFile)

    const response = await fetch(
      "http://127.0.0.1:8000/analyze",
      {
        method: "POST",
        body: formData,
      }
    )

    const result = await response.json()

    setAnalysisResult(result)
  }

  type Rule = {
  source: string
  feature: string
  feature_level: number
  effect: string
}

type Recommendation = {
  element: string
  score: number
  text: string
}

type AnalysisResult = {
  rules: Rule[]
  merged_adjustments: Record<string, number>
  recommendations: Recommendation[]
}

  return (
    <main>
      <h1>헤어 분석</h1>

      <input
        type="file"
        accept="image/*"
        onChange={(event) => {
          const file = event.target.files?.[0] ?? null
          setSelectedFile(file)
        }}
      />

      {selectedFile && (
        <>
          <p>선택한 파일: {selectedFile.name}</p>

        </>
      )}

      <button
        disabled={!selectedFile}
        onClick={handleAnalyze}
      >
        분석하기
      </button>

      {analysisResult && (
        <div>
          <h2>얼굴 특징</h2>

          {analysisResult.rules.map((rule, index) => (
            <div key={index}>
              <p>특징: {rule.feature}</p>
              <p>효과: {rule.effect}</p>
            </div>
          ))}
        
          <h2>헤어 추천</h2>

          {analysisResult.recommendations.map((recommendation) => (
            <div key={recommendation.element}>
              <p>{recommendation.text}
              {" "}
              (score: {recommendation.score})
              </p>
            </div>
          ))}
        </div>
      )}
    </main>
  )
}

export default App