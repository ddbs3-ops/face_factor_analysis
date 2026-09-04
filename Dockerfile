FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libegl1 \
        libgles2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN python -m pip install --upgrade pip

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
    sounddevice==0.5.6 \
    azure-storage-blob==12.30.1 \
    azure-identity==1.25.3

RUN python -m pip install \
    --only-binary=:all: \
    mediapipe==1.0.1 \
    --no-deps

ENV MPLBACKEND=Agg

CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]