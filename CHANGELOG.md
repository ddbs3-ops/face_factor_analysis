# Changelog

---

## v1.1 - 2026.08.19

### Changed
- 헤어라인 탐색 범위를 얼굴 중앙에서 양쪽 눈 바깥쪽 영역까지 확대
- skin-hair boundary 기반 검출 방식으로 개선
- 전체 boundary median 대신 위쪽 15% 후보의 median 사용
- geometric estimate 보정값과 fallback 기준 조정

### Added
- Streamlit 기반 `hairline_labeler.py` 검증 도구 추가

### Result
- 가일 스타일, 가르마, 한쪽 헤어라인 노출 케이스에서 검출 안정성 개선

### Known Issue
-  상부 이마를 대부분 가리는 짧은 내림머리에서는 앞머리 경계를 실제 헤어라인으로 검출하여 얼굴 세로/가로 비율이 과소추정될 수 있음

---

## v1 - 2026.08.09 ~ 2026.08.18

### Added
- MediaPipe Face Landmarker 기반 얼굴 랜드마크 추출
- yaw / pitch / roll 기반 정면 여부 확인
- 얼굴 세로 / 가로 비율 측정
- 상안부 / 중안부 / 하안부 비율 측정
- 턱 폭 / 광대 폭 비율 측정
- 턱끝 각도 및 좌우 하악각 측정
- 턱/하악 윤곽 local angle 측정
- SQLite 저장 파이프라인 구축
- 초기 segmentation 기반 헤어라인 추정 로직 구현
- AI Hub 데이터셋에서 남성 정면 이미지 선별 파이프라인 구축

### Known Issues
- 가일, 가르마, 앞머리 등 헤어스타일에 따라 헤어라인 검출 오차 발생