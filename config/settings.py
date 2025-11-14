"""Application settings and configuration."""
from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM API Keys
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    groq_api_key: str = ""
    deepinfra_api_key: str = ""

    # Default LLM Provider
    default_llm_provider: str = "claude"

    # Model Names
    claude_model: str = "claude-3-5-sonnet-20241022"
    openai_model: str = "gpt-4-turbo-preview"
    groq_model: str = "mixtral-8x7b-32768"
    deepinfra_model: str = "meta-llama/Meta-Llama-3.1-70B-Instruct"

    # RAG Settings
    vector_store_path: Path = Path("./data/vectorstore")
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # Application Settings
    max_file_size: int = 10485760  # 10MB
    supported_file_extensions: str = ".py,.js,.ts,.jsx,.tsx,.java,.cpp,.c,.go,.rs,.md,.txt"
    max_context_files: int = 20

    # Web Search
    enable_web_search: bool = True
    max_search_results: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        return [ext.strip() for ext in self.supported_file_extensions.split(",")]

    def get_api_key(self, provider: str) -> str:
        """Get API key for specified provider."""
        key_map = {
            "claude": self.anthropic_api_key,
            "openai": self.openai_api_key,
            "groq": self.groq_api_key,
            "deepinfra": self.deepinfra_api_key,
        }
        return key_map.get(provider, "")

    def get_model_name(self, provider: str) -> str:
        """Get model name for specified provider."""
        model_map = {
            "claude": self.claude_model,
            "openai": self.openai_model,
            "groq": self.groq_model,
            "deepinfra": self.deepinfra_model,
        }
        return model_map.get(provider, "")


# Global settings instance
settings = Settings()
