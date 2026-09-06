export type HairElement =
  | "top_volume"
  | "side_volume"
  | "forehead_exposure"
  | "bangs_length"
  | "bangs_weight"
  | "parting_asymmetry"
  | "curl_strength"

export type EvidenceStrength = "direct"

export type RuleContribution = {
  element: HairElement
  value: number
  reason: string
  evidence_strength: EvidenceStrength
}

export type AnalysisRule = {
  source: string
  face_type?: string
  dominant_region?: "upper" | "middle" | "lower"
  feature: string
  feature_level: number
  contributions: RuleContribution[]
  effect: string
}

export type RecommendationReason = {
  source: string
  feature: string
  feature_level: number
  contribution: number
  reason: string
  evidence_strength: EvidenceStrength
}

export type Recommendation = {
  element: HairElement
  score: number
  text: string
  reasons: RecommendationReason[]
}

export type MergedContribution = {
  source: string
  feature: string
  feature_level: number
  value: number
  reason: string
  evidence_strength: EvidenceStrength
}

export type MergedRule = {
  score: number
  contributions: MergedContribution[]
}

export type MergedRules = Record<HairElement, MergedRule>

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

export type JawAngleVisualPoints = {
  intersection: PointRatio
  upper_end: PointRatio
  lower_end: PointRatio
}

export type MeasurementStat = {
  value: number
  mean: number
  top_percent: number
}

export type JawAngleStat = MeasurementStat & {
  left_value: number
  right_value: number
}

export type MeasurementStats = {
  face_ratio: MeasurementStat
  upper_ratio: MeasurementStat
  middle_ratio: MeasurementStat
  lower_ratio: MeasurementStat
  jaw_width: MeasurementStat
  chin_angle: MeasurementStat
  jaw_angle: JawAngleStat
}

export type HeightWidthRatioVisualPoints = {
  top: PointRatio
  bottom: PointRatio
}

export type FrontalityResult = {
  is_frontal: boolean
  pose: {
    yaw_deg: number
    pitch_deg: number
    roll_deg: number
  }
  messages: string[]
  reasons: string[]
}

export type ChinAnglePoints = {
  intersection: PointRatio
  left_end: PointRatio
  right_end: PointRatio
}

export type AnalysisResult = {
  frontality_result: FrontalityResult
  vertical_ratios: VerticalRatios
  vertical_points: VerticalPoints
  jaw_width_ratio: number
  jaw_width_points: JawWidthPoints
  measurement_stats: MeasurementStats

  jaw_angle_points: {
    left: JawAngleVisualPoints
    right: JawAngleVisualPoints
  }

  chin_angle_points: ChinAnglePoints
  height_width_ratio_visual_points: HeightWidthRatioVisualPoints

  rules: AnalysisRule[]
  merged_rules: MergedRules
  recommendations: Recommendation[]
}


export type AnalysisStatus = "idle" | "loading" | "success" | "error"
