"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """AgentOS AI Core settings."""

    # LLM API Keys
    openai_api_key: str = ""
    deepseek_api_key: str = ""
    tavily_api_key: str = ""

    # DeepSeek
    deepseek_base_url: str = "https://api.deepseek.com"

    # Ollama (local)
    ollama_base_url: str = "http://localhost:11434"
    ollama_default_model: str = "qwen2.5:7b"

    # Model defaults
    default_model_provider: str = "deepseek"
    default_model_name: str = "deepseek-chat"
    complex_model_name: str = "deepseek-chat"  # DeepSeek Chat is good enough

    # Agent defaults
    default_max_steps: int = 10
    default_timeout: int = 120  # seconds

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = {"env_file": "../../.env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
