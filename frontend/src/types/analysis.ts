export type Adjustments = Record<string, number>

export type AnalysisRule = {
  source: string
  face_type?: string
  dominant_region?: string
  feature: string
  feature_level: number
  adjustments: Adjustments
  effect: string
}

export type Recommendation = { element: string; score: number; text: string }

export type AnalysisResult = {
  rules: AnalysisRule[]
  merged_adjustments: Adjustments
  recommendations: Recommendation[]
}

export type AnalysisStatus = "idle" | "loading" | "success" | "error"
