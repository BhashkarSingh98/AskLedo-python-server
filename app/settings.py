from pathlib import Path
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        extra="ignore",
    )

    database_url: str = (
        "postgresql://searchmakesolution:searchmakesolution@localhost:5433/searchmakesolution"
    )

    llm_provider: Literal["vllm", "gemini"] = "vllm"
    llm_timeout_seconds: float = 60
    vllm_base_url: str = "http://localhost:8001/v1"
    vllm_model: str = "Qwen/Qwen2.5-7B-Instruct"
    vllm_api_key: str = ""
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash"

    routing_interval_seconds: float = 60
    routing_delay_seconds: int = 60
    routing_top_solutioners: int = 5

    @model_validator(mode="after")
    def require_gemini_key(self) -> "Settings":
        if self.llm_provider == "gemini" and not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required when LLM_PROVIDER=gemini")
        return self


settings = Settings()
