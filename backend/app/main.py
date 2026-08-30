from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routes.analyze import router as analyze_router
from backend.app.routes.consultation import router as consultation_router

app = FastAPI()

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://icy-beach-065dc0000.7.azurestaticapps.net",
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