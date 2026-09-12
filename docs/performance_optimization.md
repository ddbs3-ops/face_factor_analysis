# Performance Optimization

## Baseline

자세한 기준 데이터는 [performance_baseline.md](performance_baseline.md) 참고.

- `/analyze` mean: 3.131s
- `/analyze` median: 3.256s
- Image load mean: 0.459s
- Image load median: 0.415s

`performance_baseline.md`는 개선 전 원본 기록으로 유지하고, 이 파일에는 변경 내용과 성능 측정 결과를 계속 누적한다.

---

## Optimization 1 — 이미지 중복 로딩 제거

### 변경 내용

기존에는 동일 이미지를 `cv2.imread()`로 두 번 읽고 있었다.

Before:

```text
load_image()
 ├─ cv2.imread()
 └─ prepare_mp_image(path)
      └─ cv2.imread()
```

After:

```text
load_image()
 ├─ cv2.imread()
 └─ prepare_mp_image(img)
```

이미 읽은 NumPy 이미지를 MediaPipe 입력 생성에 재사용하도록 변경했다.

### 측정 조건

- Azure App Service
- 1 vCPU
- 동일 테스트 이미지
- 수정 후 마지막 10회 `/analyze` 요청 사용

### 결과

| 항목 | Before | After | 변화 |
| --- | --- | --- | --- |
| `/analyze` mean | 3.131s | 2.464s | -21.3% |
| `/analyze` median | 3.256s | 2.054s | -36.9% |
| Image load mean | 0.459s | 0.235s | **-48.9%** |
| Image load median | 0.415s | 0.215s | **-48.1%** |
| `/analyze` max | 4.210s | 4.508s | +7.1% |

### 해석

이번 변경의 직접적인 효과는 Image load에서 확인됐다.

Image load 중앙값이 약 0.415초에서 0.215초로 감소하여 약 48% 개선됐다.

전체 `/analyze` 처리시간도 감소했지만, 이번 측정에서는 Segmentation inference 시간 또한 이전보다 낮게 측정됐기 때문에 전체 처리시간 감소분을 모두 이미지 로딩 최적화의 효과로 볼 수는 없다.

또한 최대 처리시간은 여전히 4초 이상으로 나타났다.

따라서 이미지 중복 로딩 문제는 개선됐지만, Selfie Segmentation과 MediaPipe 모델 lifecycle로 인한 변동성은 남아 있다.

---

## Optimization 2 — MediaPipe 모델 재사용

### 변경 내용

기존에는 `/measure`, `/analyze` 요청이 들어올 때마다 Face Landmarker와 Selfie Segmenter를 새로 생성하고, 요청이 끝날 때마다 `close()`로 해제하고 있었다.

Before:

```text
Request
 ├─ Face Landmarker 생성
 ├─ Selfie Segmenter 생성
 ├─ 분석
 ├─ Face Landmarker close
 └─ Selfie Segmenter close
```

After:

```text
Application startup
 ├─ Face Landmarker 생성
 └─ Selfie Segmenter 생성

Request
 └─ 기존 모델 인스턴스 재사용

Application shutdown
 ├─ Face Landmarker close
 └─ Selfie Segmenter close
```

FastAPI의 lifespan을 사용해 앱 시작 시 모델을 한 번만 생성하고, `app.state`에 보관하여 `/measure`, `/analyze` 요청에서 재사용하도록 변경했다.

모델 정리는 `ExitStack`을 사용하여 초기화 도중 예외가 발생하거나 종료 과정에서 일부 정리 작업이 실패하는 경우에도 생성된 리소스가 안전하게 해제되도록 보완했다.

### 측정 조건

- Azure App Service
- 1 vCPU
- 동일 테스트 이미지
- 두 번째 서버 프로세스가 정상 기동된 이후 측정
- 첫 `/analyze` 요청 1회는 별도 기록
- 이후 10회 요청을 비교 표본으로 사용

### 결과

| 항목 | Optimization 1 | Optimization 2 | 변화 |
| --- | --- | --- | --- |
| `/analyze` mean | 2.464s | **1.692s** | **-31.3%** |
| `/analyze` median | 2.054s | **1.533s** | **-25.4%** |
| `/analyze` min | 1.692s | **1.084s** | -35.9% |
| `/analyze` max | 4.508s | **2.713s** | -39.8% |

### 내부 처리시간

| 항목 | 평균 | 중앙값 |
| --- | --- | --- |
| Image load | 0.269s | 0.243s |
| Face inference | 0.077s | 0.062s |
| Segmentation inference | 1.212s | 1.045s |
| Image analysis | 1.627s | 1.466s |
| Reference DB | 0.021s | 0.016s |
| Postprocess | 0.031s | 0.015s |

### 해석

이번 변경에서는 Segmentation inference 시간이 이전 측정과 거의 비슷하게 유지됐다.

Optimization 1에서 Segmentation median은 약 1.049초였고, Optimization 2에서는 약 1.045초로 큰 차이가 없었다.

그럼에도 `/analyze` 중앙값은

```text
2.054s → 1.533s
```

로 약 25.4% 감소했다.

따라서 이번 개선은 단순히 Segmentation이 우연히 빨라진 결과라기보다, 요청마다 반복되던 MediaPipe 모델 생성 및 종료 비용을 제거한 효과가 전체 응답시간 감소에 반영된 것으로 볼 수 있다.

또한 `analyze_user`의 전체 시간과 `image_analysis` 시간이 이전보다 훨씬 가까워졌다.

예를 들어 일부 요청에서는:

```text
image_analysis = 1.162s
analyze_user   = 1.175s
```

정도로 차이가 매우 작게 나타났다.

이는 모델 lifecycle 비용이 요청 처리 경로에서 거의 제거되었음을 보여준다.

### Baseline 대비 누적 개선

| 단계 | `/analyze` mean | `/analyze` median |
| --- | --- | --- |
| Baseline | 3.131s | 3.256s |
| Optimization 1 | 2.464s | 2.054s |
| Optimization 2 | **1.692s** | **1.533s** |

Baseline 대비:

- 평균 처리시간 약 **46.0% 감소**
- 중앙값 처리시간 약 **52.9% 감소**

### 남은 병목

현재 `/analyze`에서 가장 큰 단일 비용은 여전히 Selfie Segmentation inference이다.

Optimization 2 기준 Segmentation median은 약 **1.045s**로, 전체 `/analyze` median 1.533초에서 큰 비중을 차지한다.

현재 `/analyze`는 사용자가 이미 `/measure` 단계에서 확정한 `hairline_y_ratio`를 전달받고 있음에도 Selfie Segmentation을 다시 수행하고 있다.

따라서 다음 최적화에서는 `/analyze`에서 불필요한 Segmentation을 생략할 수 있는지 검토한다.

---

## Optimization 3 — `/analyze` Segmentation 생략

TODO
