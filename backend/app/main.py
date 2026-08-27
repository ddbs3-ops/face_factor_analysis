from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routes.analyze import router as analyze_router

app = FastAPI()

ALLOWED_ORIGINS = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(analyze_router)


@app.get("/")
def root():
    return {"message": "Hello backend!"}