from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Response from LLM with metadata"""
    content: str
    model: str
    tokens_used: Optional[int] = None
    metadata: Dict[str, Any] = None


class BaseLLMService(ABC):
    """Abstract base class for LLM services"""
    
    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.config = kwargs
    
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """Generate text response from prompt"""
        pass
    
    @abstractmethod
    async def generate_with_context(
        self,
        prompt: str,
        context_documents: list[str],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """Generate response with RAG context"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM service is available"""
        pass