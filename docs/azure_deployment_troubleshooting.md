# Azure App Service 배포 트러블슈팅

이 문서는 `face_factor_analysis` FastAPI 백엔드를 Azure App Service에 배포하면서 발생한 문제와 해결 과정을 정리한 기록이다.

## 1. 최종 배포 구조

최종적으로는 Azure App Service의 built-in Python 런타임에 직접 의존성을 설치하는 방식 대신, Docker 이미지에 Python 패키지와 Linux 시스템 라이브러리를 함께 고정한 뒤 Azure Container Registry(ACR)를 통해 배포했다.

```text
Local development
→ Docker image build
→ Azure Container Registry
→ Azure App Service custom container
→ FastAPI / Uvicorn
```

현재 Docker 이미지는 Python 3.12 slim을 기반으로 하고, MediaPipe가 요구하는 `libegl1`, `libgles2`를 OS 패키지로 설치한다. Python 패키지는 `opencv-contrib-python-headless`를 명시적으로 설치하고, `mediapipe==1.0.1`은 `--no-deps`로 분리 설치한다.

## 2. 문제 1: OpenCV GUI 라이브러리 오류

### 증상

Azure Linux에서 서버 시작 시 다음 오류가 발생했다.

```text
ImportError: libxcb.so.1: cannot open shared object file: No such file or directory
```

### 원인

`mediapipe`를 일반적으로 설치하면 의존성으로 `opencv-contrib-python`이 설치된다. 이 패키지는 GUI/X11 계열 Linux 라이브러리를 요구할 수 있어 headless 서버 환경에서 문제가 발생했다.

### 해결

일반 OpenCV 대신 서버용 headless 패키지를 사용했다.

```text
opencv-contrib-python-headless==4.14.0.94
```

그리고 MediaPipe가 다시 일반 `opencv-contrib-python`을 설치하지 않도록 다음처럼 분리 설치했다.

```bash
python -m pip install opencv-contrib-python-headless==4.14.0.94
python -m pip install mediapipe==1.0.1 --no-deps
```

## 3. 문제 2: MediaPipe Python 런타임 의존성 누락

### 증상

`mediapipe==1.0.1`을 `--no-deps`로 설치한 이후 아래와 같은 오류가 순차적으로 발생했다.

```text
ModuleNotFoundError: No module named 'certifi'
ModuleNotFoundError: No module named 'matplotlib'
```

### 원인

`--no-deps`는 OpenCV만 제외하는 옵션이 아니라 MediaPipe의 모든 자동 의존성 설치를 중단한다. 따라서 필요한 런타임 패키지를 직접 제공해야 했다.

### 해결

MediaPipe의 wheel metadata와 로컬 환경을 기준으로 다음 의존성을 명시적으로 관리했다.

```text
absl-py==2.5.0
certifi==2026.7.22
flatbuffers==25.12.19
matplotlib==3.11.1
sounddevice==0.5.6
numpy==2.5.1
```

이 외에 `opencv-contrib-python-headless`를 별도로 설치하고 MediaPipe는 계속 `--no-deps`로 유지했다.

## 4. 문제 3: NumPy / Pandas ABI 불일치

### 증상

Azure에서 FastAPI 앱 import 중 다음 오류가 발생했다.

```text
ValueError: numpy.dtype size changed, may indicate binary incompatibility.
Expected 96 from C header, got 88 from PyObject
```

### 원인

배포 환경은 `numpy==2.5.1`, `pandas==2.1.1` 조합이었지만 로컬에서 실제 동작 중인 Pandas 버전은 `3.0.5`였다. C extension이 포함된 패키지들은 단순히 설치 여부뿐 아니라 ABI 호환성도 중요하다.

### 해결

로컬에서 검증된 버전 조합으로 통일했다.

```text
numpy==2.5.1
pandas==3.0.5
scipy==1.18.0
```

또한 GitHub Actions smoke test에서 NumPy, Pandas, SciPy를 함께 import하고 실제 연산까지 수행하도록 확장했다.

## 5. 문제 4: Azure 배포 패키지 경로 문제

### 증상

중간 단계에서 다음과 같은 오류가 발생했다.

```text
Could not find virtual environment directory /home/site/wwwroot/antenv
No module named uvicorn
```

### 원인

GitHub Actions에서 생성한 `.python_packages`가 배포 artifact에 포함되지 않거나 Azure 런타임의 Python path에 잡히지 않았다.

### 해결

GitHub Actions artifact 업로드 시 숨김 파일을 포함했다.

```yaml
include-hidden-files: true
```

그리고 built-in Python 배포를 사용하던 단계에서는 다음 환경변수를 사용했다.

```text
PYTHONPATH=/home/site/wwwroot/.python_packages/lib/site-packages
```

이 설정은 이후 Docker 기반 배포로 전환하면서 더 이상 핵심 의존성이 아니게 되었다.

## 6. 문제 5: MediaPipe native library의 Linux 시스템 의존성

### 증상

FastAPI 서버 자체는 정상 기동됐지만 `/measure` 호출 시 아래 오류가 발생했다.

```text
OSError: libEGL.so.1: cannot open shared object file: No such file or directory
```

### 원인 분석

Azure SSH/Kudu 환경에서 MediaPipe의 native `.so`를 `ldd`로 검사했다.

```bash
find /home/site/wwwroot/.python_packages/lib/site-packages/mediapipe \
  -name '*.so' \
  -exec sh -c 'echo "===== $1 ====="; ldd "$1" | grep "not found" || true' _ {} \;
```

그 결과 실제 누락된 라이브러리는 다음 두 개였다.

```text
libEGL.so.1 => not found
libGLESv2.so.2 => not found
```

MediaPipe Linux wheel의 native binary가 CPU 기반 실행에서도 이 soname들에 링크되어 있기 때문에, GPU를 사용하지 않아도 동적 로더 단계에서 실패할 수 있었다.

### 임시 검증

Azure 컨테이너에 직접 다음 패키지를 설치했다.

```bash
apt-get update
apt-get install -y libegl1 libgles2
```

설치 직후 `/measure` 요청이 `200 OK`로 성공했다. 따라서 문제의 직접 원인이 `libEGL.so.1`, `libGLESv2.so.2` 부재임을 확인했다.

## 7. 왜 Docker로 전환했는가

Azure built-in Python 컨테이너에 `apt-get install`을 직접 실행하는 방식은 현재 컨테이너의 writable layer를 수정하는 임시 해결책에 가깝다. 재배포, 재시작, 스케일 아웃, 플랫폼 이미지 교체 시 동일한 시스템 라이브러리가 항상 존재한다고 보장하기 어렵다.

따라서 Python 패키지뿐 아니라 OS 수준 의존성까지 같은 실행 환경에 고정하기 위해 Docker custom container로 전환했다.

현재 `Dockerfile`의 핵심은 다음과 같다.

```dockerfile
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libegl1 \
        libgles2 \
    && rm -rf /var/lib/apt/lists/*
```

그리고 OpenCV와 MediaPipe는 충돌을 막기 위해 별도로 설치한다.

```dockerfile
RUN python -m pip install \
    --only-binary=:all: \
    opencv-contrib-python-headless==4.14.0.94 \
    numpy==2.5.1 \
    scipy==1.18.0 \
    pandas==3.0.5 \
    fastapi==0.141.1 \
    uvicorn==0.52.4 \
    python-multipart==0.0.32 \
    absl-py==2.5.0 \
    certifi==2026.7.22 \
    flatbuffers==25.12.19 \
    matplotlib==3.11.1 \
    sounddevice==0.5.6

RUN python -m pip install \
    --only-binary=:all: \
    mediapipe==1.0.1 \
    --no-deps
```

`--only-binary=:all:`은 CI/배포 환경에서 예상치 못한 소스 빌드 fallback을 방지하고 Linux wheel 존재 여부를 즉시 확인하기 위해 사용했다.

## 8. Docker 로컬 검증

Azure에 다시 올리기 전에 로컬 Windows에서 Docker Desktop + WSL2를 사용해 Linux 컨테이너를 직접 실행했다.

```bash
docker build -t face-factor-api .
docker run --name face-factor-api-container -p 8000:8000 face-factor-api
```

검증 결과:

```text
GET  /docs     → 정상
POST /measure  → 200 OK
POST /analyze  → 200 OK
```

즉 Azure로 보내기 전에 동일한 Linux 기반 컨테이너에서 MediaPipe, DB, 분석 로직, FastAPI 응답이 모두 정상 동작함을 확인했다.

## 9. Azure Container Registry와 App Service 연결

Docker 이미지를 Azure Container Registry에 업로드했다.

```text
Registry: facefactoracracr.azurecr.io
Image:    face-factor-api:latest
```

로컬 이미지에 ACR 태그를 붙인 뒤 push했다.

```bash
docker tag face-factor-api:latest facefactoracracr.azurecr.io/face-factor-api:latest
az acr login --name facefactoracracr
docker push facefactoracracr.azurecr.io/face-factor-api:latest
```

App Service에는 system-assigned managed identity를 생성하고 ACR에 `AcrPull` 권한을 부여했다.

```text
App Service identity
→ AcrPull role
→ Azure Container Registry
```

이후 App Service가 다음 이미지를 사용하도록 연결했다.

```text
facefactoracracr.azurecr.io/face-factor-api:latest
```

## 10. 문제 6: App Service와 컨테이너 포트 불일치

### 증상

App Service 상태는 `Running`이고 Docker 이미지 연결도 정상으로 보였지만 `/docs`에 접속되지 않았다.

### 원인

Docker 컨테이너의 Uvicorn은 8000번 포트에서 실행되고 있었다.

```dockerfile
CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Azure App Service가 custom container에서 사용할 포트를 알 수 있도록 별도 설정이 필요했다.

### 해결

App Service 환경변수에 다음 값을 추가했다.

```text
WEBSITES_PORT=8000
```

설정 반영 후 컨테이너가 정상 시작되었고 `/docs`, `/measure`, `/analyze` 모두 외부 Azure URL에서 정상 동작했다.

## 11. 최종적으로 배운 점

이번 배포에서 가장 크게 확인한 점은 "로컬에서 Python 코드가 동작한다"와 "Linux 운영 환경에서 서비스가 재현 가능하게 실행된다"는 서로 다른 문제라는 것이다.

특히 다음 세 가지 계층을 분리해서 확인하는 것이 중요했다.

```text
Python package dependency
→ certifi, matplotlib, pandas 등

Binary / ABI compatibility
→ numpy, pandas, scipy, OpenCV 등

OS shared library dependency
→ libEGL.so.1, libGLESv2.so.2 등
```

문제를 해결할 때도 단순히 오류 메시지에 나온 패키지를 하나씩 추가하기보다 다음 순서가 효과적이었다.

```text
1. traceback으로 실패 지점 확인
2. Python metadata와 실제 로컬 버전 비교
3. native .so는 ldd로 시스템 의존성 확인
4. 임시 설치로 원인 검증
5. Dockerfile에 해결책을 고정해 재현 가능한 환경으로 전환
6. 로컬 Docker에서 실제 API 테스트
7. Azure ACR/App Service에 동일 이미지 배포
```

## 12. 최종 상태

```text
Azure App Service      정상
Docker custom container 정상
FastAPI /docs           정상
POST /measure           정상
POST /analyze           정상
MediaPipe               정상
OpenCV headless         정상
ACR image pull          정상
```

이번 트러블슈팅의 핵심 해결책은 MediaPipe의 Linux native dependency를 확인한 뒤 `libegl1`, `libgles2`를 Docker 이미지에 명시적으로 포함하고, Python 패키지와 OS 의존성을 하나의 재현 가능한 컨테이너 환경으로 고정한 것이다.
