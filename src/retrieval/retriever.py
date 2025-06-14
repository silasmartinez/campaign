"""
Retrieval system for campaign content.
Handles query processing and context-aware document retrieval.
"""

import re
from typing import Dict, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum

from ..storage.vector_store import VectorStore


class QueryIntent(Enum):
    """Types of queries the system can handle."""
    LORE_LOOKUP = "lore_lookup"
    CHARACTER_INFO = "character_info"
    LOCATION_INFO = "location_info"
    ENCOUNTER_PREP = "encounter_prep"
    GENERAL_SEARCH = "general_search"


@dataclass
class RetrievalContext:
    """Context information for query processing."""
    current_campaign: Optional[str] = None
    current_location: Optional[str] = None
    recent_events: list[str] = None
    active_npcs: list[str] = None
    content_preferences: Dict[str, Any] = None


@dataclass
class RetrievalResult:
    """Result from document retrieval."""
    content: str
    source_title: str
    source_path: str
    content_type: str
    relevance_score: float
    metadata: Dict[str, Any]


class CampaignRetriever:
    """Main retrieval system for campaign content."""
    
    def __init__(self, vector_store: VectorStore, settings=None):
        # Import here to avoid circular dependency
        from ..config.settings import get_settings
        
        if settings is None:
            settings = get_settings()
            
        self.vector_store = vector_store
        self.context = RetrievalContext()
        self.settings = settings
        
        # Keywords for intent classification
        self.intent_keywords = {
            QueryIntent.CHARACTER_INFO: [
                'npc', 'character', 'villain', 'ally', 'who is', 'tell me about',
                'personality', 'motivation', 'backstory', 'stats'
            ],
            QueryIntent.LOCATION_INFO: [
                'where', 'location', 'place', 'city', 'town', 'dungeon', 'map',
                'geography', 'layout', 'description'
            ],
            QueryIntent.ENCOUNTER_PREP: [
                'encounter', 'combat', 'fight', 'battle', 'monster', 'creature',
                'tactics', 'stats', 'abilities', 'challenge'
            ],
            QueryIntent.LORE_LOOKUP: [
                'history', 'lore', 'legend', 'mythology', 'past', 'ancient',
                'tradition', 'culture', 'religion'
            ]
        }
    
    def set_context(self, context: RetrievalContext) -> None:
        """Update the retrieval context."""
        self.context = context
    
    def search(self, 
               query: str, 
               max_results: Optional[int] = None,
               content_type_filter: Optional[str] = None) -> list[RetrievalResult]:
        """Main search method with query processing and context awareness."""
        
        # Use config default if not specified
        if max_results is None:
            max_results = self.settings.retrieval.search.default_max_results
        
        # Process and enhance the query
        processed_query = self._preprocess_query(query)
        intent = self._classify_intent(query)
        
        # Apply content type filtering based on intent
        if not content_type_filter:
            content_type_filter = self._get_content_type_for_intent(intent)
        
        # Perform vector search
        search_results = self.vector_store.search(
            query=processed_query,
            n_results=max_results * 2,  # Get more results for filtering
            content_type=content_type_filter
        )
        
        # Post-process and rank results
        filtered_results = self._post_process_results(search_results, query, intent)
        
        # Convert to RetrievalResult objects
        retrieval_results = []
        for result in filtered_results[:max_results]:
            retrieval_result = RetrievalResult(
                content=result['content'],
                source_title=result['metadata'].get('document_title', 'Unknown'),
                source_path=result['metadata'].get('file_path', ''),
                content_type=result['metadata'].get('content_type', 'general'),
                relevance_score=result['similarity'],
                metadata=result['metadata']
            )
            retrieval_results.append(retrieval_result)
        
        return retrieval_results
    
    def search_by_entity(self, entity_name: str, entity_type: str = None) -> list[RetrievalResult]:
        """Search for content related to a specific entity (NPC, location, etc.)."""
        query = f"{entity_name}"
        if entity_type:
            query += f" {entity_type}"
        
        return self.search(query, content_type_filter=entity_type)
    
    def get_context_relevant_content(self, query: str) -> list[RetrievalResult]:
        """Get content that's relevant to the current campaign context."""
        # Enhance query with context information
        context_enhanced_query = self._enhance_query_with_context(query)
        
        return self.search(context_enhanced_query)
    
    def _preprocess_query(self, query: str) -> str:
        """Clean and enhance the query for better search results."""
        # Basic text cleaning
        cleaned = re.sub(r'\s+', ' ', query.strip().lower())
        
        # Expand common abbreviations
        abbreviations = {
            'dm': 'dungeon master',
            'pc': 'player character',
            'npc': 'non-player character',
            'hp': 'hit points',
            'ac': 'armor class'
        }
        
        for abbr, full in abbreviations.items():
            cleaned = re.sub(rf'\b{abbr}\b', full, cleaned)
        
        return cleaned
    
    def _classify_intent(self, query: str) -> QueryIntent:
        """Classify the intent of the user's query."""
        query_lower = query.lower()
        
        # Score each intent based on keyword matches
        intent_scores = {}
        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                intent_scores[intent] = score
        
        # Return the highest scoring intent, or general search if no matches
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        return QueryIntent.GENERAL_SEARCH
    
    def _get_content_type_for_intent(self, intent: QueryIntent) -> Optional[str]:
        """Map query intent to content type filter."""
        intent_to_content_type = {
            QueryIntent.CHARACTER_INFO: 'character',
            QueryIntent.LOCATION_INFO: 'location',
            QueryIntent.ENCOUNTER_PREP: 'encounter',
            QueryIntent.LORE_LOOKUP: 'lore'
        }
        return intent_to_content_type.get(intent)
    
    def _enhance_query_with_context(self, query: str) -> str:
        """Enhance query with current campaign context."""
        enhanced_query = query
        
        # Add current location context
        if self.context.current_location:
            enhanced_query += f" {self.context.current_location}"
        
        # Add campaign context
        if self.context.current_campaign:
            enhanced_query += f" {self.context.current_campaign}"
        
        # Add active NPCs context
        if self.context.active_npcs:
            enhanced_query += " " + " ".join(self.context.active_npcs)
        
        return enhanced_query
    
    def _post_process_results(self, 
                             results: list[Dict[str, Any]], 
                             original_query: str, 
                             intent: QueryIntent) -> list[Dict[str, Any]]:
        """Post-process search results for relevance and context."""
        
        # Filter out very low similarity results
        threshold = self.settings.retrieval.search.similarity_threshold
        filtered_results = [r for r in results if r['similarity'] > threshold]
        
        # Apply context-based boosting
        for result in filtered_results:
            boost_score = self._calculate_context_boost(result)
            result['similarity'] *= boost_score
        
        # Remove duplicates (same document, different chunks)
        unique_results = self._deduplicate_results(filtered_results)
        
        # Sort by final similarity score
        unique_results.sort(key=lambda x: x['similarity'], reverse=True)
        
        return unique_results
    
    def _calculate_context_boost(self, result: Dict[str, Any]) -> float:
        """Calculate boost score based on current context."""
        boost = 1.0
        metadata = result['metadata']
        
        # Boost results from current campaign
        if (self.context.current_campaign and 
            self.context.current_campaign.lower() in metadata.get('document_title', '').lower()):
            boost *= 1.2
        
        # Boost recently created or modified content
        # (This would require additional metadata tracking)
        
        # Boost based on content type preferences
        if self.context.content_preferences:
            content_type = metadata.get('content_type', 'general')
            if content_type in self.context.content_preferences:
                boost *= self.context.content_preferences[content_type]
        
        return boost
    
    def _deduplicate_results(self, results: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
        """Remove duplicate results from the same document."""
        seen_documents = set()
        unique_results = []
        
        for result in results:
            doc_id = result['metadata']['document_id']
            if doc_id not in seen_documents:
                seen_documents.add(doc_id)
                unique_results.append(result)
        
        return unique_results
    
    def get_related_content(self, document_id: str, max_results: int = 3) -> list[RetrievalResult]:
        """Get content related to a specific document."""
        # Get the document chunks
        chunks = self.vector_store.get_document_chunks(document_id)
        
        if not chunks:
            return []
        
        # Use the first chunk as query for finding related content
        first_chunk = chunks[0]['content'][:500]  # Use first 500 chars
        
        # Search for related content, excluding the original document
        results = self.vector_store.search(
            query=first_chunk,
            n_results=max_results + 5  # Get extra in case we need to filter
        )
        
        # Filter out results from the same document
        related_results = [
            r for r in results 
            if r['metadata']['document_id'] != document_id
        ][:max_results]
        
        # Convert to RetrievalResult objects
        retrieval_results = []
        for result in related_results:
            retrieval_result = RetrievalResult(
                content=result['content'],
                source_title=result['metadata'].get('document_title', 'Unknown'),
                source_path=result['metadata'].get('file_path', ''),
                content_type=result['metadata'].get('content_type', 'general'),
                relevance_score=result['similarity'],
                metadata=result['metadata']
            )
            retrieval_results.append(retrieval_result)
        
        return retrieval_results