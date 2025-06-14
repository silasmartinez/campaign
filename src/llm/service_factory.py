from typing import Optional, Dict, Any
from .base import BaseLLMService
from .ollama_service import OllamaService
from .multi_model_service import MultiModelOllamaService
from ..config.settings import Settings


class LLMServiceFactory:
    """Factory for creating LLM service instances"""
    
    @staticmethod
    def create_service(settings: Settings) -> Optional[BaseLLMService]:
        """Create appropriate LLM service based on configuration"""
        
        # Check if LLM integration is enabled
        if not settings.features.beta.get("llm_integration", False):
            return None
        
        # Try local LLM first (Ollama with multi-model support)
        if settings.llm.local.enabled:
            service = MultiModelOllamaService(
                settings=settings,
                timeout=settings.llm.local.timeout,
                temperature=settings.llm.local.temperature,
                max_tokens=settings.llm.local.max_tokens
            )
            
            if service.is_available():
                return service
            else:
                print(f"Warning: Ollama service not available at {settings.llm.local.base_url}")
        
        # TODO: Add cloud LLM fallback (OpenAI, Anthropic)
        # if settings.llm.cloud.openai.enabled and settings.security.api_keys.openai:
        #     return OpenAIService(...)
        
        return None
    
    @staticmethod
    def get_available_models(settings: Settings) -> Dict[str, list]:
        """Get list of available models for each provider"""
        available = {}
        
        # Check Ollama models
        if settings.llm.local.enabled:
            try:
                service = OllamaService(
                    model_name=settings.llm.local.model,
                    host=settings.llm.local.base_url
                )
                if service.is_available():
                    available["ollama"] = service.list_models()
            except Exception as e:
                print(f"Error checking Ollama models: {e}")
        
        # TODO: Add cloud provider model lists
        
        return available