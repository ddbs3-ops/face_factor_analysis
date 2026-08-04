import numpy as np
from scipy.spatial.transform import Rotation 
from core.schemas import HeadPose, FrontalityResult

def extract_head_pose(matrix : np.ndarray):
    """
    전달받은 4x4 변환행렬을 yaw,pitch,roll을 추출한다.
    사용하는 회전 분해는 R = Rz(roll) @ Ry(yaw) @ Rx(pitch)
    """

    if matrix.shape != (4, 4):      #is not 썻었는데 에러 발생 했음 이유는 != 는 값이 다른지 비교하고 is not은 같은 객체가 아닌지 비교함
        raise ValueError("4x4 얼굴 변환행렬이 필요합니다.")
    if not np.all(np.isfinite(matrix)):
        raise ValueError("변환 행렬에 잘못된 값이 들어있습니다.")

    rotation_matrix = matrix[:3,:3]

    # 수치 오차가 있는 행렬을
    # 가장 가까운 순수 회전행렬로 직교화한다.
    u, _, vt = np.linalg.svd(rotation_matrix)

    rotation = u @ vt

    # det가 -1이면 회전이 아니라
    # 반사 성분이 포함된 행렬이므로 보정한다.
    if np.linalg.det(rotation) < 0:
        u[:, -1] *= -1
        rotation = u @ vt

    # 대문자 ZYX: intrinsic Euler 분해
    #반환되는 순서도 Z, Y, X
    roll_deg, yaw_deg, pitch_deg = (
        Rotation            #from scipy.spatial.transform import Rotation 
        .from_matrix(rotation)
        .as_euler(
            "ZYX",
            degrees=True,
        )
    )

    return HeadPose(yaw_deg=yaw_deg, roll_deg=roll_deg, pitch_deg=pitch_deg)   #from core.schemas import HeadPose


MAX_YAW_DEG = 15
MAX_ROLL_DEG = 15
MAX_PITCH_DEG = 15

def evaluate_frontality( 
    matrix : np.ndarray
) :
    pose = extract_head_pose(matrix)
    reasons = [] 
    messages = []  
    # 사용자에게 출력할 message에는 사용자 친화적으로 표현 해주어 main에서 출력하도록 리스트로 묶어 return에선 튜플로 반환한다.
    # 값을 갖고 갈 reasons에는 핵심만 담아 "roll 초과 : 몇도, 기준값 : 몇도"이런식으로 리스트를 만들고 튜플로 묶어 반환한다.


    if abs(pose.pitch_deg) > MAX_PITCH_DEG:
        messages += ["고개가 위 아래로 기울어져 있습니다. 고개를 바로 세워 주세요"]
        reasons += [f"pitch 초과 : {pose.pitch_deg:.2f}°, 허용범위 : ±{MAX_PITCH_DEG}"]

    if abs(pose.roll_deg) > MAX_ROLL_DEG:
        messages += ["머리가 한쪽으로 기울어져 있습니다. 머리를 수평으로 맞춰주세요"]
        reasons += [f"roll 초과 : {pose.roll_deg:.2f}°, 허용범위 : ±{MAX_ROLL_DEG}"]

    if abs(pose.yaw_deg) > MAX_YAW_DEG:
        messages += ["얼굴이 옆으로 돌아가 있습니다. 카메라를 정면으로 바라봐 주세요"]
        reasons += [f"yaw 초과 : {pose.yaw_deg:.2f}°, 허용범위 ±{MAX_YAW_DEG}"]
    

    from core.schemas import FrontalityResult
    return FrontalityResult(
         is_frontal= not reasons,
         pose = pose,
         reasons= tuple(reasons),
         messages= tuple(messages)
    )

