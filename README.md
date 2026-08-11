이 프로젝트는 얼굴 특징 분석 -> 얼굴 특징에 맞는 헤어스타일 추천으로 이루어지는 프로젝트다
그중 첫번째로 얼굴 특징 분석을 v1으로 진행중이다
얼굴 특징 분석 이후 각 특징에 어울리는 헤어스타일을 정리한다
 예를 들어 사각턱 -> 하악각 각도 일정 범위 이내 -> 이마를 들어내 시선 중심을 위로 올림 -> 이마를 들어내는 헤어스타일 여러개 추천 -> 생성형 ai로 헤어스타일 확인 및 상담카드 생성

얼굴 특징 분석을 위해서 15정도의 지표를 사진에서 추출한다.
1. 얼굴 가로세로 종횡비 (x,y차이)
2. 광대폭 / 얼굴 길이 비율 (유클리드 거리) <- 일단 나중에
3. 하악각폭 / 얼굴 길이 비율 (유클리드 거리) <- 나중에
4. 하악각폭 / 광대폭 (유클리드 거리)
5. 상안부 비율
6. 중안부 비율
7. 하안부 비율
8. 헤어라인
9. 턱끝 각도
10. 턱끝 둥글기
11. 하악각 각도
12. 하악각 둥글기

먼저 사용자에게 사진을 받을때 정면이 아니면 분석하고자 하는것에 왜곡이 있을 수 있어
최소화 하고자 정면성 검사를 진행한다.
정면성 검사는 mediapipe의 변환행렬을 받는 옵션을 키고, 
yaw, pitch, roll을 계산한다.

1,4,8 에서 모두 쓰이지만 mediapipe의 랜드마크 검출 혹은 다른 방법으로도 검출이 어려운 부분이 있다. 바로 헤어라인 시작점이다. 앞머리에 가려진 사진이 많기 때문에 이걸 정확하게 검출하기는 힘들다. 
따라서 헤어라인 검출 부터 진행한다.
헤어라인 검출은 mediapipe의 selifie_multicalss 를 사용한다. 
selifie_multicalss로 헤어 영역과 피부 영역을 분리한다. 
이후 얼굴 중심 세로선을 랜드마크로 검출하고 그 영역을 좌우로 검사하며 위로 올라간다. 이때 헤어라인이 끝나는 지점을 검출한다. 하지만 앞머리 이마를 덮고있으면 이 추정이 쓸모 없어지기 때문에 중안부 하안부 거리를 통해 간접적으로 검출한다. 이후 UX를 이용해 사용자에게 헤어라인을 직접 움직이게 해서 정확도를 올리려한다.

db에 저장할 목록

#face_measurements_db
id
path
is_frontial

yaw
pitch
roll

height_to_width_ratio
jaw_to_cheekbone_ratio

upper_ratio
middle_ratio
lower_ratio

chin_angle
chin_contour_mean
chin_contour_std
chin_contour_min #가장 강한 코너
chin_contour_range

left_jaw_angle
left_jaw_contour_std
left_jaw_contour_min #가장 강한 코너
left_jaw_contour_range

right_jaw_anlge
right_jaw_contour_std
right_jaw_contour_min #가장 강한 코너
right_jaw_contour_range

#countour_measurement_db
튜플 저장
