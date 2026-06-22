import time
from typing import Any

import httpx

from config import settings


class TranslationError(Exception):
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


class LibreTranslateClient:
    def __init__(self, base_url: str | None = None, timeout: float | None = None):
        self.base_url = (base_url or settings.libretranslate_url).rstrip("/")
        self.timeout = timeout or settings.request_timeout

    async def health_check(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            started = time.perf_counter()
            response = await client.get(f"{self.base_url}/languages")
            latency_ms = round((time.perf_counter() - started) * 1000, 2)
            response.raise_for_status()
            languages = response.json()
            return {
                "status": "ok",
                "engine": "libretranslate",
                "base_url": self.base_url,
                "supported_languages": len(languages),
                "latency_ms": latency_ms,
            }

    async def detect_language(self, text: str) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/detect",
                json={"q": text},
            )
            response.raise_for_status()
            return response.json()

    async def translate(
        self,
        text: str,
        source: str,
        target: str,
    ) -> dict[str, Any]:
        payload = {
            "q": text,
            "source": source,
            "target": target,
            "format": "text",
        }

        started = time.perf_counter()
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.base_url}/translate", json=payload)

        latency_ms = round((time.perf_counter() - started) * 1000, 2)

        if response.status_code >= 400:
            detail = response.text[:300]
            raise TranslationError(
                f"Translation engine error ({response.status_code}): {detail}",
                status_code=502,
            )

        data = response.json()
        translated_text = data.get("translatedText", "")

        detected_language = None
        if source == "auto":
            detections = await self.detect_language(text)
            if detections:
                detected_language = detections[0].get("language")

        return {
            "translated_text": translated_text,
            "source_lang": source,
            "target_lang": target,
            "detected_language": detected_language,
            "latency_ms": latency_ms,
            "engine": "libretranslate",
        }
