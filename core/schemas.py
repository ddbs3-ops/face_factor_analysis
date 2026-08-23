from dataclasses import dataclass
from pathlib import Path

@dataclass
class HeadPose:
    yaw_deg: float
    pitch_deg: float
    roll_deg: float

@dataclass
class  FrontalityResult:
    is_frontal: bool
    pose: HeadPose
    reasons: tuple[str,...] #reasons는 문자열이 0개 이상 들어가는 튜플이다.
    messages: tuple[str,...]

@dataclass
class Point3D:
    x : float
    y : float
    z : float

@dataclass
class Point2D:
    x:float
    y:float

@dataclass
class RawFace:
    points : tuple[Point3D, ...]
    image_width : int
    image_height : int

@dataclass
class VerticalFacePoints:
    glabella_y: float
    subnasale_y: float
    chin_y: float

@dataclass
class VerticalFaceRatios:
    upper : float
    middle : float
    lower : float

@dataclass
class HairlineResult:
    detected_y : float | None
    estimated_y : float
    final_y : float | None


@dataclass
class JawMeasurements:
    jaw_to_cheekbone_width_ratio: float

    chin_contour_angles_deg: tuple[float, ...]
    left_jaw_contour_angles_deg: tuple[float, ...]
    right_jaw_contour_angles_deg: tuple[float, ...]

    chin_angle_deg: float
    left_jaw_angle_deg: float
    right_jaw_angle_deg: float


@dataclass
class FaceMeasurements:
    height_to_width_ratio: float
    vertical_ratios: VerticalFaceRatios
    jaw: JawMeasurements


@dataclass
class SelectedSample:
    image_path: Path
    person_id: int
    gt_yaw: float
    gt_pitch: float
    gt_roll: float

@dataclass
class HairlineROI:
    left_x: int
    right_x: int
    top_y: int
    bottom_y: int

@dataclass
class ImageAnalysisResult:
    frontality_result: FrontalityResult
    face_measurements: FaceMeasurements
    hairline_result: HairlineResult
    image_width: int
    image_height: int

@dataclass
class ImageMeasurementResult:
    frontality_result: FrontalityResult
    raw_face: RawFace
    vertical_facepoints: VerticalFacePoints
    hairline_result: HairlineResult
    image_width: int
    image_height: int