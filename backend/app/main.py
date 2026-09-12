from contextlib import asynccontextmanager, ExitStack

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routes.analyze import router as analyze_router
from backend.app.routes.consultation import router as consultation_router
from database.create_consultation_tables import create_consultation_tables

from core.mediapipe_tasks import (
    create_face_landmarker,
    create_selfie_segmenter,
)
from config.settings import (
    FACE_LANDMARKER_MODEL_PATH,
    SELFIE_MODEL_PATH,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    with ExitStack() as stack:
        face_landmarker = create_face_landmarker(
            FACE_LANDMARKER_MODEL_PATH
        )
        stack.callback(face_landmarker.close)

        selfie_segmenter = create_selfie_segmenter(
            SELFIE_MODEL_PATH
        )
        stack.callback(selfie_segmenter.close)

        app.state.face_landmarker = face_landmarker
        app.state.selfie_segmenter = selfie_segmenter

        yield


app = FastAPI(lifespan=lifespan)

create_consultation_tables()

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://icy-beach-065dc0000.7.azurestaticapps.net",
    "https://hedap.kr",
    "https://www.hedap.kr",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(analyze_router)
app.include_router(consultation_router)

@app.get("/")
def root():
    return {
        "service": "Face Factor Analysis API",
        "version": "0.1.0",
        "status": "running",
    }
