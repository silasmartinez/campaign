"""
Configuration management for Campaign Assistant.
Implements 12-factor app principles with environment-aware YAML configuration.
"""

import os
import logging
import logging.config
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field

import yaml
from pydantic import BaseModel, Field, validator


class AppConfig(BaseModel):
    """Application configuration."""
    name: str = "Campaign Assistant"
    version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"


class VectorDBConfig(BaseModel):
    """Vector database configuration."""
    provider: str = "chromadb"
    path: str = "./data/chroma_db"
    collection_name: str = "campaign_documents"


class FileStorageConfig(BaseModel):
    """File storage configuration."""
    data_dir: str = "./data"
    upload_dir: str = "./data/uploads"
    processed_dir: str = "./data/processed"
    max_file_size_mb: int = 50


class StorageConfig(BaseModel):
    """Storage configuration."""
    vector_db: VectorDBConfig = Field(default_factory=VectorDBConfig)
    files: FileStorageConfig = Field(default_factory=FileStorageConfig)


class ChunkingConfig(BaseModel):
    """Document chunking configuration."""
    chunk_size: int = 1000
    chunk_overlap: int = 200


class ProcessingConfig(BaseModel):
    """Document processing configuration."""
    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)
    supported_formats: list[str] = [".pdf", ".md", ".markdown", ".txt"]
    classification: dict[str, Any] = {"enabled": True, "confidence_threshold": 0.7}


class EmbeddingModelConfig(BaseModel):
    """Embedding model configuration."""
    provider: str = "sentence_transformers"
    name: str = "all-MiniLM-L6-v2"
    cache_dir: str = "./data/models"


class EmbeddingsConfig(BaseModel):
    """Embeddings configuration."""
    model: EmbeddingModelConfig = Field(default_factory=EmbeddingModelConfig)
    alternatives: list[dict[str, str]] = []


class SearchConfig(BaseModel):
    """Search configuration."""
    default_max_results: int = 5
    similarity_threshold: float = 0.3
    enable_intent_classification: bool = True
    enable_context_boosting: bool = True


class QueryConfig(BaseModel):
    """Query processing configuration."""
    max_query_length: int = 1000
    enable_query_expansion: bool = False
    enable_spell_correction: bool = False


class RetrievalConfig(BaseModel):
    """Retrieval configuration."""
    search: SearchConfig = Field(default_factory=SearchConfig)
    query: QueryConfig = Field(default_factory=QueryConfig)


class LocalLLMConfig(BaseModel):
    """Local LLM configuration."""
    enabled: bool = True
    provider: str = "ollama"
    base_url: str = "http://localhost:11434"
    timeout: int = 30
    temperature: float = 0.7
    max_tokens: Optional[int] = 2000
    
    # Task-specific model selection (loaded from YAML config)
    models: Dict[str, str] = Field(default_factory=lambda: {
        "default": "llama3.1:8b",
        "rag_qa": "llama3.1:8b",
        "creative": "mistral:7b",
        "analysis": "llama3.1:8b",
        "synthesis": "mistral-nemo:12b",
        "general": "llama3.1:8b"
    })
    
    # Model fallback chain (loaded from YAML config)
    fallback_models: list[str] = Field(default_factory=lambda: [
        "llama3.1:8b",
        "mistral:7b",
        "gemma2:9b",
        "llama3.2:3b"
    ])


class OpenAIConfig(BaseModel):
    """OpenAI configuration."""
    enabled: bool = False
    model: str = "gpt-4o-mini"
    max_tokens: int = 2000
    temperature: float = 0.7


class AnthropicConfig(BaseModel):
    """Anthropic configuration."""
    enabled: bool = False
    model: str = "claude-3-haiku-20240307"
    max_tokens: int = 2000
    temperature: float = 0.7


class CloudLLMConfig(BaseModel):
    """Cloud LLM configuration."""
    openai: OpenAIConfig = Field(default_factory=OpenAIConfig)
    anthropic: AnthropicConfig = Field(default_factory=AnthropicConfig)


class LLMConfig(BaseModel):
    """LLM configuration."""
    local: LocalLLMConfig = Field(default_factory=LocalLLMConfig)
    cloud: CloudLLMConfig = Field(default_factory=CloudLLMConfig)


class APIConfig(BaseModel):
    """API server configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    reload: bool = False


class CORSConfig(BaseModel):
    """CORS configuration."""
    enabled: bool = True
    origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]


class APIKeysConfig(BaseModel):
    """API keys configuration."""
    openai: Optional[str] = None
    anthropic: Optional[str] = None


class SecurityConfig(BaseModel):
    """Security configuration."""
    api_keys: APIKeysConfig = Field(default_factory=APIKeysConfig)
    cors: CORSConfig = Field(default_factory=CORSConfig)


class FeatureFlagsConfig(BaseModel):
    """Feature flags configuration."""
    experimental: dict[str, bool] = {"enabled": False}
    beta: dict[str, bool] = {
        "multi_campaign_support": False,
        "web_interface": False,
        "llm_integration": True
    }
    alpha: dict[str, bool] = {
        "advanced_analytics": False,
        "collaborative_features": False
    }


class Settings(BaseModel):
    """Main settings class that encompasses all configuration."""
    
    app: AppConfig = Field(default_factory=AppConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    embeddings: EmbeddingsConfig = Field(default_factory=EmbeddingsConfig)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    features: FeatureFlagsConfig = Field(default_factory=FeatureFlagsConfig)
    logging: dict[str, Any] = {}
    
    @validator('*', pre=True)
    def resolve_env_vars(cls, v):
        """Resolve environment variables in string values."""
        if isinstance(v, str) and v.startswith('${') and v.endswith('}'):
            env_var = v[2:-1]
            default_val = None
            
            # Handle ${VAR:default} syntax
            if ':' in env_var:
                env_var, default_val = env_var.split(':', 1)
            
            return os.getenv(env_var, default_val)
        return v
    
    def create_directories(self) -> None:
        """Create necessary directories based on configuration."""
        dirs_to_create = [
            self.storage.files.data_dir,
            self.storage.files.upload_dir,
            self.storage.files.processed_dir,
            self.embeddings.model.cache_dir,
            Path(self.storage.vector_db.path).parent,
        ]
        
        # Create logs directory if file logging is configured
        if self.logging and 'handlers' in self.logging:
            for handler_config in self.logging['handlers'].values():
                if isinstance(handler_config, dict) and 'filename' in handler_config:
                    log_file = Path(handler_config['filename'])
                    dirs_to_create.append(str(log_file.parent))
        
        for dir_path in dirs_to_create:
            Path(dir_path).mkdir(parents=True, exist_ok=True)


class ConfigManager:
    """Manages configuration loading and environment handling."""
    
    def __init__(self):
        self._settings: Optional[Settings] = None
        self._environment = self._detect_environment()
        
    def _detect_environment(self) -> str:
        """Detect the current environment from various sources."""
        # 1. Check explicit environment variable
        env = os.getenv('CAMPAIGN_ENV', '').lower()
        if env in ['development', 'production', 'test']:
            return env
            
        # 2. Check common CI/deployment indicators
        if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
            return 'test'
        elif os.getenv('HEROKU_APP_NAME') or os.getenv('RAILWAY_ENVIRONMENT'):
            return 'production'
        elif os.getenv('DEBUG') == 'true':
            return 'development'
            
        # 3. Default based on common development indicators
        if any(os.path.exists(f) for f in ['.git', 'pyproject.toml', 'main.py']):
            return 'development'
            
        return 'production'
    
    def _load_yaml_config(self, file_path: Path) -> dict[str, Any]:
        """Load configuration from a YAML file."""
        if not file_path.exists():
            return {}
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise RuntimeError(f"Error parsing YAML config {file_path}: {e}")
        except Exception as e:
            raise RuntimeError(f"Error loading config {file_path}: {e}")
    
    def _merge_configs(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """Recursively merge configuration dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
                
        return result
    
    def _load_environment_secrets(self, config: dict[str, Any]) -> dict[str, Any]:
        """Load sensitive configuration from environment variables."""
        # API Keys
        if 'security' not in config:
            config['security'] = {}
        if 'api_keys' not in config['security']:
            config['security']['api_keys'] = {}
            
        # Load API keys from environment
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            config['security']['api_keys']['openai'] = openai_key
            
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_key:
            config['security']['api_keys']['anthropic'] = anthropic_key
            
        # Database URLs and other secrets
        db_url = os.getenv('DATABASE_URL')
        if db_url:
            if 'storage' not in config:
                config['storage'] = {}
            config['storage']['database_url'] = db_url
            
        return config
    
    def load_settings(self) -> Settings:
        """Load and return the application settings."""
        if self._settings is not None:
            return self._settings
            
        config_dir = Path(__file__).parent.parent.parent / 'config'
        
        # Load base configuration
        base_config = self._load_yaml_config(config_dir / 'default.yaml')
        
        # Load environment-specific overrides
        env_config = self._load_yaml_config(config_dir / f'{self._environment}.yaml')
        
        # Merge configurations
        merged_config = self._merge_configs(base_config, env_config)
        
        # Load secrets from environment
        merged_config = self._load_environment_secrets(merged_config)
        
        # Create settings instance
        self._settings = Settings(**merged_config)
        
        # Create required directories
        self._settings.create_directories()
        
        # Configure logging
        if self._settings.logging:
            logging.config.dictConfig(self._settings.logging)
        
        return self._settings
    
    @property
    def environment(self) -> str:
        """Get the current environment."""
        return self._environment
    
    def reload(self) -> Settings:
        """Force reload of settings."""
        self._settings = None
        return self.load_settings()


# Global configuration manager instance
config_manager = ConfigManager()

def get_settings() -> Settings:
    """Get the current application settings."""
    return config_manager.load_settings()

def get_environment() -> str:
    """Get the current environment."""
    return config_manager.environment