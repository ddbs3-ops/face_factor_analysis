from dataclasses import dataclass

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