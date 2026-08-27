import type { AnalysisResult as Result } from "../types/analysis"
import { useState } from "react"

type Props = {
  result: Result
  previewUrl: string | null
}

type InspectionType =
  | "vertical"
  | "jaw-width"
  | null

const inspectionMap: Record<string, InspectionType> = {
  vertical_face: "vertical",
  lower_face: "jaw-width",
}

function scoreLabel(score: number) {
  if (score > 0) return "추천"
  if (score < 0) return "비추천"
  return "보통"
}

function AnalysisResult({ result, previewUrl }: Props) {
  const [inspectionType, setInspectionType] =
    useState<InspectionType>(null)

  const activateInspection = (type: InspectionType) => {
    setInspectionType(type)
  }

  const clearInspection = () => {
    setInspectionType(null)
  }

  const upperPercent = Math.round(result.vertical_ratios.upper * 100)
  const middlePercent = Math.round(result.vertical_ratios.middle * 100)
  const lowerPercent = Math.round(result.vertical_ratios.lower * 100)
  const upperCenter =
    (result.vertical_points.hairline + result.vertical_points.glabella) / 2
  const middleCenter =
    (result.vertical_points.glabella + result.vertical_points.subnasale) / 2
  const lowerCenter =
    (result.vertical_points.subnasale + result.vertical_points.chin) / 2

  return (
    <section className="results" aria-labelledby="result-title">
      <div className="result-header">
        <p className="eyebrow">ANALYSIS COMPLETE</p>
        <h2 id="result-title">분석 결과</h2>
        <p>얼굴의 특징과 이를 보완하는 헤어 방향을 정리했어요.</p>
      </div>

      {previewUrl && (
        <div className="result-face-preview">
          <img
            src={previewUrl}
            alt="분석된 얼굴"
          />

          <svg
            className={`jaw-width-overlay ${
              inspectionType === "jaw-width" ? "is-active" : ""
            }`}
            viewBox="0 0 100 100"
            preserveAspectRatio="none"
            aria-hidden="true"
          >
            <line
              x1={result.jaw_width_points.left_cheekbone.x * 100}
              y1={result.jaw_width_points.left_cheekbone.y * 100}
              x2={result.jaw_width_points.right_cheekbone.x * 100}
              y2={result.jaw_width_points.right_cheekbone.y * 100}
              className="jaw-width-line cheekbone-line"
              onMouseEnter={() => activateInspection("jaw-width")}
              onMouseLeave={clearInspection}
            />

            <line
              x1={result.jaw_width_points.left_jaw.x * 100}
              y1={result.jaw_width_points.left_jaw.y * 100}
              x2={result.jaw_width_points.right_jaw.x * 100}
              y2={result.jaw_width_points.right_jaw.y * 100}
              className="jaw-width-line jaw-line"
              onMouseEnter={() => activateInspection("jaw-width")}
              onMouseLeave={clearInspection}
            />

            <circle
              cx={result.jaw_width_points.left_cheekbone.x * 100}
              cy={result.jaw_width_points.left_cheekbone.y * 100}
              r="1.2"
              className="jaw-width-point"
            />

            <circle
              cx={result.jaw_width_points.right_cheekbone.x * 100}
              cy={result.jaw_width_points.right_cheekbone.y * 100}
              r="1.2"
              className="jaw-width-point"
            />

            <circle
              cx={result.jaw_width_points.left_jaw.x * 100}
              cy={result.jaw_width_points.left_jaw.y * 100}
              r="1.2"
              className="jaw-width-point"
            />

            <circle
              cx={result.jaw_width_points.right_jaw.x * 100}
              cy={result.jaw_width_points.right_jaw.y * 100}
              r="1.2"
              className="jaw-width-point"
            />
          </svg>
          
          <div
            className={`jaw-width-label cheekbone-label ${
              inspectionType === "jaw-width" ? "is-active" : ""
            }`}
            style={{
              left: `${
                (
                  result.jaw_width_points.left_cheekbone.x +
                  result.jaw_width_points.right_cheekbone.x
                ) / 2 * 100
              }%`,
              top: `${
                (
                  result.jaw_width_points.left_cheekbone.y +
                  result.jaw_width_points.right_cheekbone.y
                ) / 2 * 100
              }%`,
            }}
          >
            광대폭 1.00
          </div>

          <div
            className={`jaw-width-label jaw-label ${
              inspectionType === "jaw-width" ? "is-active" : ""
            }`}
            style={{
              left: `${
                (
                  result.jaw_width_points.left_jaw.x +
                  result.jaw_width_points.right_jaw.x
                ) / 2 * 100
              }%`,
              top: `${
                (
                  result.jaw_width_points.left_jaw.y +
                  result.jaw_width_points.right_jaw.y
                ) / 2 * 100
              }%`,
            }}
          >
            턱폭 {result.jaw_width_ratio.toFixed(2)}
          </div>

          <div
            className={`face-guide-line ${
              inspectionType === "vertical" ? "is-active" : ""
            }`}
            style={{ top: `${result.vertical_points.hairline * 100}%` }}
            onMouseEnter={() => activateInspection("vertical")}
            onMouseLeave={clearInspection}
          >
            <span>헤어라인</span>
          </div>

          <div
            className={`face-guide-line ${
              inspectionType === "vertical" ? "is-active" : ""
            }`}
            style={{ top: `${result.vertical_points.glabella * 100}%` }}
            onMouseEnter={() => activateInspection("vertical")}
            onMouseLeave={clearInspection}
          >
            <span>미간</span>
          </div>

          <div
            className={`face-guide-line ${
              inspectionType === "vertical" ? "is-active" : ""
            }`}
            style={{ top: `${result.vertical_points.subnasale * 100}%` }}
            onMouseEnter={() => activateInspection("vertical")}
            onMouseLeave={clearInspection}
          >
            <span>코밑</span>
          </div>

          <div
            className={`face-guide-line ${
              inspectionType === "vertical" ? "is-active" : ""
            }`}
            style={{ top: `${result.vertical_points.chin * 100}%` }}
            onMouseEnter={() => activateInspection("vertical")}
            onMouseLeave={clearInspection}
          >
            <span>턱끝</span>
          </div>

          <div
            className={`face-region-label ${
              inspectionType === "vertical" ? "is-active" : ""
            }`}
            style={{ top: `${upperCenter * 100}%` }}
          >
            상안부 {upperPercent}%
          </div>

          <div
            className={`face-region-label ${
              inspectionType === "vertical" ? "is-active" : ""
            }`}
            style={{ top: `${middleCenter * 100}%` }}
          >
            중안부 {middlePercent}%
          </div>

          <div
            className={`face-region-label ${
              inspectionType === "vertical" ? "is-active" : ""
            }`}
            style={{ top: `${lowerCenter * 100}%` }}
          >
            하안부 {lowerPercent}%
          </div>
        </div>
      )}


      <div className="result-grid">
        <section className="result-card" aria-labelledby="features-title">
          <div className="card-title"><span className="step-number" aria-hidden="true">02</span>
            <h3 id="features-title">얼굴 특징</h3></div>
          <div className="result-list">
            {result.rules.map((rule, index) => (
              <article
                className="feature-item"
                key={`${rule.source}-${index}`}
                  onMouseEnter={() =>
                  activateInspection(
                    inspectionMap[rule.source] ?? null
                  )
                }
                onMouseLeave={clearInspection}
                >
                <h4>{rule.feature}</h4>
                <p>{rule.effect}</p>
              </article>
            ))}
          </div>
        </section>
        <section className="result-card" aria-labelledby="recommendations-title">
          <div className="card-title"><span className="step-number" aria-hidden="true">03</span>
            <h3 id="recommendations-title">헤어 추천</h3></div>
          <div className="result-list">
            {result.recommendations.map((item) => {
              const kind = item.score > 0 ? "positive" : item.score < 0 ? "negative" : "neutral"
              return <article className="recommendation-item" key={item.element}>
                <p>{item.text}</p>
                <span className={`score-badge score-${kind}`} aria-label={`추천 점수 ${item.score}`}>
                  {scoreLabel(item.score)} {item.score > 0 ? "+" : ""}{item.score}
                </span>
              </article>
            })}
          </div>
        </section>
      </div>
    </section>
  )
}

export default AnalysisResult
