from __future__ import annotations

import httpx

from backend.app.core.config import settings


class DeepSeekClient:
    def __init__(self) -> None:
        self._api_key = settings.DEEPSEEK_API_KEY
        self._base = settings.DEEPSEEK_API_BASE.rstrip("/")
        self._model = settings.DEEPSEEK_MODEL

    async def generate_warning_summary(self, anonymous_student_id: str, reasons: list[str]) -> str:
        if not self._api_key:
            return f"Student {anonymous_student_id}: monitor learning status. Reasons: {', '.join(reasons)}."

        payload = {
            "model": self._model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an education analytics assistant. Never output sensitive personal data.",
                },
                {
                    "role": "user",
                    "content": (
                        f"Student ID: {anonymous_student_id}. "
                        f"Warning reasons: {', '.join(reasons)}. "
                        "Generate a concise learning-risk analysis and actionable guidance in Chinese."
                    ),
                },
            ],
            "temperature": 0.3,
        }

        headers = {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(f"{self._base}/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        return data["choices"][0]["message"]["content"].strip()
