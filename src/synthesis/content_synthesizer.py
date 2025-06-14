from typing import Dict, Any, Optional
from dataclasses import dataclass
from ..llm.base import BaseLLMService, LLMResponse
from ..retrieval.retriever import CampaignRetriever


@dataclass
class SynthesisRequest:
    """Request for content synthesis"""
    query: str
    intent: str = "general"  # general, session_prep, npc_info, lore_expansion, etc.
    tone: Optional[str] = None  # dark, whimsical, epic, etc.
    max_context_docs: int = 5
    campaign_context: Optional[Dict[str, Any]] = None


@dataclass
class SynthesisResult:
    """Result from content synthesis"""
    content: str
    sources: list[str]
    confidence: float
    metadata: Dict[str, Any]
    llm_response: LLMResponse


class ContentSynthesizer:
    """Synthesizes campaign content using RAG + LLM"""
    
    def __init__(self, retriever: CampaignRetriever, llm_service: BaseLLMService):
        self.retriever = retriever
        self.llm_service = llm_service
    
    async def synthesize(self, request: SynthesisRequest) -> SynthesisResult:
        """Synthesize content based on the request"""
        
        # 1. Retrieve relevant documents
        search_results = self.retriever.search(
            query=request.query,
            max_results=request.max_context_docs
        )
        
        # 2. Build context documents
        context_docs = []
        sources = []
        for result in search_results:
            context_docs.append(f"Source: {result.metadata.get('source', 'Unknown')}\n{result.content}")
            sources.append(result.metadata.get('source', 'Unknown'))
        
        # 3. Build system prompt based on intent and tone
        system_prompt = self._build_system_prompt(request.intent, request.tone)
        
        # 4. Generate response using LLM with task-specific model selection
        llm_response = await self.llm_service.generate_with_context(
            prompt=request.query,
            context_documents=context_docs,
            system_prompt=system_prompt,
            temperature=0.7,
            intent=request.intent
        )
        
        # 5. Calculate confidence based on retrieval scores and LLM metadata
        confidence = self._calculate_confidence(search_results, llm_response)
        
        return SynthesisResult(
            content=llm_response.content,
            sources=sources,
            confidence=confidence,
            metadata={
                "intent": request.intent,
                "tone": request.tone,
                "num_context_docs": len(context_docs),
                "retrieval_scores": [r.relevance_score for r in search_results]
            },
            llm_response=llm_response
        )
    
    def _build_system_prompt(self, intent: str, tone: Optional[str] = None) -> str:
        """Build system prompt based on intent and tone"""
        
        base_prompts = {
            "general": "You are a helpful D&D Campaign Assistant. Provide clear, accurate information based on the provided context.",
            
            "session_prep": """You are a D&D Campaign Assistant helping a DM prepare for a session. 
Focus on actionable information: plot hooks, NPC motivations, potential encounters, and narrative connections.
Be specific and practical - provide concrete details the DM can use immediately.""",
            
            "npc_info": """You are a D&D Campaign Assistant providing NPC information.
Focus on personality, motivations, relationships, and potential dialogue.
Make NPCs feel alive and memorable with distinct voices and mannerisms.""",
            
            "lore_expansion": """You are a D&D Campaign Assistant expanding on campaign lore.
Maintain consistency with established facts while adding rich detail.
Focus on world-building elements: history, culture, politics, and interconnections.""",
            
            "encounter_design": """You are a D&D Campaign Assistant helping design encounters.
Consider party level, narrative context, and tactical variety.
Provide both combat and non-combat encounter options where appropriate."""
        }
        
        system_prompt = base_prompts.get(intent, base_prompts["general"])
        
        # Add tone guidance
        if tone:
            tone_guidance = {
                "dark": "Maintain a dark, serious tone with hints of danger and moral complexity.",
                "whimsical": "Use a lighthearted, playful tone with humor and wonder.",
                "epic": "Use a grand, heroic tone emphasizing high stakes and legendary deeds.",
                "mysterious": "Maintain an air of mystery and intrigue, revealing information gradually.",
                "gritty": "Use a realistic, harsh tone focusing on practical concerns and consequences."
            }
            
            if tone in tone_guidance:
                system_prompt += f"\n\nTone: {tone_guidance[tone]}"
        
        return system_prompt
    
    def _calculate_confidence(self, search_results: list[Any], llm_response: LLMResponse) -> float:
        """Calculate confidence score for the synthesis"""
        
        if not search_results:
            return 0.1  # Very low confidence without context
        
        # Base confidence on retrieval quality
        avg_retrieval_score = sum(r.relevance_score for r in search_results) / len(search_results)
        
        # Adjust based on number of sources
        source_bonus = min(0.2, len(search_results) * 0.05)
        
        # TODO: Add LLM confidence indicators when available
        # llm_confidence = self._extract_llm_confidence(llm_response)
        
        confidence = min(1.0, avg_retrieval_score + source_bonus)
        return round(confidence, 2)
    
    async def generate_session_summary(
        self, 
        session_notes: str, 
        campaign_context: Optional[Dict[str, Any]] = None
    ) -> SynthesisResult:
        """Generate a session summary and update campaign state"""
        
        request = SynthesisRequest(
            query=f"Please create a session summary and identify important story developments from these notes:\n\n{session_notes}",
            intent="session_prep",
            max_context_docs=3
        )
        
        # Enhance system prompt for session summaries
        system_prompt = """You are a D&D Campaign Assistant creating a session summary.

Focus on:
1. Key story developments and plot progression
2. Important NPC interactions and relationship changes
3. New locations discovered or lore revealed
4. Character decisions that might have future consequences
5. Unresolved plot threads or mysteries introduced

Format your response as:
## Session Summary
[Brief overview of what happened]

## Key Developments
- [Important story beats]

## NPCs Encountered
- [Notable NPC interactions]

## Ongoing Threads
- [Plot hooks and unresolved elements]

Be concise but thorough. Focus on information that will be useful for future session preparation."""
        
        # Retrieve relevant campaign context
        context_results = self.retriever.search(
            query=f"campaign context session history {session_notes[:200]}",
            max_results=3
        )
        
        context_docs = [f"Source: {r.metadata.get('source', 'Unknown')}\n{r.content}" for r in context_results]
        
        llm_response = await self.llm_service.generate_with_context(
            prompt=request.query,
            context_documents=context_docs,
            system_prompt=system_prompt,
            intent="session_summary"
        )
        
        return SynthesisResult(
            content=llm_response.content,
            sources=[r.metadata.get('source', 'Unknown') for r in context_results],
            confidence=self._calculate_confidence(context_results, llm_response),
            metadata={"intent": "session_summary", "type": "campaign_update"},
            llm_response=llm_response
        )