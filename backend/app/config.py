import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    coder_model: str = Field(default="openai/gpt-oss-120b", alias="CODER_MODEL")
    critic_model: str = Field(default="openai/gpt-oss-20b", alias="CRITIC_MODEL")

    langfuse_enabled: bool = Field(default=False, alias="LANGFUSE_ENABLED")
    langfuse_public_key: str = Field(default="", alias="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: str = Field(default="", alias="LANGFUSE_SECRET_KEY")
    langfuse_host: str = Field(default="https://cloud.langfuse.com", alias="LANGFUSE_HOST")

    database_url: str = Field(default="sqlite+aiosqlite:///./data/repair.db", alias="DATABASE_URL")

    max_attempts: int = Field(default=3, alias="MAX_ATTEMPTS")
    sandbox_timeout_seconds: int = Field(default=30, alias="SANDBOX_TIMEOUT_SECONDS")
    sandbox_memory_mb: int = Field(default=512, alias="SANDBOX_MEMORY_MB")
    sandbox_cpu_limit: float = Field(default=1.0, alias="SANDBOX_CPU_LIMIT")
    use_docker_sandbox: str = Field(default="auto", alias="USE_DOCKER_SANDBOX")

    mock_llm: bool = Field(default=False, alias="MOCK_LLM")

    backend_host: str = Field(default="0.0.0.0", alias="BACKEND_HOST")
    backend_port: int = Field(default=8000, alias="BACKEND_PORT")
    frontend_port: int = Field(default=5173, alias="FRONTEND_PORT")

    workspace_root: str = str(PROJECT_ROOT / "workspaces")
    data_dir: str = str(PROJECT_ROOT / "data")

    class Config:
        env_file = str(PROJECT_ROOT / ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()

# Ensure data and workspace directories exist
os.makedirs(settings.data_dir, exist_ok=True)
os.makedirs(settings.workspace_root, exist_ok=True)
