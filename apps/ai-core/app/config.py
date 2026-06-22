"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """AgentOS AI Core settings."""

    # LLM API Keys
    openai_api_key: str = ""
    tavily_api_key: str = ""

    # Ollama (local)
    ollama_base_url: str = "http://localhost:11434"
    ollama_default_model: str = "qwen2.5:7b"

    # Model defaults
    default_model_provider: str = "openai"
    default_model_name: str = "gpt-4o-mini"  # cheap for dev
    complex_model_name: str = "gpt-4o"        # premium for complex tasks

    # Agent defaults
    default_max_steps: int = 10
    default_timeout: int = 120  # seconds

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = {"env_file": "../../.env", "env_file_encoding": "utf-8"}


settings = Settings()
