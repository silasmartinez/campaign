"""
Document processing module for campaign content ingestion.
Handles PDF, markdown, and text file processing with metadata extraction.
"""

import os
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

import PyPDF2
import markdown
from bs4 import BeautifulSoup


@dataclass
class Document:
    """Represents a processed document with content and metadata."""
    id: str
    title: str
    content: str
    file_path: str
    file_type: str
    created_at: datetime
    metadata: Dict[str, Any]
    chunks: List[str] = None


class DocumentProcessor:
    """Processes various document types for campaign content ingestion."""
    
    def __init__(self, chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None, settings=None):
        # Import here to avoid circular dependency
        from ..config.settings import get_settings
        
        if settings is None:
            settings = get_settings()
        
        self.chunk_size = chunk_size or settings.processing.chunking.chunk_size
        self.chunk_overlap = chunk_overlap or settings.processing.chunking.chunk_overlap
        self.supported_extensions = set(settings.processing.supported_formats)
    
    def process_file(self, file_path: str) -> Optional[Document]:
        """Process a single file and return a Document object."""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {path.suffix}")
        
        # Generate document ID from file hash
        doc_id = self._generate_document_id(file_path)
        
        # Extract content based on file type
        if path.suffix.lower() == '.pdf':
            content, title = self._process_pdf(file_path)
        elif path.suffix.lower() in {'.md', '.markdown'}:
            content, title = self._process_markdown(file_path)
        else:  # .txt
            content, title = self._process_text(file_path)
        
        # Extract metadata
        metadata = self._extract_metadata(file_path, content)
        
        # Create chunks
        chunks = self._create_chunks(content)
        
        return Document(
            id=doc_id,
            title=title or path.stem,
            content=content,
            file_path=file_path,
            file_type=path.suffix.lower(),
            created_at=datetime.now(),
            metadata=metadata,
            chunks=chunks
        )
    
    def process_directory(self, directory_path: str, recursive: bool = True) -> List[Document]:
        """Process all supported files in a directory."""
        path = Path(directory_path)
        documents = []
        
        if not path.exists() or not path.is_dir():
            raise ValueError(f"Invalid directory: {directory_path}")
        
        pattern = "**/*" if recursive else "*"
        
        for file_path in path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                try:
                    doc = self.process_file(str(file_path))
                    if doc:
                        documents.append(doc)
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
        
        return documents
    
    def _process_pdf(self, file_path: str) -> tuple[str, Optional[str]]:
        """Extract text content from PDF file."""
        content = ""
        title = None
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Try to get title from PDF metadata
            if pdf_reader.metadata:
                title = pdf_reader.metadata.get('/Title')
            
            # Extract text from all pages
            for page in pdf_reader.pages:
                content += page.extract_text() + "\n"
        
        return content.strip(), title
    
    def _process_markdown(self, file_path: str) -> tuple[str, Optional[str]]:
        """Extract content from markdown file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            raw_content = file.read()
        
        # Convert markdown to HTML then extract text
        html = markdown.markdown(raw_content, extensions=['meta', 'toc'])
        soup = BeautifulSoup(html, 'html.parser')
        content = soup.get_text()
        
        # Try to extract title from first heading or frontmatter
        title = None
        lines = raw_content.split('\n')
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
                break
            elif line.startswith('title:'):
                title = line[6:].strip().strip('"\'')
                break
        
        return content.strip(), title
    
    def _process_text(self, file_path: str) -> tuple[str, Optional[str]]:
        """Extract content from text file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Use filename as title
        title = Path(file_path).stem
        
        return content.strip(), title
    
    def _extract_metadata(self, file_path: str, content: str) -> Dict[str, Any]:
        """Extract metadata from file and content."""
        path = Path(file_path)
        stat = path.stat()
        
        metadata = {
            'file_size': stat.st_size,
            'modified_at': datetime.fromtimestamp(stat.st_mtime),
            'word_count': len(content.split()),
            'character_count': len(content),
            'file_name': path.name,
            'file_extension': path.suffix.lower()
        }
        
        # Simple content classification
        content_lower = content.lower()
        metadata['content_type'] = self._classify_content(content_lower)
        
        return metadata
    
    def _classify_content(self, content: str) -> str:
        """Basic content type classification."""
        # Simple keyword-based classification
        if any(word in content for word in ['npc', 'character', 'villain', 'ally']):
            return 'character'
        elif any(word in content for word in ['location', 'city', 'town', 'dungeon', 'map']):
            return 'location'
        elif any(word in content for word in ['encounter', 'combat', 'monster', 'creature']):
            return 'encounter'
        elif any(word in content for word in ['lore', 'history', 'legend', 'mythology']):
            return 'lore'
        elif any(word in content for word in ['quest', 'adventure', 'mission', 'campaign']):
            return 'adventure'
        else:
            return 'general'
    
    def _create_chunks(self, content: str) -> List[str]:
        """Split content into overlapping chunks for better retrieval."""
        if len(content) <= self.chunk_size:
            return [content]
        
        chunks = []
        start = 0
        
        while start < len(content):
            end = start + self.chunk_size
            
            # Try to break at sentence or paragraph boundaries
            if end < len(content):
                # Look for sentence endings near the chunk boundary
                for i in range(end, max(start + self.chunk_size - 100, start), -1):
                    if content[i] in '.!?\n':
                        end = i + 1
                        break
            
            chunk = content[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - self.chunk_overlap
        
        return chunks
    
    def _generate_document_id(self, file_path: str) -> str:
        """Generate a unique ID for the document based on file path and modification time."""
        path = Path(file_path)
        id_string = f"{file_path}_{path.stat().st_mtime}"
        return hashlib.md5(id_string.encode()).hexdigest()