import asyncio
from typing import Dict, Any, Optional
import ollama
from .base import BaseLLMService, LLMResponse


class OllamaService(BaseLLMService):
    """Ollama local LLM service implementation"""
    
    def __init__(self, model_name: str = "llama2", host: str = "localhost:11434", **kwargs):
        super().__init__(model_name, **kwargs)
        self.host = host
        self.client = ollama.Client(host=host)
        self._available_models = None
    
    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """Generate text response from prompt"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        options = {"temperature": temperature}
        if max_tokens:
            options["num_predict"] = max_tokens
        
        try:
            # Run in thread pool since ollama.chat is synchronous
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.chat(
                    model=self.model_name,
                    messages=messages,
                    options=options
                )
            )
            
            return LLMResponse(
                content=response["message"]["content"],
                model=self.model_name,
                tokens_used=response.get("eval_count"),
                metadata={
                    "total_duration": response.get("total_duration"),
                    "load_duration": response.get("load_duration"),
                    "prompt_eval_count": response.get("prompt_eval_count"),
                    "eval_count": response.get("eval_count")
                }
            )
        except Exception as e:
            raise RuntimeError(f"Ollama generation failed: {str(e)}")
    
    async def generate_with_context(
        self,
        prompt: str,
        context_documents: list[str],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """Generate response with RAG context"""
        
        # Build context string from documents
        context = "\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(context_documents)])
        
        # Enhanced system prompt for RAG
        rag_system_prompt = """You are a D&D Campaign Assistant. Use the provided context documents to answer questions and help with campaign management.

Guidelines:
- Base your responses primarily on the provided context
- Maintain the tone and style consistent with the campaign setting
- If context is insufficient, clearly state what additional information would be helpful
- Provide specific references to source material when relevant
- Be creative but stay true to established lore and narrative"""
        
        if system_prompt:
            rag_system_prompt = f"{rag_system_prompt}\n\nAdditional instructions: {system_prompt}"
        
        # Build the full prompt with context
        full_prompt = f"""Context Documents:
{context}

---

Question/Request: {prompt}

Please provide a helpful response based on the context above."""
        
        return await self.generate(
            prompt=full_prompt,
            system_prompt=rag_system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    def is_available(self) -> bool:
        """Check if Ollama service is available"""
        try:
            # Try to list models to test connection
            self.client.list()
            return True
        except Exception:
            return False
    
    def list_models(self) -> list[str]:
        """List available models in Ollama"""
        try:
            models = self.client.list()
            return [model.model for model in models.models]
        except Exception as e:
            raise RuntimeError(f"Failed to list Ollama models: {str(e)}")
    
    def pull_model(self, model_name: str) -> bool:
        """Pull a model if not available"""
        try:
            self.client.pull(model_name)
            return True
        except Exception as e:
            print(f"Failed to pull model {model_name}: {str(e)}")
            return False
    
    def get_available_models(self) -> list[str]:
        """Get cached list of available models"""
        if self._available_models is None:
            try:
                models = self.client.list()
                self._available_models = [model.model for model in models.models]
            except Exception:
                self._available_models = []
        return self._available_models
    
    def is_model_available(self, model_name: str) -> bool:
        """Check if specific model is available"""
        available = self.get_available_models()
        return model_name in available
    
    def refresh_model_cache(self):
        """Force refresh of available models cache"""
        self._available_models = None