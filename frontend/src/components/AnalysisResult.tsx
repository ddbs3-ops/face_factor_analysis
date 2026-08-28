import type { AnalysisResult as Result } from "../types/analysis"
import { useState } from "react"

type Props = {
  result: Result
  previewUrl: string | null
}

type InspectionType =
  | "face-ratio"
  | "vertical"
  | "jaw-width"
  | "jaw-angle"
  | "chin-angle"
  | null

type HoveredGuide =
  | "cheekbone"
  | "jaw"
  | "face-height"
  | null

const inspectionMap: Record<string, InspectionType> = {
  face_ratio: "face-ratio",
  vertical_ratio: "vertical",
  jaw_width: "jaw-width",
  jaw_angle: "jaw-angle",
  chin_angle: "chin-angle",
}

function getMeasurementStat(
  rule: Result["rules"][number],
  measurementStats: Result["measurement_stats"],
) {
  if (rule.source === "face_ratio") {
    return measurementStats.face_ratio
  }

  if (rule.source === "jaw_width") {
    return measurementStats.jaw_width
  }

  if (rule.source === "jaw_angle") {
    return measurementStats.jaw_angle
  }

  if (rule.source === "chin_angle") {
    return measurementStats.chin_angle
  }

  if (rule.source === "vertical_ratio") {
    if (rule.dominant_region === "upper") {
      return measurementStats.upper_ratio
    }

    if (rule.dominant_region === "middle") {
      return measurementStats.middle_ratio
    }

    if (rule.dominant_region === "lower") {
      return measurementStats.lower_ratio
    }
  }

  return null
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
  const [hoveredGuide, setHoveredGuide] =useState<HoveredGuide>(null)

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
          
          {/* 1. 턱폭 시각화 */}
          <svg
            className={`jaw-width-overlay ${
              inspectionType === "jaw-width" ||
              inspectionType === "face-ratio"
                ? "is-active" : ""
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
              className={`jaw-width-line cheekbone-line ${
              hoveredGuide === "cheekbone" ||
              hoveredGuide === "jaw" ||
              hoveredGuide === "face-height" ||
              inspectionType === "jaw-width" ||
              inspectionType === "face-ratio"
                ? "is-active"
                : ""
            }`}
              onMouseEnter={() => setHoveredGuide("cheekbone")}
              onMouseLeave={() => setHoveredGuide(null)}  
            />

            <line
              x1={result.jaw_width_points.left_jaw.x * 100}
              y1={result.jaw_width_points.left_jaw.y * 100}
              x2={result.jaw_width_points.right_jaw.x * 100}
              y2={result.jaw_width_points.right_jaw.y * 100}
              className={`jaw-width-line jaw-line ${
                hoveredGuide === "jaw" ||
                hoveredGuide === "cheekbone" ||
                inspectionType === "jaw-width"
                  ? "is-active"
                  : ""
              }`}
              onMouseEnter={() => setHoveredGuide("jaw")}
              onMouseLeave={() => setHoveredGuide(null)}
            />

          </svg>
          <div
            className={`jaw-width-label cheekbone-label ${
              inspectionType === "jaw-width" ||
              inspectionType === "face-ratio" ||
              hoveredGuide === "jaw" ||
              hoveredGuide === "cheekbone" ||
              hoveredGuide === "face-height"
                ? "is-active"
                : ""
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
              inspectionType === "jaw-width" ||
              hoveredGuide === "jaw" ||
              hoveredGuide === "cheekbone"
                ? "is-active"
                : ""
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

          {/* 하악각 시각화 */}
          <svg
            className={`jaw-angle-overlay ${
              inspectionType === "jaw-angle" ? "is-active" : ""
            }`}
            viewBox="0 0 100 100"
            preserveAspectRatio="none"
            aria-hidden="true"
          >
            {/* 왼쪽 하악각 */}
            <line
              x1={result.jaw_angle_points.left.intersection.x * 100}
              y1={result.jaw_angle_points.left.intersection.y * 100}
              x2={result.jaw_angle_points.left.upper_end.x * 100}
              y2={result.jaw_angle_points.left.upper_end.y * 100}
              className="jaw-angle-line"
              onMouseEnter={() => activateInspection("jaw-angle")}
              onMouseLeave={clearInspection}
            />

            <line
              x1={result.jaw_angle_points.left.intersection.x * 100}
              y1={result.jaw_angle_points.left.intersection.y * 100}
              x2={result.jaw_angle_points.left.lower_end.x * 100}
              y2={result.jaw_angle_points.left.lower_end.y * 100}
              className="jaw-angle-line"
              onMouseEnter={() => activateInspection("jaw-angle")}
              onMouseLeave={clearInspection}
            />

            {/* 오른쪽 하악각 */}
            <line
              x1={result.jaw_angle_points.right.intersection.x * 100}
              y1={result.jaw_angle_points.right.intersection.y * 100}
              x2={result.jaw_angle_points.right.upper_end.x * 100}
              y2={result.jaw_angle_points.right.upper_end.y * 100}
              className="jaw-angle-line"
              onMouseEnter={() => activateInspection("jaw-angle")}
              onMouseLeave={clearInspection}
            />

            <line
              x1={result.jaw_angle_points.right.intersection.x * 100}
              y1={result.jaw_angle_points.right.intersection.y * 100}
              x2={result.jaw_angle_points.right.lower_end.x * 100}
              y2={result.jaw_angle_points.right.lower_end.y * 100}
              className="jaw-angle-line"
              onMouseEnter={() => activateInspection("jaw-angle")}
              onMouseLeave={clearInspection}
            />
          </svg>
          <div
            className={`jaw-angle-label left-jaw-angle-label ${
              inspectionType === "jaw-angle" ? "is-active" : ""
            }`}
            style={{
              left: `${
                result.jaw_angle_points.left.intersection.x * 100
              }%`,
              top: `${
                result.jaw_angle_points.left.intersection.y * 100
              }%`,
            }}
          >
            왼쪽 하악각 {result.measurement_stats.jaw_angle.left_value.toFixed(1)}°
          </div>

          <div
            className={`jaw-angle-label right-jaw-angle-label ${
              inspectionType === "jaw-angle" ? "is-active" : ""
            }`}
            style={{
              left: `${
                result.jaw_angle_points.right.intersection.x * 100
              }%`,
              top: `${
                result.jaw_angle_points.right.intersection.y * 100
              }%`,
            }}
          >
            오른쪽 하악각 {result.measurement_stats.jaw_angle.right_value.toFixed(1)}°
          </div>
          <svg
            className={`face-ratio-overlay ${
              inspectionType === "face-ratio" ||
              hoveredGuide === "face-height"
                ? "is-active" : ""
            }`}
            viewBox="0 0 100 100"
            preserveAspectRatio="none"
            aria-hidden="true"
          >
            <line
              x1={result.height_width_ratio_visual_points.top.x * 100}
              y1={result.height_width_ratio_visual_points.top.y * 100}
              x2={result.height_width_ratio_visual_points.bottom.x * 100}
              y2={result.height_width_ratio_visual_points.bottom.y * 100}
              className={`face-height-line ${
                hoveredGuide === "face-height" ||
                hoveredGuide === "cheekbone" ||
                inspectionType === "face-ratio"
                  ? "is-active"
                  : ""
              }`}
              onMouseEnter={() => setHoveredGuide("face-height")}
              onMouseLeave={() => setHoveredGuide(null)}
            />
          </svg>
          <div
            className={`face-ratio-label ${
              inspectionType === "face-ratio" ||
              hoveredGuide === "face-height" ||
              hoveredGuide === "cheekbone"
                ? "is-active"
                : ""
            }`}
            style={{
              left: `${
                (
                  result.height_width_ratio_visual_points.top.x +
                  result.height_width_ratio_visual_points.bottom.x
                ) / 2 * 100
              }%`,
              top: `${
                (
                  result.height_width_ratio_visual_points.top.y +
                  result.height_width_ratio_visual_points.bottom.y
                ) / 2 * 100
              }%`,
            }}
          >
            얼굴 길이 {result.measurement_stats.face_ratio.value.toFixed(2)}
          </div>
        </div>
      )}


      <div className="result-grid">
        <section className="result-card" aria-labelledby="features-title">
          <div className="card-title"><span className="step-number" aria-hidden="true">02</span>
            <h3 id="features-title">얼굴 특징</h3></div>
          <div className="result-list">
            {result.rules.map((rule, index) => {
              const stat = getMeasurementStat(
                rule,
                result.measurement_stats,
              )

              return (
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

                  {stat && (
                    <p>
                      내 측정값 {stat.value} · 평균 {stat.mean}
                    </p>
                  )}
                </article>
              )
            })}
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
