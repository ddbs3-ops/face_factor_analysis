from fastapi import FastAPI

from backend.app.api.analyze import router as analyze_router


app = FastAPI()

app.include_router(analyze_router)


@app.get("/")
def root():
    return {"message": "Hello FastAPI"}