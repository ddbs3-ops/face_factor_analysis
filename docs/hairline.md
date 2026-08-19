# Hairline Estimation

Face Factor Analysis에서 얼굴 세로 길이와 상안부 비율을 계산하기 위해
헤어라인 위치를 별도로 추정합니다.

MediaPipe Face Landmarker는 실제 헤어라인을 직접 제공하지 않고,
앞머리나 가르마에 의해 보이는 모발 경계가 실제 헤어라인과 달라질 수 있기 때문에
`segmentation 기반 검출`과 `geometric estimate`를 함께 사용합니다.

---

## v1 문제 상황

v1에서는 얼굴 중앙의 좁은 영역에서
각 x 위치마다 아래에서 위로 탐색하며 처음 발견되는 hair pixel을 수집하고,
그 y값들의 median을 detected hairline으로 사용했습니다.

하지만 테스트 과정에서 다음과 같은 문제가 확인되었습니다.

- 가일 스타일
- 6:4 / 7:3 가르마
- 한쪽만 헤어라인이 노출된 스타일
- 앞머리가 이마 전체를 가리는 스타일

특히 실제 헤어라인이 한쪽에 보이더라도
전체 boundary의 median 때문에 앞머리 끝을 헤어라인으로 선택하는 경우가 있었습니다.

---

## v1.1 개선

### 탐색 영역 확대

얼굴 중앙의 좁은 탐색 범위를 제거하고,
MediaPipe의 양쪽 눈 바깥쪽 랜드마크 사이를 탐색하도록 변경했습니다.

이를 통해 가르마나 가일 스타일처럼
헤어라인이 한쪽에서 노출되는 경우에도 해당 정보를 활용할 수 있습니다.

### Skin-Hair Boundary

단순히 hair pixel을 처음 만나는 것이 아니라,

`skin 확인 → 이후 처음 만나는 hair`

를 boundary로 사용합니다.

이를 통해 이마 피부가 확인된 영역에서
피부와 모발이 `전환되는 지점`을 헤어라인 후보로 사용합니다.

### 위쪽 Boundary 우선 사용

모든 boundary의 median 대신
y값이 작은 위쪽 15%를 선택한 뒤 그 median을 사용합니다.

`skin-hair boundary`
→ `위쪽 15% 선택`
→ `median`
→ `detected hairline`

이를 통해 한쪽에서만 실제 헤어라인이 보이는 경우를 더 안정적으로 처리합니다.

---

## Geometric Estimate

segmentation 결과를 보완하기 위해
중안부와 하안부 길이를 이용한 기하학적 추정값을 함께 사용합니다.

현재는 다음과 같이 계산합니다.

`estimated upper face length`
`= ((middle face length + lower face length) / 2) * 0.85`


`difference ratio`
`= |detected - estimated| / middle face length`

- difference ratio <= 0.30 → detected 사용
- difference ratio > 0.30 → estimated 사용
- detected가 없는 경우 → estimated 사용

---

### 왜 '0.85'와 '0.30' 인가?

여기서 `0.85`와 `0.30`은 해부학적 기준이나 통계적으로 최적화된 값이 아니라,
여러 얼굴 이미지의 결과를 수동으로 확인하면서 현재 rule-based 방식이
안정적으로 동작하도록 경험적으로 설정한 값입니다.

향후 충분한 ground truth hairline 데이터가 확보되면
회귀 또는 머신러닝 기반 분석을 통해 해당 값과 추정 방식을 다시 보정할 예정입니다.


---

## 현재 결과와 한계

수동 검증 결과,
가일 스타일, 가르마, 한쪽 헤어라인 노출 등의 경우에서
v1보다 안정적인 헤어라인 검출이 가능해졌습니다.

다만 짧은 내림머리나
헤어라인이 부분적으로만 드러나는 경우에는 여전히 오차가 발생할 수 있습니다.

현재는 예외 규칙을 계속 추가하기보다
일반적인 사진에서 안정적으로 동작하는 수준에서
rule-based 헤어라인 추정을 마무리합니다.

추후 충분한 수동 라벨 데이터가 확보되면
회귀나 머신러닝, 이미지 기반 모델을 이용한 보정을 별도로 실험할 예정입니다.