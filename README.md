# Hedap (헤답) 
"헤어의 답을 찾다"

> 얼굴의 비율과 윤곽을 분석하고, 어떤 헤어 방향을 왜 추천하는지 설명하는 남성 헤어 상담 서비스

Hedap은 얼굴을 하나의 얼굴형으로 분류하는 대신, 세부적인 비율과 윤곽을 각각 측정합니다.
분석 결과를 바탕으로 헤어 요소의 조절 방향과 이유를 보여주고,
고객이 원하는 스타일과 평소 손질 습관을 정리해 미용사와 공유할 수 있도록 돕습니다.

[서비스 바로가기](https://hedap.kr)

## 서비스 사용 흐름

1. **사진 업로드** — 정면 얼굴 사진에서 랜드마크와 헤어라인을 추정합니다.
2. **헤어라인 확인·보정** — 이미지 위의 선을 드래그해 실제 위치에 맞춥니다.
3. **얼굴 특징과 추천 이유 확인** — 측정 영역을 사진에서 확인하고, 추천 카드를 펼쳐 근거를 읽습니다.
4. **상담 요청 작성** — 커트·펌 질문에 답하거나 빠른 상담 모드로 이동합니다.
5. **미용사에게 공유** — 추천 요청사항, 고객 희망사항, 추가 요청과 참고 헤어사진을 링크·QR로 전달합니다.

## 1. 사진 업로드 및 헤어라인 검출 및 보정
<img width="1235" height="1570" alt="Image" src="https://github.com/user-attachments/assets/6e1e05d2-1223-4761-81bd-089fa9f5b1fd" />

## 2. 분석 결과 화면 
<img width="2153" height="1527" alt="Image" src="https://github.com/user-attachments/assets/2d34cec4-d961-42fb-8449-adfd0b4b46b8" />

## 3. 헤어 스타일 추천 및 이유 설명
<img width="1232" height="1096" alt="Image" src="https://github.com/user-attachments/assets/a97ae048-4575-4870-a8cd-4e945390d3d0" />


## 왜 만들었나요?

같은 얼굴형으로 분류되더라도 상안부와 하안부의 비율, 턱의 폭, 턱끝의 각도는 서로 다릅니다.
하나의 얼굴형 이름만으로는 이런 차이를 설명하기 어렵다고 생각했습니다.

그래서 “어떤 얼굴형인가?”보다 **어떤 특징이 있고, 그 특징에 맞춰 머리의 어느 부분을 조절할 수 있는가?**에 집중했습니다.
스타일을 일방적으로 결정하기보다, 사용자가 추천 근거를 이해하고 자신의 선호를 함께 전달할 수 있는 상담 도구를 만드는 것이 목표입니다.

## 현재 구현된 기능

| 영역 | 구현 내용 |
| --- | --- |
| 얼굴 분석 | MediaPipe 랜드마크 추출, Yaw·Pitch·Roll 기반 촬영 자세 확인, 얼굴 비율·턱·윤곽 측정 |
| 헤어라인 보정 | 피부·모발 경계 검출과 기하학적 추정, 사용자 위치 보정 |
| 결과 시각화 | 얼굴 특징별 측정 영역 표시, 특징 선택 컨트롤, 비율 바와 기준 데이터 분포 비교 |
| 추천 설명 | 윗머리·옆머리 볼륨, 이마 노출, 앞머리 길이·무게감, 가르마 비대칭, 컬 강도에 대한 규칙 기반 추천 |
| 상담 플로우 | 커트·펌 및 스타일을 정하지 못한 고객을 위한 분기형 질문, 공통 스타일링 질문 |
| 답변 처리 | 단일·복수선택, 직접 입력, 필수 입력 검증, 단독 선택 옵션, 경로 변경 시 후속 답변 정리 |
| 상담 공유 | 추천 요청사항과 고객 희망사항 구분, 추가 요청·참고 헤어사진, 공유 링크·QR |

현재 추천은 **얼굴 측정값과 기준 데이터 분포를 이용하는 규칙 기반 방식**입니다.
추천 카드에서 영향을 준 얼굴 특징과 이유를 확인할 수 있으며,
LLM 기반 문장 생성이나 헤어스타일 이미지 합성 기능은 사용하지 않습니다.

## 분석과 추천 방식

```text
얼굴 사진
  → 랜드마크 추출·촬영 자세 확인
  → 헤어라인 자동 추정·사용자 보정
  → 기하학적 특징 측정
  → 기준 데이터 분포와 비교
  → 얼굴 특징별 헤어 요소 조절 규칙
  → 요소별 기여도 통합
  → 추천 방향과 이유 표시
```

주요 측정 지표는 다음과 같습니다.

- 얼굴 세로 / 가로 비율
- 상안부 / 중안부 / 하안부 비율
- 턱 폭 / 광대 폭 비율
- 턱끝 각도와 좌우 하악각
- 턱·하악 윤곽의 국소 각도(Local Angle)

핵심 분석은 [분석 파이프라인](core/analysis_pipeline.py),
기준 데이터 비교는 [사용자 분석](analyze_user.py),
헤어 요소별 추천은 [추천 규칙](core/hair_rules_v3.py)에 분리되어 있습니다.

## 주요 설계와 문제 해결

### 1. 앞머리 경계와 실제 헤어라인 구분

헤어라인은 얼굴 세로 길이와 상안부 비율의 기준점이지만,
앞머리에 가려지거나 한쪽만 드러날 수 있습니다.
초기에는 중앙 영역의 모발 경계 중앙값을 사용해,
가르마·가일 스타일에서 앞머리 끝을 헤어라인으로 판단하는 문제가 있었습니다.

탐색 영역을 양쪽 눈 바깥쪽 랜드마크 사이로 넓히고,
피부에서 모발로 전환되는 경계 중 위쪽 15% 후보의 중앙값을 사용하도록 개선했습니다.
검출값이 없거나 기하학적 추정과 크게 다르면 추정값으로 대체하며,
사용자가 직접 보정할 수 있는 단계도 두었습니다.

이때 사용하는 계수와 임계값은 경험적으로 설정한 값이며, 정확도가 검증된 보편적 기준은 아닙니다.

자세한 설계와 한계는 [헤어라인 추정 기록](docs/hairline.md)에 정리했습니다.

### 2. 로컬과 Azure의 실행 환경 차이 해결

Azure 배포 과정에서 OpenCV의 GUI 의존성, NumPy·Pandas ABI 불일치,
MediaPipe 실행에 필요한 Linux 라이브러리 누락을 겪었습니다.
서버가 시작되더라도 실제 분석 요청에서 `libEGL.so.1`, `libGLESv2.so.2` 오류가 발생했습니다.

이를 해결하기 위해 Docker 이미지에 Python 패키지와 Linux 라이브러리를 함께 명시했습니다.
서버용 headless OpenCV를 사용하고 MediaPipe를 별도 설치하는 구성을 적용해,
실행 환경을 [Dockerfile](Dockerfile)에서 관리합니다.

원인별 대응은 [Azure 배포 트러블슈팅](docs/azure_deployment_troubleshooting.md)에 정리했습니다.

### 3. 질문 경로가 바뀌어도 이전 답변이 섞이지 않도록 설계

커트·펌 상담은 선택한 답변에 따라 다음 질문이 달라집니다.
이전 질문을 수정했을 때 더 이상 유효하지 않은 후속 답변이 남으면,
고객 희망사항에 잘못된 요청이 포함될 수 있습니다.

질문 구조는 [상담 플로우 JSON](backend/app/data/consultation_flow.json)으로 관리하고,
[공통 유틸리티](frontend/src/utils/consultationFlow.ts)에서 후속 답변과 직접 입력값을 정리합니다.
직접 입력은 해당 옵션이 선택된 경우에만 필수 검증에 포함하고,
‘특별히 없음’은 다른 항목과 함께 선택되지 않도록 처리합니다.

상담문은 현재 [상담문 생성 서비스](backend/app/services/consultation_flow_service.py)에서 조립합니다.
선택지 표시 문구와 상담문 표현을 분리하는 리팩토링은 다음 개선 과제입니다.

## 시스템 구성

```text
React · TypeScript · Vite / Azure Static Web Apps
                    │ HTTP
                    ▼
              FastAPI / Azure App Service
                    ├─ 얼굴 분석·추천
                    │    ├─ MediaPipe · OpenCV · NumPy
                    │    └─ 기준 측정 DB / SQLite
                    └─ 상담 생성·공유
                         ├─ 질문 트리 / JSON
                         ├─ 상담 저장 / SQLite
                         └─ 참고 헤어사진 / Azure Blob Storage
```

백엔드 API와 얼굴 분석 코어를 분리해 웹 요청 처리와 측정 로직을 각각 관리합니다.
기준 측정 DB와 공유 상담 저장 DB도 용도를 구분합니다.

| 구분 | 기술 |
| --- | --- |
| Frontend | React, TypeScript, Vite, Framer Motion |
| Backend | Python, FastAPI, Uvicorn |
| Computer Vision | MediaPipe, OpenCV, NumPy |
| Data | SQLite, Pandas |
| Infrastructure | Docker, GitHub Actions, Azure Static Web Apps, Azure Container Registry, Azure App Service, Azure Blob Storage |

### 배포

GitHub Actions에 프론트엔드와 백엔드 배포 워크플로가 구성되어 있습니다.

- **프론트엔드:** Vite 빌드 → Azure Static Web Apps
- **백엔드:** Docker 빌드 → Azure Container Registry → Azure App Service → API 응답 확인

백엔드 컨테이너는 시작 시 상담 DB 마이그레이션을 실행합니다.
운영 상담 데이터는 `APP_DB_PATH`를 영속 저장소 경로로 지정해 관리해야 합니다.

## 데이터와 검증

기준 측정 데이터 구축에는 [AI Hub 안면 데이터셋](https://aihub.or.kr/aihubdata/data/view.do?dataSetSn=71427)을 사용합니다.
[샘플 선별 로직](core/dataset_loader.py)은 남성, 동일 인물당 한 장,
GT Yaw·Pitch·Roll이 모두 0인 이미지를 선택합니다.

선별한 이미지를 동일한 측정 파이프라인으로 처리해 지표별 분포와 사용자 측정값을 비교합니다.
이 분포는 선택된 데이터셋에 대한 기준이며, 전체 남성 인구를 대표하는 기준이나 추천 정확도의 증거는 아닙니다.

헤어라인 검증을 위해 Streamlit 기반 [내부 라벨링 도구](tools/hairline_labeler.py)도 작성했습니다.
경계 후보·검출값·기하학적 추정값·최종 위치를 비교하고, 노출 상태와 수동 정답 위치를 기록하기 위한 도구입니다.
현재 웹 서비스와 별도이며, 실행 전 의존성과 import 경로를 확인해야 합니다.

상담 로직에는 경로 연결, 문장 생성, 직접 입력 검증, 선택 해제·경로 변경 시 답변 정리 테스트를 두었습니다.
이 테스트는 기능의 회귀를 확인하는 것이며 얼굴 분석·추천의 정확도 검증을 대신하지 않습니다.

## 로컬 실행

### 준비 사항

- Docker, Node.js 24 및 npm
- 아래 모델 파일과 기준 DB
- 참고 헤어사진 업로드·조회까지 사용할 경우 Azure Blob Storage 설정과 접근 권한

```text
models/face_landmarker.task
models/selfie_multiclass_256x256.tflite
data/face_analysis_v1_1.db
```

모델 파일은 저장소에 포함되어 있으며, 경로는
[config/settings.py](config/settings.py)에서 관리합니다.

기준 DB를 직접 구축하려면 데이터셋 경로와
[구축 스크립트](build_measurement_db.py)를 확인하세요.
현재 스크립트는 선별된 이미지 중 앞의 최대 3개만 처리하도록 설정되어 있습니다.

### Backend — Docker

저장소 루트에서 실행합니다.

```bash
docker build -t hedap-api .
docker run --rm -p 8000:8000 --mount type=volume,source=hedap-data,target=/app/storage -e APP_DB_PATH=/app/storage/app.db hedap-api
```

API 문서는 실행 후 `http://localhost:8000/docs`에서 확인할 수 있습니다.
위 명령은 상담 DB를 Docker 볼륨에 보관하지만 Azure 인증은 구성하지 않습니다.
참고 헤어사진 기능을 사용하려면 [Blob Storage 서비스](backend/app/services/blob_storage_service.py)의 계정·컨테이너 설정과
`DefaultAzureCredential`이 사용할 인증 수단을 별도로 준비해야 합니다.

Python 개발 환경에서 직접 실행하려면 Python 3.12를 기준으로
[의존성 목록](requirements.txt)과 Dockerfile의 설치 방식을 참고해 환경을 구성한 뒤 실행합니다.
Linux의 시스템 라이브러리와 MediaPipe·OpenCV 설치 주의사항은 배포 트러블슈팅 문서를 참고하세요.

```bash
python -m database.migrations.run
python -m uvicorn backend.app.main:app --reload
```

### Frontend

`frontend/.env.development.local`에 로컬 API 주소를 설정합니다.

```dotenv
VITE_API_URL=http://localhost:8000
```

별도 터미널에서 실행합니다.

```bash
cd frontend
npm ci
npm run dev
```

브라우저에서 `http://localhost:5173`에 접속합니다.
다른 포트를 사용한다면 백엔드의 허용 Origin 설정도 함께 확인하세요.

### 테스트·빌드

저장소 루트에서 상담 백엔드 테스트를 실행합니다.

```bash
python -m unittest discover -s test -p test_consultation_flow.py
```

프론트엔드 테스트·빌드는 `frontend/`에서 실행합니다.

```bash
node --test tests/consultationFlow.test.ts
npm run build
```

## 현재 한계와 다음 단계

- **측정 오차:** 촬영 각도, 조명, 앞머리 가림과 segmentation 결과에 따라 측정값이 달라질 수 있습니다.
- **추천 검증:** 남성 얼굴·헤어 요소를 중심으로 설계한 규칙입니다. 실제 만족도나 미용사 평가로 추천 효과를 검증해야 합니다.
- **문장 품질:** 선택지와 상담문이 일부 결합되어 있고, 자유 입력을 자연스럽게 연결하는 데 한계가 있습니다.
- **성능 측정:** 분석 성공률, 처리 시간, 헤어라인 보정 비율과 동시 요청 성능에 대한 정량 지표를 추가할 예정입니다.

다음 단계는 상담문 생성 구조 리팩토링, 실제 사용자·헤어 디자이너 피드백 수집,
측정·추천 기준 검증입니다.
이를 통해 개인용 헤어 분석과 디자이너용 상담 보조 중 어떤 사용 맥락에서 더 도움이 되는지 확인하려고 합니다.

## 저장소 구조

```text
backend/               FastAPI API·서비스·상담 질문 데이터
frontend/              React 웹 UI·상담 플로우 테스트
core/                  얼굴 측정·헤어라인 추정·추천 규칙
database/              SQLite 저장·조회·마이그레이션
config/                모델·기준 데이터 경로와 랜드마크 설정
models/                별도 준비하는 MediaPipe 모델
data/                  기준 측정 DB·로컬 상담 DB·검증 데이터
tools/                 측정 데이터 분석·내부 라벨링 도구
test/                  Python 테스트·분석 검증 스크립트
docs/                  알고리즘·배포 문제 해결 기록
analyze_user.py        사용자 측정값 비교·추천 조립
build_measurement_db.py 기준 측정 데이터 구축
```

## 개발 기록

- [CHANGELOG](CHANGELOG.md)
- [헤어라인 추정 설계와 개선](docs/hairline.md)
- [Azure·Docker 배포 트러블슈팅](docs/azure_deployment_troubleshooting.md)
