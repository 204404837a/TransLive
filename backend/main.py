from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import settings
from translator import LibreTranslateClient, TranslationError

app = FastAPI(
    title="TransLive API",
    description="实时中英互译系统后端服务",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

translator = LibreTranslateClient()


class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, description="待翻译文本")
    source: Literal["zh", "en", "auto"] = "auto"
    target: Literal["zh", "en"] = "en"


class TranslateResponse(BaseModel):
    translated_text: str
    source_lang: str
    target_lang: str
    detected_language: str | None = None
    latency_ms: float
    engine: str


class DetectRequest(BaseModel):
    text: str = Field(..., min_length=1)


@app.get("/health")
async def health():
    try:
        engine_status = await translator.health_check()
        return {"status": "ok", "backend": "translive", "engine_status": engine_status}
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Translation engine unavailable: {exc}",
        ) from exc


@app.post("/api/translate", response_model=TranslateResponse)
async def translate(request: TranslateRequest):
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    if len(text) > settings.max_text_length:
        raise HTTPException(
            status_code=400,
            detail=f"Text exceeds maximum length of {settings.max_text_length} characters",
        )

    source = request.source
    target = request.target

    if source != "auto" and source == target:
        raise HTTPException(status_code=400, detail="Source and target language must differ")

    try:
        result = await translator.translate(text=text, source=source, target=target)
        return TranslateResponse(**result)
    except TranslationError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Translation failed: {exc}") from exc


@app.post("/api/detect")
async def detect(request: DetectRequest):
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        detections = await translator.detect_language(text)
        return {"detections": detections}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Detection failed: {exc}") from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.backend_host, port=settings.backend_port, reload=True)
