# Face Factor Analysis

얼굴 사진에서 기하학적 특징을 정량적으로 측정하고,
이를 설명 가능한 헤어스타일 추천에 활용하기 위한 개인 프로젝트입니다.

## 프로젝트 소개

기존의 얼굴형 분석은 얼굴을 `oval`, `heart`, `round`, `square` 등
소수의 얼굴형 라벨로 분류하는 경우가 많습니다.

Face Factor Analysis는 하나의 얼굴형으로 분류하는 대신,
얼굴을 구성하는 세부적인 비율과 윤곽 특성을 각각 측정하는 것을 목표로 합니다.

현재 측정하는 주요 특징은 다음과 같습니다.

- 얼굴 세로 / 가로 비율
- 상안부 / 중안부 / 하안부 비율
- 턱 폭 / 광대 폭 비율
- 턱끝 각도
- 좌우 하악각
- 턱 및 하악 윤곽의 local angle

장기적으로는 이러한 얼굴 특징과 헤어스타일 요소 사이의 관계를 데이터화하여,

`얼굴 특징 → 시각적 특성 → 조절할 헤어 요소 → 시각적 효과`

형태의 **설명 가능한 헤어 추천 시스템**을 구축하는 것이 목표입니다.

---

## 분석 대상

현재는 **남성 얼굴과 남성 헤어스타일**을 중심으로 분석을 진행합니다.

남성 헤어스타일은 앞머리 노출 정도, 가르마, 옆머리 볼륨,
윗머리 높이 등 얼굴 비율과 연결되는 요소가 비교적 명확하며,
초기 단계에서는 분석 범위를 제한하여 측정 및 추천 기준을 안정적으로 구축하는 것이 필요하다고 판단했습니다.

따라서 현재 데이터셋과 측정 기준은 남성 얼굴 이미지를 중심으로 구성합니다.

향후 분석 기준과 추천 로직이 충분히 안정화되면
여성 헤어스타일을 포함한 더 넓은 범위로 확장할 예정입니다.

---

## 현재 분석 파이프라인

MediaPipe Face Landmarker를 이용해 얼굴 랜드마크를 추출하고,
기하학적 특징을 계산한 뒤 SQLite 데이터베이스에 저장합니다.

주요 흐름은 다음과 같습니다.

`얼굴 이미지`
→ `Face Landmark 추출`
→ `정면 여부 확인`
→ `헤어라인 추정`
→ `얼굴 비율 및 윤곽 측정`
→ `SQLite 저장`

### 촬영 상태

- yaw
- pitch
- roll
- frontal 여부

### 얼굴 비율

- 얼굴 세로 / 가로 비율
- 상안부 / 중안부 / 하안부 비율
- 턱 폭 / 광대 폭 비율

### 턱과 윤곽

- 턱끝 각도
- 좌우 하악각
- 턱 및 하악 윤곽의 local angle

---

## 시스템 아키텍처

현재 프로젝트는 얼굴 분석 로직과 웹 서비스 계층을 분리하여 구성합니다.

```text
React / Vite Frontend
        ↓
     FastAPI
        ↓
Face Analysis Pipeline
        ↓
Reference Database
```

프론트엔드는 사용자의 이미지 업로드와 분석 결과 표시를 담당하고,
FastAPI 백엔드는 이미지 입력을 받아 기존 얼굴 분석 파이프라인을 호출합니다.

백엔드 API 계층과 핵심 분석 로직을 분리하여,
웹 환경과 무관하게 얼굴 분석 기능을 독립적으로 유지할 수 있도록 구성합니다.

주요 디렉터리 역할은 다음과 같습니다.

```text
backend/      FastAPI API 계층
frontend/     React / Vite 사용자 인터페이스
core/         얼굴 측정 및 분석 핵심 로직
database/     SQLite 저장 및 조회
config/       모델 및 데이터 경로 설정
models/       MediaPipe 모델 파일
data/         기준 데이터베이스 및 분석 데이터
docs/         알고리즘 및 배포 과정 문서
```

---

## 데이터셋

현재 대규모 분석을 위해 AI Hub 안면 데이터셋을 사용합니다.

출처:
https://aihub.or.kr/aihubdata/data/view.do?srchOptnCnd=OPTNCND001&currMenu=115&topMenu=100&searchKeyword=celeb-k&aihubDataSe=data&dataSetSn=71427

분석 대상은 다음 조건으로 선별합니다.

- 남성
- 동일 인물당 한 장
- GT yaw = 0
- GT pitch = 0
- GT roll = 0

이를 통해 동일한 조건의 정면 얼굴 이미지를 대상으로
얼굴 기하학적 특징 데이터를 구축합니다.

---

## 헤어라인 추정

얼굴 세로 길이와 상안부 비율을 계산하려면
얼굴의 위쪽 기준점인 헤어라인이 필요합니다.

하지만 MediaPipe Face Landmarker는 실제 헤어라인을 직접 제공하지 않고,
앞머리나 가르마 등에 의해 보이는 모발 경계와 실제 헤어라인이 달라질 수 있습니다.

따라서 현재는 segmentation 기반 검출과
얼굴 비율 기반 geometric estimate를 함께 사용합니다.

현재 검출은

`skin-hair boundary`
→ `위쪽 15% 후보`
→ `median`
→ `detected hairline`

방식으로 동작하며,
detected 값이 geometric estimate와 크게 차이나는 경우에는
estimated hairline을 fallback으로 사용합니다.

다만 짧은 내림머리처럼 실제 헤어라인이 가려진 경우에는
자동 추정만으로 정확한 위치를 판단하기 어렵습니다.

현재 웹 UI에서는 자동 추정된 헤어라인 위치를 이미지 위에 표시하고,
사용자가 필요할 경우 직접 위치를 조정할 수 있도록 구성했습니다.

분석 과정은 다음과 같습니다.

```text
이미지 업로드
→ 자동 헤어라인 측정
→ 추정 위치 표시
→ 사용자 확인 또는 수정
→ 최종 분석
```

상세한 설계 및 개선 과정은
[`docs/hairline.md`](docs/hairline.md)에 정리합니다.

---

## 검증

헤어라인 알고리즘을 빠르게 검증하기 위해
Streamlit 기반의 내부 라벨링 도구를 사용합니다.

`tools/hairline_labeler.py`

이 도구를 통해

- segmentation boundary
- detected hairline
- estimated hairline
- 실제 분석 로직이 선택하는 hairline

을 이미지와 함께 확인할 수 있습니다.

또한 사람이 직접 `visible`, `partial`, `covered` 상태와
필요한 경우 실제 hairline y를 기록하여
향후 알고리즘 개선에 사용할 검증 데이터를 구축할 수 있습니다.

해당 도구는 핵심 분석 알고리즘이 아닌
반복적인 검증과 수동 라벨링을 위한 내부 도구이므로,
UI 구현에는 Codex를 활용한 바이브 코딩 방식을 사용했습니다.

---

## 현재 한계

현재 시스템은 모든 헤어스타일에서 정확한 헤어라인을 복원하는 것을 목표로 하지 않습니다.

특히 다음과 같은 경우에는 오차가 발생할 수 있습니다.

- 짧게 내려온 앞머리
- 실제 헤어라인이 대부분 가려진 스타일
- 헤어라인이 매우 제한된 영역에서만 노출되는 경우
- segmentation 결과가 불안정한 이미지

현재 단계에서는 규칙 기반 예외처리를 계속 추가하기보다
일반적인 사진에서 안정적으로 동작하는 수준을 우선합니다.

---

## 개발 환경

프론트엔드와 백엔드는 로컬 개발 환경에서 각각 실행할 수 있습니다.

### Backend

가상환경 활성화 후 FastAPI 서버를 실행합니다.

```bash
uvicorn backend.app.main:app --reload
```

기본 로컬 주소:

```text
http://127.0.0.1:8000
```

FastAPI 문서:

```text
http://127.0.0.1:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Vite 환경변수를 이용해 개발 환경과 운영 환경의 API 주소를 분리합니다.

```text
.env.development
→ 로컬 FastAPI 서버

.env.production
→ Azure에 배포된 FastAPI 서버
```

프론트엔드 코드에서는 실행 환경에 관계없이 다음 환경변수를 사용합니다.

```ts
const API_BASE_URL = import.meta.env.VITE_API_URL
```

`npm run dev` 실행 시 development 환경이 사용되고,
production build 시 production 환경변수가 적용됩니다.

이를 통해 로컬 개발과 운영 환경에서 API 주소를 코드 내부에서 직접 변경하지 않고 관리할 수 있습니다.

---

## 배포 및 CI/CD

백엔드는 Docker 기반으로 컨테이너화하여 Azure App Service에 배포합니다.

현재 배포 흐름은 다음과 같습니다.

```text
Developer
   ↓
git push origin main
   ↓
GitHub Actions
   ↓
Docker Image Build
   ↓
Azure Container Registry
   ↓
Azure App Service
   ↓
FastAPI Backend
```

`main` 브랜치에 코드가 push되면 GitHub Actions가 자동으로 실행됩니다.

GitHub Actions는 다음 작업을 수행합니다.

1. 저장소 checkout
2. Azure 로그인
3. Docker 이미지 빌드
4. Azure Container Registry에 이미지 push
5. Azure App Service가 새 Docker 이미지를 사용하도록 설정
6. App Service 재시작
7. 배포된 API 응답 확인

이를 통해 데스크탑이나 노트북 등 개발 장비가 변경되더라도
동일한 Git 저장소를 기준으로 개발 및 배포할 수 있습니다.

Docker 이미지는 FastAPI 백엔드 실행에 필요한 코드와 모델만 포함하며,
React 프론트엔드는 별도 배포를 전제로 백엔드 Docker 이미지에서 제외합니다.

배포 과정에서 발생한 주요 문제와 해결 과정은
[`docs/azure_deployment_troubleshooting.md`](docs/azure_deployment_troubleshooting.md)에 정리합니다.

---

## 향후 계획

현재 구축한 얼굴 기하학적 측정 파이프라인을 기반으로
얼굴 특징과 헤어스타일 요소 사이의 관계를 지속적으로 데이터화합니다.

최종적으로는

`얼굴 특징`
→ `시각적 특성`
→ `조절할 헤어 요소`
→ `시각적 효과`

관계를 이용하여
사용자에게 **왜 해당 헤어스타일이 적합한지 설명할 수 있는 추천 시스템**을 구축하는 것이 목표입니다.

헤어라인 추정의 경우에는 현재 rule-based 방식을 유지하고,
추후 충분한 수동 라벨 데이터가 확보되면

- 선형 회귀
- Random Forest / Gradient Boosting
- 이미지 기반 딥러닝

등을 이용한 보정 방법을 별도로 실험할 예정입니다.

또한 현재 구축된 FastAPI 백엔드와 React 프론트엔드를 기반으로
실제 사용자가 접근할 수 있는 MVP 형태의 웹 서비스를 완성하는 것을 목표로 합니다.

---

## Development History

버전별 주요 변경 사항은 [`CHANGELOG.md`](CHANGELOG.md)에서 관리합니다.

헤어라인 알고리즘의 상세한 시행착오와 설계 과정은
[`docs/hairline.md`](docs/hairline.md)에서 확인할 수 있습니다.

Azure 및 Docker 배포 과정의 주요 문제와 해결 과정은
[`docs/azure_deployment_troubleshooting.md`](docs/azure_deployment_troubleshooting.md)에서 확인할 수 있습니다.