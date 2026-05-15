from groq import Groq

from app.core.config import settings


class LLMService:
    def __init__(self):
        self.client = Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None

    def complete(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        if not self.client:
            return self._fallback_response(user_prompt)

        response = self.client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=700,
        )
        return response.choices[0].message.content or ""

    @staticmethod
    def _fallback_response(user_prompt: str) -> str:
        return (
            "Demo response: I can answer using uploaded business documents, capture leads, "
            "and trigger follow-up workflows. Add GROQ_API_KEY in .env for live AI answers.\n\n"
            f"User request received: {user_prompt[:300]}"
        )


llm_service = LLMService()
