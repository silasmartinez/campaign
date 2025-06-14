# Campaign Assistant

AI-powered D&D Campaign Management Tool

A RAG-powered campaign management assistant designed to help Dungeon Masters prepare sessions, manage evolving campaign state, and synthesize content from multiple sources while maintaining consistent tone and narrative coherence.

## Phase 1 - Core RAG POC

This implementation focuses on the foundational content ingestion and retrieval system:

- **Document Processing**: PDF, Markdown, and text file ingestion with metadata extraction
- **Vector Storage**: ChromaDB-based semantic search with document embeddings
- **Intelligent Retrieval**: Context-aware search with query intent classification
- **CLI Interface**: Command-line tools for document management and interactive search

## Quick Start

### Option 1: Using Make (Recommended)
```bash
# Check system requirements first
make check-system

# Install and run test
make quickstart

# Or step by step
make install          # Install dependencies
make run-test         # Test the system
```

### Option 2: Manual Installation
```bash
# Run the install script
./install.sh

# Activate virtual environment
source venv/bin/activate

# Test the system
python test_campaign.py
```

### Troubleshooting
```bash
make doctor           # Diagnose issues and get fix suggestions
make fix-macos       # Auto-fix common macOS issues (macOS only)
```

## Usage

### Basic Commands
```bash
# Activate environment (after installation)
source venv/bin/activate

# Ingest documents from a directory
python main.py ingest /path/to/campaign/docs

# Interactive search mode
python main.py interactive

# Quick search
python main.py search "Who is the village elder?"

# List all documents
python main.py list

# Show collection statistics
python main.py stats
```

### Development Commands
```bash
make dev-install      # Install dev dependencies
make format           # Format code
make lint            # Run linting
make test            # Run tests
make clean           # Clean up files
```

## Features

### Document Processing
- **Multi-format support**: PDF, Markdown, plain text
- **Automatic classification**: NPCs, locations, encounters, lore
- **Metadata extraction**: File info, content analysis, word counts
- **Smart chunking**: Context-preserving text segmentation

### Semantic Search
- **Vector embeddings**: Using sentence-transformers for semantic similarity
- **Intent recognition**: Automatic query classification (character info, locations, etc.)
- **Context awareness**: Campaign-specific relevance boosting
- **Deduplication**: Smart handling of multi-chunk documents

### CLI Interface
- **Interactive mode**: Conversational search experience
- **Batch operations**: Directory-level document processing
- **Statistics**: Collection insights and content analysis
- **Management**: Document listing, deletion, collection reset

## Architecture

```
src/
├── ingestion/          # Document processing pipeline
│   └── document_processor.py
├── storage/           # Vector database management
│   └── vector_store.py
└── retrieval/         # Search and query processing
    └── retriever.py

main.py               # CLI interface
test_campaign.py      # Test suite with sample data
```

## Requirements

- Python 3.9+
- 2GB+ RAM (for local embeddings)
- macOS, Linux, or Windows

## Next Steps (Phase 2+)

- Web interface with FastAPI/Next.js
- LLM integration for content synthesis
- Session preparation tools
- Living document management
- Multi-campaign support

## Contributing

This is a Phase 1 POC. See `reference/base_reqs.md` for the full technical specification and roadmap.
