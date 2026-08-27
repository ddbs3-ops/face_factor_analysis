export type Adjustments = Record<string, number>

export type AnalysisRule = {
  source: string
  face_type?: string
  dominant_region?: "upper" | "middle" | "lower"
  feature: string
  feature_level: number
  adjustments: Adjustments
  effect: string
}

export type Recommendation = { element: string; score: number; text: string }

export type VerticalRatios = {
  upper: number
  middle: number
  lower: number
}

export type VerticalPoints = {
  hairline: number
  glabella: number
  subnasale: number
  chin: number
}

export type PointRatio = {
  x: number
  y: number
}

export type JawWidthPoints = {
  left_cheekbone: PointRatio
  right_cheekbone: PointRatio
  left_jaw: PointRatio
  right_jaw: PointRatio
}

export type AnalysisResult = {
  vertical_ratios: VerticalRatios
  vertical_points: VerticalPoints

  jaw_width_ratio: number
  jaw_width_points: JawWidthPoints

  rules: AnalysisRule[]
  merged_adjustments: Adjustments
  recommendations: Recommendation[]
}

export type AnalysisStatus = "idle" | "loading" | "success" | "error"
