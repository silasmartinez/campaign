# Campaign Assistant - Claude Code Context

## Project Overview
A RAG-powered D&D campaign management assistant that helps Dungeon Masters prepare sessions, manage evolving campaign state, and synthesize content from multiple sources while maintaining consistent tone and narrative coherence.

## Engineering Principles & Architecture

### Core Principles
- **12-Factor App Compliance**: Environment-aware configuration, stateless processes, explicit dependencies
- **Container-First**: Prefer Docker/containerized solutions for deployment and development
- **Local-First**: Data stored locally with optional cloud LLM integration
- **Engineering Best Practices**: Clean code, testing, CI/CD, security-first design
- **Modular Architecture**: Loosely coupled components for maintainability

### Technical Standards
- **Code Quality**: Type hints, docstrings, linting (black, isort), testing (pytest)
- **Configuration**: YAML-based with environment variable overrides
- **Security**: API key management, data protection, access controls
- **Performance**: < 2s simple queries, < 10s complex synthesis
- **Scalability**: Support 1000+ documents, multi-year campaigns

## Current Implementation Status

### ✅ Completed (Phase 1 Foundation)
- **Document Processing**: PDF, Markdown, text file ingestion
- **Vector Storage**: ChromaDB integration for semantic search
- **Basic CLI**: Command-line interface for ingestion and search
- **Configuration System**: Environment-aware YAML configuration
- **Storage Architecture**: Local file system + vector database
- **Content Classification**: Document type detection and metadata extraction
- **Search & Retrieval**: Vector similarity search with relevance scoring

### 🚧 In Progress
- **Setup Wizard**: Need to implement 🧙‍♂️ wizard for initial configuration
- **Multi-Campaign Support**: Feature flag exists but not implemented
- **Container Support**: Need Docker setup and `make install_docker`

### ❌ Missing Critical Features
- **Web Interface**: Currently CLI-only, need FastAPI backend + frontend
- **LLM Integration**: Local (Ollama) and cloud (OpenAI/Anthropic) model support
- **Session State Management**: Campaign timeline and context tracking
- **Content Synthesis**: Currently retrieval-only, need content generation
- **Tone Adaptation**: Maintain campaign atmosphere across content
- **Living Documents**: Dynamic content updates based on session outcomes

## Deviations from Base Requirements

### Agreed Deviations
1. **Database Choice**: Using ChromaDB (vector) + SQLite instead of PostgreSQL for simplicity
2. **Platform Priority**: Starting with local development, container deployment second
3. **UI Implementation**: CLI-first approach for MVP, web interface in Phase 2

### Technical Debt
1. **No Setup Wizard**: Should have 🧙‍♂️ emoji and config population
2. **No Docker Support**: make install uses venv, need containerized option
3. **Single Campaign**: Multi-campaign isolation not implemented
4. **No Web Interface**: CLI-only limits usability

## Dependencies

### Core Runtime
- **Python 3.11+**: Primary language
- **ChromaDB 0.4.18**: Vector database for embeddings
- **sentence-transformers 2.7.0**: Text embedding models
- **LangChain 0.1.4**: LLM orchestration framework
- **FastAPI 0.104.1**: Web framework (for future API)
- **Pydantic 2.5.2**: Data validation and settings

### Development
- **pytest 7.4.3**: Testing framework
- **black 23.12.1**: Code formatting
- **isort**: Import sorting (implied in Makefile)

### Future Dependencies (Planned)
- **Ollama**: Local LLM inference
- **OpenAI/Anthropic SDKs**: Cloud LLM integration
- **PostgreSQL**: Production database (scalability)
- **Next.js**: Frontend framework
- **Docker**: Containerization

## Feature Roadmap

### Phase 1: Foundation (Current)
- [x] Document ingestion system
- [x] Vector search and retrieval
- [x] Basic CLI interface
- [ ] Setup wizard with 🧙‍♂️ emoji
- [ ] Multi-campaign support
- [ ] Docker containerization

### Phase 2: Content Generation
- [ ] LLM integration (local + cloud)
- [ ] Session preparation tools
- [ ] Tone adaptation engine
- [ ] Web interface (FastAPI + frontend)
- [ ] Living document system

### Phase 3: Advanced Features
- [ ] Multi-campaign management
- [ ] Collaborative features
- [ ] Advanced analytics
- [ ] Community integration

## Wishlist Features

### High Priority
- **🧙‍♂️ Setup Wizard**: Interactive configuration with cute wizard emoji
- **Campaign Switching**: Easy switching between multiple isolated campaigns
- **Docker Development**: `make install_docker` for containerized development
- **Web UI**: Modern web interface for better UX
- **Smart Content Synthesis**: Merge content from multiple sources with tone consistency

### Medium Priority
- **Player Portal**: Shared access for players with privacy controls
- **Export/Import**: Portable campaign data and template sharing
- **Advanced Search**: Complex queries with entity relationships
- **Session Tracker**: Real-time session state and outcome processing

### Low Priority
- **Mobile App**: iOS/Android companion app
- **Voice Interface**: Speech-to-text for live session assistance
- **VTT Integration**: Direct integration with Roll20, Foundry VTT
- **Community Hub**: Template and content sharing platform

## Current File Structure
```
campaign/
├── src/                    # Source code
│   ├── config/            # Configuration management
│   ├── ingestion/         # Document processing
│   ├── storage/           # Vector and file storage
│   └── retrieval/         # Search and retrieval
├── config/                # Configuration files (missing)
├── data/                  # Runtime data (gitignored)
├── scripts/               # Utility scripts
├── main.py               # CLI entry point
├── requirements.txt      # Python dependencies
├── pyproject.toml        # Project configuration
└── Makefile             # Build and deployment
```

## Git Workflow & Commands

### Development Commands
- `make install`: Install all dependencies in virtual environment
- `make start`: Start the Campaign Assistant CLI
- `make test`: Run test suite
- `make format`: Format code with black and isort
- `make lint`: Check code formatting and style

### Planned Commands
- `make install_docker`: Install using Docker containers
- `make dev`: Start development server with hot reload
- `make deploy`: Deploy to production environment

## Known Issues

### Immediate Fixes Needed
1. **Missing Setup Wizard**: No initial configuration flow
2. **No Docker Support**: Only virtual environment installation
3. **Single Campaign Limitation**: No isolation between campaigns
4. **Runtime Files in Git**: Need to verify .gitignore coverage

### Technical Issues
1. **sentence-transformers Compatibility**: Fixed version conflicts with huggingface_hub
2. **Configuration Loading**: YAML config files don't exist yet
3. **Feature Flags**: Multi-campaign support disabled in config

## Testing Strategy

### Current Testing
- Basic smoke tests in `test_campaign.py`
- Manual testing through CLI commands

### Planned Testing
- Unit tests for all core components
- Integration tests for end-to-end workflows
- Performance benchmarks for ingestion/retrieval
- User acceptance testing for DM workflows

## Security Considerations

### Data Protection
- All campaign data stored locally by default
- API keys managed through environment variables
- No sensitive data in configuration files
- DM-only content access controls (planned)

### API Security
- Secure handling of cloud LLM API keys
- Rate limiting for external API calls
- Input validation and sanitization
- CORS configuration for web interface

## Performance Targets

### Response Times
- Simple queries: < 2 seconds
- Complex synthesis: < 10 seconds
- Document ingestion: < 5 minutes for 50-100 pages

### Scalability
- Support 1000+ documents per campaign
- Multiple concurrent campaigns
- Multi-year campaign timelines
- Efficient storage and retrieval at scale

---

*Last updated: 2025-01-13*
*Current Phase: 1 (Foundation)*
*Next Major Milestone: Setup Wizard + Multi-Campaign Support*