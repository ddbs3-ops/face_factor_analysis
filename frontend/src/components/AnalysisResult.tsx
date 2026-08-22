import type { AnalysisResult as Result } from "../types/analysis"

function scoreLabel(score: number) {
  if (score > 0) return "추천"
  if (score < 0) return "비추천"
  return "보통"
}

function AnalysisResult({ result }: { result: Result }) {
  return (
    <section className="results" aria-labelledby="result-title">
      <div className="result-header">
        <p className="eyebrow">ANALYSIS COMPLETE</p>
        <h2 id="result-title">분석 결과</h2>
        <p>얼굴의 특징과 이를 보완하는 헤어 방향을 정리했어요.</p>
      </div>
      <div className="result-grid">
        <section className="result-card" aria-labelledby="features-title">
          <div className="card-title"><span className="step-number" aria-hidden="true">02</span>
            <h3 id="features-title">얼굴 특징</h3></div>
          <div className="result-list">
            {result.rules.map((rule, index) => (
              <article className="feature-item" key={`${rule.source}-${index}`}>
                <h4>{rule.feature}</h4><p>{rule.effect}</p>
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
