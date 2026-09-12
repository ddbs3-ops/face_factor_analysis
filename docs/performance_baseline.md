# Performance Baseline

> 리팩토링 및 성능 최적화 전에 측정한 서버 성능 기준 데이터입니다.  
> 이후 동일한 조건으로 재측정하여 Before / After 비교에 사용합니다.

## 1. 측정 목적

헤답의 얼굴 분석 API에서 사용자가 체감하는 지연이 어디에서 발생하는지 확인하고,
성능 개선 전 상태를 수치로 남기기 위해 `/measure`, `/analyze` 요청을 단계별로 측정했습니다.

이번 문서는 **최적화 전 기준 데이터**를 보존하는 것이 목적이며,
아직 원인을 확정하거나 개선 효과를 주장하지 않습니다.

## 2. 측정 환경

- 측정일: 2026-09-12
- Backend: FastAPI
- Deployment: Azure App Service
- 서버 사양: 1 vCPU
- MediaPipe Face Landmarker
- MediaPipe Selfie Segmentation
- 동일 테스트 이미지 반복 요청
- 서버 내부 `time.perf_counter()` 기준
- 브라우저 Network 시간과 화면 렌더링 시간은 제외

---

# 3. `/measure` Baseline

## 측정 횟수

- 서버 시작 직후 요청: 1회
- 이후 요청: 10회
- 총 11회

비교 기준 통계는 서버 시작 직후 첫 요청을 제외한 **10회**를 사용합니다.

## 서버 시작 직후 첫 요청

| 항목 | 시간 |
| --- | ---: |
| File save | 0.021s |
| Face model init | 0.866s |
| Segment model init | 0.482s |
| Image load | 2.489s |
| Face inference | 0.091s |
| Segmentation inference | 2.691s |
| Rest | 0.793s |
| `/measure` total | **7.431s** |

## 이후 10회 통계

| 항목 | 평균 | 중앙값 | 최소 | 최대 |
| --- | ---: | ---: | ---: | ---: |
| `/measure` total | **2.929s** | **2.245s** | 1.737s | **7.322s** |
| Image load | 0.632s | 0.456s | 0.325s | 1.504s |
| MediaPipe model init (Face + Segment) | 0.415s | 0.353s | 0.202s | 1.124s |
| Face inference | 0.109s | 0.066s | 0.049s | 0.292s |
| Segmentation inference | **1.596s** | **1.285s** | 0.883s | **3.780s** |
| Rest | 0.155s | 0.060s | 0.040s | 1.002s |

## 관찰

`/measure`에서는 Selfie Segmentation inference가 가장 큰 처리 비용을 차지했습니다.

이후 10회 기준:

- Segmentation inference 평균: **1.596s**
- `/measure` 전체 평균: **2.929s**
- 평균 시간 기준 Segmentation inference가 전체의 약 **54.5%**
- Face inference 평균은 **0.109s**로 상대적으로 작음
- Image load도 평균 **0.632s**로 무시하기 어려운 비용
- 일반적으로 2초 초반대에 끝나는 요청이 많았지만, 최대 **7.322s**까지 증가한 요청도 존재

느린 요청에서는 Segmentation만 느려지는 것이 아니라 이미지 로딩, 모델 초기화,
기타 처리도 함께 느려지는 경우가 관찰되었습니다.

---

# 4. `/analyze` Baseline

## 측정 횟수

- 서버 재시작 직후 첫 요청: 1회
- 이후 요청: 12회
- 총 13회

비교 기준 통계는 첫 요청을 제외한 **12회**를 사용합니다.

## 서버 재시작 직후 첫 요청

| 항목 | 시간 |
| --- | ---: |
| File save | 0.029s |
| Face model init | 1.278s |
| Segment model init | 0.984s |
| Image analysis | 4.956s |
| Reference DB | 0.772s |
| Postprocess | 0.192s |
| `analyze_user` total | 9.146s |
| `/analyze` total | **9.176s** |

`image_analysis` 내부:

| 항목 | 시간 |
| --- | ---: |
| Image load | 2.474s |
| Face inference | 0.273s |
| Segmentation inference | 2.049s |
| Detect total | 2.323s |
| Rest | 0.140s |

첫 요청에서는 특정 한 단계만이 아니라 모델 생성, 이미지 로딩,
Segmentation, DB 조회 등 여러 단계가 동시에 느렸습니다.

## 이후 12회 통계

| 항목 | 평균 | 중앙값 | 최소 | 최대 |
| --- | ---: | ---: | ---: | ---: |
| `/analyze` total | **3.131s** | **3.256s** | 2.171s | **4.210s** |
| `analyze_user` | 3.118s | 3.249s | 2.152s | 4.192s |
| Image analysis | **2.111s** | **2.237s** | 1.406s | 3.104s |
| Face model init | 0.157s | 0.127s | 0.100s | 0.250s |
| Segment model init | 0.240s | 0.184s | 0.130s | 0.473s |
| Model init total | 0.398s | 0.352s | 0.230s | 0.715s |
| Reference DB | 0.042s | 0.030s | 0.011s | 0.151s |
| Postprocess | 0.016s | 0.011s | 0.002s | 0.041s |
| File save | 0.013s | 0.010s | 0.002s | 0.042s |

### `image_analysis` 내부

| 항목 | 평균 | 중앙값 | 최소 | 최대 |
| --- | ---: | ---: | ---: | ---: |
| Image load | 0.459s | 0.415s | 0.314s | 0.762s |
| Face inference | 0.079s | 0.065s | 0.050s | 0.171s |
| Segmentation inference | **1.503s** | **1.600s** | 0.895s | **2.259s** |
| Rest | 0.065s | 0.061s | 0.040s | 0.108s |

## 관찰

`/analyze`에서도 가장 큰 단일 비용은 Selfie Segmentation inference였습니다.

이후 12회 기준:

- Segmentation inference 평균: **1.503s**
- `image_analysis` 평균: **2.111s**
- `/analyze` 전체 평균: **3.131s**
- Segmentation은 평균 기준 `image_analysis`의 약 **71%**
- Segmentation은 평균 기준 `/analyze` 전체의 약 **48%**
- Face inference 평균은 **0.079s**
- Reference DB 평균은 **0.042s**
- Postprocess 평균은 **0.016s**

따라서 현재 측정값만 보면 DB 조회나 추천 후처리보다
MediaPipe 관련 처리와 이미지 분석 단계의 비용이 훨씬 큽니다.

---

# 5. 미계측 구간

`analyze_user`의 단계별 측정값을 모두 합한 값과 `total` 사이에 차이가 존재합니다.

첫 요청을 제외한 12회에서 이 차이는:

| 항목 | 평균 | 중앙값 | 최소 | 최대 |
| --- | ---: | ---: | ---: | ---: |
| 미계측 구간 | 0.551s | 0.493s | 0.372s | 1.286s |

현재 코드 구조상 이 구간에는 MediaPipe 객체의 `close()` 수행 시간이 포함되어 있을 가능성이 높지만,
`close()` 자체를 별도로 계측하지 않았기 때문에 **모델 종료 시간으로 확정하지 않습니다.**

향후 필요하면 별도 계측합니다.

---

# 6. 현재 확인된 구조적 개선 후보

아직 리팩토링 전이며 아래 항목은 **측정값을 바탕으로 한 개선 후보**입니다.

1. **Selfie Segmentation 중복 실행 검토**
   - `/measure`에서 헤어라인을 계산한 뒤 사용자가 `hairline_y_ratio`를 확정해 `/analyze`에 전달함
   - 현재 `/analyze`에서도 다시 Selfie Segmentation이 실행됨
   - 이미 확정된 헤어라인을 사용하는 경우 두 번째 Segmentation이 필요한지 구조적으로 검토

2. **MediaPipe 모델 재사용 검토**
   - 현재 요청마다 Face Landmarker와 Selfie Segmenter를 생성하고 종료함
   - `/analyze`에서 모델 생성만 평균 약 **0.398s**

3. **이미지 중복 로딩 제거 검토**
   - 현재 이미지 처리 과정에서 같은 파일을 중복 decode하는 경로가 존재
   - `/measure` Image load 평균 **0.632s**
   - `/analyze` Image load 평균 **0.459s**

4. **DB / 추천 후처리는 낮은 우선순위**
   - Reference DB 평균 **0.042s**
   - Postprocess 평균 **0.016s**
   - 현재 전체 지연에서 차지하는 비중이 작음

---

# 7. 측정 시 주의사항

`/measure`와 `/analyze`의 `total`은 현재 계측 범위가 완전히 동일하지 않습니다.

- `/measure`의 성능 로그는 `finally`에서 MediaPipe 모델을 `close()`하기 전에 출력됨
- `/analyze`의 `analyze_user` total에는 `finally`의 모델 종료 구간이 포함됨

따라서 현재 `/measure total`과 `/analyze total`을 서로 직접 비교하기보다는,
각 엔드포인트의 **리팩토링 전후 비교 기준**으로 사용하는 것이 적절합니다.

또한 이번 측정은 동일 이미지에 대한 소규모 반복 테스트이며,
실제 다중 사용자 부하 테스트나 SLA 측정 결과가 아닙니다.

---

# 8. Before / After 비교용 기준값

리팩토링 후 동일한 환경과 테스트 이미지로 다시 측정합니다.

| 항목 | Before | After | 개선율 |
| --- | ---: | ---: | ---: |
| `/measure` mean | 2.929s | - | - |
| `/measure` median | 2.245s | - | - |
| `/measure` max | 7.322s | - | - |
| `/measure` segmentation median | 1.285s | - | - |
| `/analyze` mean | 3.131s | - | - |
| `/analyze` median | 3.256s | - | - |
| `/analyze` max | 4.210s | - | - |
| `/analyze` segmentation median | 1.600s | - | - |

## 다음 측정 원칙

리팩토링 후에는 가능한 한 다음 조건을 유지합니다.

- 동일 Azure 서버 사양
- 동일 테스트 이미지
- 동일한 요청 흐름
- 첫 요청은 별도 기록
- 이후 반복 요청의 mean / median / min / max 기록
- `/measure`, `/analyze` 각각 비교
