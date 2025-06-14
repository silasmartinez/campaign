"""
Vector storage module using ChromaDB for semantic search capabilities.
Handles document embedding storage and retrieval for campaign content.
"""

import os
from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from ..ingestion.document_processor import Document


class VectorStore:
    """Manages document embeddings and semantic search using ChromaDB."""
    
    def __init__(self, 
                 storage_path: Optional[str] = None,
                 embedding_model: Optional[str] = None,
                 collection_name: Optional[str] = None,
                 settings=None):
        """Initialize the vector store with ChromaDB and sentence transformer."""
        # Import here to avoid circular dependency
        from ..config.settings import get_settings
        
        if settings is None:
            settings = get_settings()
        
        # Use config values or provided parameters
        self.storage_path = Path(storage_path or settings.storage.vector_db.path)
        self.embedding_model_name = embedding_model or settings.embeddings.model.name
        self.collection_name = collection_name or settings.storage.vector_db.collection_name
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.storage_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(
            self.embedding_model_name,
            cache_folder=settings.embeddings.model.cache_dir
        )
        
        # Get or create collection
        self.collection = self._get_or_create_collection()
    
    def _get_or_create_collection(self):
        """Get existing collection or create a new one."""
        try:
            return self.client.get_collection(name=self.collection_name)
        except ValueError:
            return self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Campaign documents and content"}
            )
    
    def add_document(self, document: Document) -> None:
        """Add a single document to the vector store."""
        if not document.chunks:
            # If no chunks, treat entire content as one chunk
            chunks = [document.content]
        else:
            chunks = document.chunks
        
        # Prepare data for insertion
        ids = []
        documents = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{document.id}_chunk_{i}"
            ids.append(chunk_id)
            documents.append(chunk)
            
            # Combine document metadata with chunk-specific metadata
            chunk_metadata = {
                'document_id': document.id,
                'document_title': document.title,
                'file_path': document.file_path,
                'file_type': document.file_type,
                'chunk_index': i,
                'total_chunks': len(chunks),
                'created_at': document.created_at.isoformat()
            }
            
            # Serialize document metadata, converting datetime objects to strings
            for key, value in document.metadata.items():
                if isinstance(value, datetime):
                    chunk_metadata[key] = value.isoformat()
                else:
                    chunk_metadata[key] = value
            metadatas.append(chunk_metadata)
        
        # Add to collection
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add multiple documents to the vector store."""
        for document in documents:
            self.add_document(document)
    
    def search(self, 
               query: str, 
               n_results: int = 10,
               content_type: Optional[str] = None,
               file_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for relevant documents using semantic similarity."""
        # Build where clause for filtering
        where_clause = {}
        if content_type:
            where_clause['content_type'] = content_type
        if file_type:
            where_clause['file_type'] = file_type
        
        # Perform search
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause if where_clause else None,
            include=['documents', 'metadatas', 'distances']
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                result = {
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i],
                    'similarity': max(0.0, 1 - results['distances'][0][i] / 2.0)  # Normalize distance to [0,1] similarity
                }
                formatted_results.append(result)
        
        return formatted_results
    
    def get_document_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        """Retrieve all chunks for a specific document."""
        results = self.collection.get(
            where={'document_id': document_id},
            include=['documents', 'metadatas']
        )
        
        chunks = []
        if results['documents']:
            for i in range(len(results['documents'])):
                chunk = {
                    'content': results['documents'][i],
                    'metadata': results['metadatas'][i]
                }
                chunks.append(chunk)
        
        # Sort by chunk index
        chunks.sort(key=lambda x: x['metadata'].get('chunk_index', 0))
        return chunks
    
    def delete_document(self, document_id: str) -> None:
        """Delete all chunks of a document from the vector store."""
        # Get all chunk IDs for this document
        results = self.collection.get(
            where={'document_id': document_id},
            include=['ids']
        )
        
        if results['ids']:
            self.collection.delete(ids=results['ids'])
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all unique documents in the vector store."""
        # Get all metadata
        results = self.collection.get(include=['metadatas'])
        
        # Group by document_id and get unique documents
        documents = {}
        for metadata in results['metadatas']:
            doc_id = metadata['document_id']
            if doc_id not in documents:
                documents[doc_id] = {
                    'document_id': doc_id,
                    'title': metadata['document_title'],
                    'file_path': metadata['file_path'],
                    'file_type': metadata['file_type'],
                    'content_type': metadata.get('content_type', 'general'),
                    'created_at': metadata['created_at'],
                    'total_chunks': metadata['total_chunks']
                }
        
        return list(documents.values())
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        count = self.collection.count()
        documents = self.list_documents()
        
        # Count by content type
        content_types = {}
        file_types = {}
        
        for doc in documents:
            content_type = doc.get('content_type', 'general')
            file_type = doc.get('file_type', 'unknown')
            
            content_types[content_type] = content_types.get(content_type, 0) + 1
            file_types[file_type] = file_types.get(file_type, 0) + 1
        
        return {
            'total_chunks': count,
            'total_documents': len(documents),
            'content_types': content_types,
            'file_types': file_types
        }
    
    def reset_collection(self) -> None:
        """Delete all data in the collection."""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self._get_or_create_collection()