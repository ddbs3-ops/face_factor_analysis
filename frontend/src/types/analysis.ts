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

export type AnalysisResult = {
  vertical_ratios: VerticalRatios
  vertical_points: VerticalPoints

  jaw_width_ratio: number
  jaw_width_points: JawWidthPoints

  measurement_stats: MeasurementStats

  jaw_angle_points: {
    left: JawAngleVisualPoints
    right: JawAngleVisualPoints
  }
  height_width_ratio_visual_points: HeightWidthRatioVisualPoints
  
  rules: AnalysisRule[]
  merged_adjustments: Adjustments
  recommendations: Recommendation[]
}



export type AnalysisStatus = "idle" | "loading" | "success" | "error"
