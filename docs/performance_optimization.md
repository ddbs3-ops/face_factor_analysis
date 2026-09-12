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

TODO

---

## Optimization 3 — /analyze segmentation 제거

TODO
