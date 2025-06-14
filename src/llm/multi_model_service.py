from typing import Dict, Any, Optional
from .base import BaseLLMService, LLMResponse
from .ollama_service import OllamaService
from ..config.settings import Settings


class MultiModelOllamaService(BaseLLMService):
    """Multi-model Ollama service with task-specific model selection"""
    
    def __init__(self, settings: Settings, **kwargs):
        # Use default model for base class
        default_model = settings.llm.local.models.get("default", "llama3.1:8b")
        super().__init__(default_model, **kwargs)
        
        self.settings = settings
        self.host = settings.llm.local.base_url
        self.models_config = settings.llm.local.models
        self.fallback_models = settings.llm.local.fallback_models
        
        # Single Ollama client instance
        self.ollama_service = OllamaService(
            model_name=default_model,
            host=self.host,
            **kwargs
        )
    
    def get_model_for_task(self, intent: str = "general") -> str:
        """Get the optimal model for a specific task/intent"""
        
        # Intent to task mapping
        task_mapping = {
            "general": "general",
            "session_prep": "analysis", 
            "npc_info": "creative",
            "lore_expansion": "synthesis",
            "encounter_design": "creative",
            "session_summary": "analysis"
        }
        
        task = task_mapping.get(intent, "general")
        preferred_model = self.models_config.get(task, self.models_config["default"])
        
        # Check if preferred model is available
        if self.ollama_service.is_model_available(preferred_model):
            return preferred_model
        
        # Fall back through fallback chain
        for fallback in self.fallback_models:
            if self.ollama_service.is_model_available(fallback):
                print(f"⚠️  Preferred model '{preferred_model}' not available, using '{fallback}'")
                return fallback
        
        # Final fallback to any available model
        available = self.ollama_service.get_available_models()
        if available:
            print(f"⚠️  Using first available model: '{available[0]}'")
            return available[0]
        
        raise RuntimeError("No Ollama models available")
    
    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        intent: str = "general"
    ) -> LLMResponse:
        """Generate text response with task-specific model selection"""
        
        model = self.get_model_for_task(intent)
        
        # Update the ollama service model temporarily
        original_model = self.ollama_service.model_name
        self.ollama_service.model_name = model
        
        try:
            response = await self.ollama_service.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Update response metadata with actual model used
            if response.metadata is None:
                response.metadata = {}
            response.metadata["actual_model"] = model
            response.metadata["intent"] = intent
            response.model = model
            
            return response
            
        finally:
            # Restore original model
            self.ollama_service.model_name = original_model
    
    async def generate_with_context(
        self,
        prompt: str,
        context_documents: list[str],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        intent: str = "general"
    ) -> LLMResponse:
        """Generate response with RAG context using optimal model"""
        
        # Use rag_qa task for context-based generation
        rag_intent = "rag_qa" if intent == "general" else intent
        model = self.get_model_for_task(rag_intent)
        
        # Update the ollama service model temporarily
        original_model = self.ollama_service.model_name
        self.ollama_service.model_name = model
        
        try:
            response = await self.ollama_service.generate_with_context(
                prompt=prompt,
                context_documents=context_documents,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Update response metadata
            if response.metadata is None:
                response.metadata = {}
            response.metadata["actual_model"] = model
            response.metadata["intent"] = intent
            response.metadata["task_type"] = "rag"
            response.model = model
            
            return response
            
        finally:
            # Restore original model
            self.ollama_service.model_name = original_model
    
    def is_available(self) -> bool:
        """Check if the service is available"""
        return self.ollama_service.is_available()
    
    def get_available_models(self) -> list[str]:
        """Get list of available models"""
        return self.ollama_service.get_available_models()
    
    def get_task_model_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all task-specific models"""
        status = {}
        available_models = self.ollama_service.get_available_models()
        
        for task, model in self.models_config.items():
            status[task] = {
                "preferred_model": model,
                "available": model in available_models,
                "actual_model": self.get_model_for_task(task) if available_models else None
            }
        
        return status
    
    def suggest_missing_models(self) -> list[str]:
        """Suggest models to pull for optimal performance"""
        available = self.ollama_service.get_available_models()
        configured = set(self.models_config.values())
        missing = []
        
        for model in configured:
            if model not in available:
                missing.append(model)
        
        return missing