# D&D Campaign Assistant - Technical Requirements

## Project Overview

A RAG-powered campaign management assistant designed to help Dungeon Masters prepare sessions, manage evolving campaign state, and synthesize content from multiple sources while maintaining consistent tone and narrative coherence.

## Core Principles

- **Local-first data storage** with hybrid local/cloud LLM usage
- **Content synthesis over simple retrieval** - merge and adapt rather than just find
- **Tone-aware content generation** - maintain campaign atmosphere across all artifacts
- **Living document management** - evolve content based on session outcomes
- **Multi-source integration** - combine official, third-party, and custom content seamlessly

---

## Phase 1: Foundation & Core RAG

### 1.1 Content Ingestion System

#### Document Processing
- **Local file ingestion**
  - PDF parsing with text extraction and metadata preservation
  - Markdown file processing with frontmatter support
  - Image ingestion with OCR capability for maps/handouts
  - Batch directory scanning and import
- **URL content retrieval**
  - Web scraping for blog posts, wikis, forum threads
  - Content extraction from HTML with noise filtering
  - Archive.org and cached content support
  - Rate limiting and respectful crawling
- **Structured data import**
  - JSON/YAML campaign data files
  - CSV imports for NPC lists, encounter tables, etc.
  - Integration hooks for popular campaign management tools

#### Content Classification
- **Automatic categorization**
  - Document type detection (campaign module, supplement, homebrew, etc.)
  - Content type classification (NPC, location, encounter, lore, etc.)
  - Source attribution tracking (official, third-party, homebrew)
  - Campaign/setting assignment
- **Metadata extraction**
  - Title, author, publication date extraction
  - Topic and theme identification
  - Cross-reference discovery (mentions of NPCs, locations, etc.)
  - Tone/mood classification

#### Storage Architecture
- **Vector database** (Chroma) for semantic search
- **Relational database** (SQLite/PostgreSQL) for metadata and relationships
- **File system** for original document preservation
- **Knowledge graph** for entity relationships and cross-references

### 1.2 Retrieval System

#### Query Processing
- **Natural language query parsing**
  - Intent classification (prep request, lore lookup, character info, etc.)
  - Entity extraction (NPC names, locations, campaign elements)
  - Context awareness (current session, recent events, player actions)
- **Semantic search capabilities**
  - Vector similarity search across all content
  - Hybrid keyword + semantic retrieval
  - Contextual re-ranking based on campaign state
  - Multi-hop reasoning for complex queries

#### Context Management
- **Session state tracking**
  - Current campaign timeline and location
  - Recent player actions and decisions
  - Active plot threads and hooks
  - NPC relationship states
- **Relevance filtering**
  - Geographic relevance (current region/location)
  - Temporal relevance (current campaign timeline)
  - Player relevance (character backgrounds, interests, abilities)

### 1.3 Core Chat Interface

#### User Interface
- **Primary chat interface**
  - Natural language interaction for all requests
  - Rich message formatting (markdown, embeds, tables)
  - File upload capability within chat
  - Message history and search
- **Artifact surfacing**
  - Dynamic sidebar with relevant documents
  - Context-aware content suggestions
  - Quick-access panels for frequently referenced material
  - Visual organization of related content

#### Response Generation
- **Local model integration** (Ollama)
  - Llama 3.1 8B or Mistral 7B for basic queries
  - Document summarization and initial processing
  - Content classification and tagging
- **Cloud model integration**
  - Claude/GPT-4 for complex synthesis tasks
  - Creative content generation
  - Tone adaptation and style matching
- **Hybrid orchestration**
  - Intelligent routing between local and cloud models
  - Cost optimization for cloud API usage
  - Fallback strategies for model availability

### 1.4 Basic Document Management

#### File Organization
- **Automated folder structure**
  - Campaign-based organization
  - Content type hierarchies
  - Source-based categorization
  - Duplicate detection and handling
- **Naming conventions**
  - Standardized file naming
  - Version control for evolving documents
  - Cross-reference preservation
  - Metadata-driven organization

#### Document Tracking
- **Version history**
  - Change tracking for evolving documents
  - Session-based snapshots
  - Rollback capabilities
  - Merge conflict resolution
- **Usage analytics**
  - Frequently accessed content identification
  - Content gap analysis
  - Reference pattern tracking
  - Optimization recommendations

---

## Phase 2: Advanced Content Generation

### 2.1 Session Preparation Tools

#### Prep Document Generation
- **Narrative session plans**
  - Story beat structuring
  - Pacing and tension management
  - Emotional arc planning
  - Player agency consideration
- **Structured reference documents**
  - At-a-glance encounter summaries
  - NPC quick-reference sheets
  - Location details and atmosphere
  - Mechanics and rules reminders
- **Branching scenario planning**
  - Multiple outcome preparation
  - Player choice consequence mapping
  - Fallback and contingency planning
  - Improvisation support material

#### Encounter Design
- **Multi-source synthesis**
  - Combine official encounters with homebrew modifications
  - Adapt published content to campaign tone
  - Scale encounters for party composition
  - Integrate ongoing plot elements
- **Mechanical optimization**
  - Balance verification and suggestions
  - Tactical complexity analysis
  - Resource management consideration
  - Time and pacing estimation

### 2.2 Tone Adaptation Engine

#### Style Consistency
- **Campaign tone analysis**
  - Existing content mood extraction
  - Writing style pattern recognition
  - Vocabulary and phrase preference learning
  - Narrative voice consistency
- **Content transformation**
  - Automatic tone adaptation for imported content
  - Style guide enforcement
  - Voice matching for generated material
  - Atmosphere preservation across sources

#### Template System
- **Artifact templates**
  - Customizable document formats
  - Style-aware content generation
  - Brand consistency maintenance
  - Player-facing vs. DM-facing formatting
- **Tone presets**
  - Pre-configured mood settings (grimdark, heroic, horror, etc.)
  - Custom tone profile creation
  - Mood-specific vocabulary and phrasing
  - Atmospheric description enhancement

### 2.3 Living Document System

#### State Management
- **Campaign timeline tracking**
  - Event chronology maintenance
  - Cause-and-effect relationship mapping
  - Future consequence prediction
  - Alternative timeline exploration
- **Dynamic content updates**
  - NPC status and relationship evolution
  - Location changes based on player actions
  - Plot thread progression tracking
  - World state consistency maintenance

#### Session Integration
- **Outcome processing**
  - Session result integration
  - Player decision impact analysis
  - Story thread closure and evolution
  - New hook and opportunity generation
- **Prep adaptation**
  - Future session adjustment based on outcomes
  - Content relevance re-evaluation
  - Priority rebalancing for upcoming sessions
  - Contingency plan activation

---

## Phase 3: Advanced Features

### 3.1 Multi-Campaign Management

#### Campaign Isolation
- **Separate knowledge bases**
  - Campaign-specific content isolation
  - Cross-campaign reference prevention
  - Independent state management
  - Shared resource libraries
- **Template sharing**
  - Reusable encounter templates
  - NPC archetype libraries
  - Location template collections
  - Mechanical framework sharing

#### Portfolio Management
- **Campaign comparison**
  - Progress tracking across campaigns
  - Resource allocation optimization
  - Prep time management
  - Success pattern analysis
- **Cross-campaign insights**
  - Effective technique identification
  - Content reuse opportunities
  - Player preference tracking
  - Improvement recommendation

### 3.2 Collaborative Features

#### Player Integration
- **Shared content management**
  - Player-accessible handouts
  - Session recap distribution
  - Character development tracking
  - Collaborative world-building
- **Privacy controls**
  - DM-only content protection
  - Spoiler prevention systems
  - Selective information sharing
  - Player knowledge state tracking

#### External Sharing
- **Export capabilities**
  - Portable document generation
  - Cross-platform compatibility
  - Version control integration
  - Backup and archival systems
- **Community integration**
  - Template sharing with other DMs
  - Community resource integration
  - Feedback and rating systems
  - Collaborative improvement

### 3.3 Advanced Analytics

#### Campaign Insights
- **Player engagement analysis**
  - Interest pattern identification
  - Participation level tracking
  - Preference learning and adaptation
  - Engagement optimization suggestions
- **Content effectiveness measurement**
  - Successful encounter identification
  - Story element impact analysis
  - Pacing optimization insights
  - Improvement opportunity detection

#### Performance Optimization
- **Prep efficiency analysis**
  - Time investment tracking
  - Resource utilization optimization
  - Workflow improvement identification
  - Automation opportunity discovery
- **Content quality metrics**
  - Player satisfaction correlation
  - Story coherence measurement
  - Tone consistency analysis
  - Narrative impact assessment

---

## Technical Architecture

### System Requirements
- **Platform support**: macOS (Apple Silicon priority), with Linux/Windows consideration
- **Local model requirements**: Optimized for M3 Max with ample RAM
- **Database**: PostgreSQL for production, SQLite for development
- **Vector store**: Chroma for embedding storage and retrieval
- **Web framework**: FastAPI backend, Next.js frontend
- **LLM integration**: Ollama for local models, API integration for cloud models

### Performance Targets
- **Response time**: < 2 seconds for simple queries, < 10 seconds for complex synthesis
- **Ingestion speed**: Process typical campaign module (50-100 pages) in < 5 minutes
- **Storage efficiency**: Optimized chunking and embedding for large document collections
- **Scalability**: Support for campaigns with 1000+ documents and multi-year timelines

### Security and Privacy
- **Local data storage**: All campaign data stored locally by default
- **API security**: Secure handling of cloud LLM API keys
- **Content protection**: DM-only content access controls
- **Data backup**: Automated backup and recovery systems

---

## Success Metrics

### User Experience
- **Prep time reduction**: 30-50% decrease in session preparation time
- **Content quality improvement**: Enhanced narrative coherence and player engagement
- **Workflow integration**: Seamless adoption into existing DM practices
- **Feature utilization**: High engagement with core features across user base

### Technical Performance
- **System reliability**: 99%+ uptime with graceful error handling
- **Response accuracy**: High relevance scores for content retrieval
- **Processing efficiency**: Optimal resource utilization for local deployment
- **Scalability validation**: Support for large-scale campaign management

### Content Generation Quality
- **Tone consistency**: Maintained atmospheric coherence across generated content
- **Narrative integration**: Seamless blending of multiple source materials
- **Player engagement**: Increased player satisfaction and session engagement
- **Creative enhancement**: Expanded creative possibilities for DM storytelling