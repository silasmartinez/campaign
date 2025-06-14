#!/usr/bin/env python3
"""
Campaign Assistant - Phase 1 POC
A simple command-line interface for testing document ingestion and retrieval.
"""

import argparse
import sys
import asyncio
from pathlib import Path

from src.ingestion.document_processor import DocumentProcessor
from src.storage.vector_store import VectorStore
from src.retrieval.retriever import CampaignRetriever, RetrievalContext
from src.llm.service_factory import LLMServiceFactory
from src.synthesis.content_synthesizer import ContentSynthesizer, SynthesisRequest
from src.config.settings import get_settings


def setup_system():
    """Initialize the campaign assistant system."""
    print("🎲 Initializing Campaign Assistant...")
    
    # Load settings
    settings = get_settings()
    
    # Initialize components
    processor = DocumentProcessor()
    vector_store = VectorStore()
    retriever = CampaignRetriever(vector_store)
    
    # Initialize LLM service if enabled
    llm_service = None
    synthesizer = None
    
    if settings.features.beta.get("llm_integration", False):
        print("🤖 Initializing LLM integration...")
        llm_service = LLMServiceFactory.create_service(settings)
        
        if llm_service:
            synthesizer = ContentSynthesizer(retriever, llm_service)
            print("✅ LLM service ready!")
        else:
            print("⚠️  LLM service not available - check Ollama installation")
    
    print("✅ System initialized!")
    return processor, vector_store, retriever, synthesizer, settings


def ingest_documents(processor, vector_store, path):
    """Ingest documents from a file or directory."""
    path_obj = Path(path)
    
    if not path_obj.exists():
        print(f"❌ Path does not exist: {path}")
        return
    
    print(f"📚 Processing documents from: {path}")
    
    if path_obj.is_file():
        # Process single file
        try:
            document = processor.process_file(str(path_obj))
            vector_store.add_document(document)
            print(f"✅ Processed: {document.title}")
        except Exception as e:
            print(f"❌ Error processing {path}: {e}")
    else:
        # Process directory
        documents = processor.process_directory(str(path_obj))
        
        if not documents:
            print("⚠️  No supported documents found")
            return
        
        print(f"📄 Found {len(documents)} documents")
        
        for doc in documents:
            try:
                vector_store.add_document(doc)
                print(f"✅ Added: {doc.title}")
            except Exception as e:
                print(f"❌ Error adding {doc.title}: {e}")
    
    # Show collection stats
    stats = vector_store.get_collection_stats()
    print(f"\n📊 Collection Stats:")
    print(f"   Total documents: {stats['total_documents']}")
    print(f"   Total chunks: {stats['total_chunks']}")
    print(f"   Content types: {stats['content_types']}")


def interactive_search(retriever):
    """Start interactive search mode."""
    print("\n🔍 Entering interactive search mode")
    print("Type your questions about campaign content, or 'quit' to exit")
    print("-" * 50)
    
    while True:
        try:
            query = input("\n❓ Question: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if not query:
                continue
            
            print("🔍 Searching...")
            results = retriever.search(query, max_results=3)
            
            if not results:
                print("❌ No relevant content found")
                continue
            
            print(f"\n📋 Found {len(results)} relevant results:\n")
            
            for i, result in enumerate(results, 1):
                print(f"🎯 Result {i} (Score: {result.relevance_score:.3f})")
                print(f"📄 Source: {result.source_title}")
                print(f"🏷️  Type: {result.content_type}")
                print(f"📝 Content: {result.content[:300]}...")
                if len(result.content) > 300:
                    print("    [truncated]")
                print("-" * 40)
        
        except KeyboardInterrupt:
            break
        except EOFError:
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n👋 Goodbye!")


def list_documents(vector_store):
    """List all documents in the collection."""
    documents = vector_store.list_documents()
    
    if not documents:
        print("📭 No documents in collection")
        return
    
    print(f"\n📚 Documents in collection ({len(documents)}):")
    print("-" * 60)
    
    for doc in documents:
        print(f"📄 {doc['title']}")
        print(f"   Type: {doc['content_type']} | Format: {doc['file_type']}")
        print(f"   Chunks: {doc['total_chunks']} | Path: {doc['file_path']}")
        print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Campaign Assistant - D&D Campaign Management Tool"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Ingest command
    ingest_parser = subparsers.add_parser('ingest', help='Ingest documents')
    ingest_parser.add_argument('path', help='Path to file or directory to ingest')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search documents')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--max-results', type=int, default=5, 
                              help='Maximum number of results')
    
    # Interactive command
    subparsers.add_parser('interactive', help='Start interactive search mode')
    
    # List command
    subparsers.add_parser('list', help='List all documents')
    
    # Stats command
    subparsers.add_parser('stats', help='Show collection statistics')
    
    # Reset command
    subparsers.add_parser('reset', help='Reset the document collection')
    
    # Ask command (LLM-powered)
    ask_parser = subparsers.add_parser('ask', help='Ask AI about campaign content')
    ask_parser.add_argument('question', help='Question to ask')
    ask_parser.add_argument('--intent', choices=['general', 'session_prep', 'npc_info', 
                                                'lore_expansion', 'encounter_design'], 
                           default='general', help='Type of question/intent')
    ask_parser.add_argument('--tone', choices=['dark', 'whimsical', 'epic', 'mysterious', 'gritty'],
                           help='Desired tone for response')
    
    # Synthesize command (Advanced LLM features)
    synthesize_parser = subparsers.add_parser('synthesize', help='Generate campaign content')
    synthesize_parser.add_argument('prompt', help='Content generation prompt')
    synthesize_parser.add_argument('--intent', choices=['session_prep', 'npc_info', 
                                                       'lore_expansion', 'encounter_design'], 
                                  default='session_prep', help='Type of content to generate')
    synthesize_parser.add_argument('--tone', choices=['dark', 'whimsical', 'epic', 'mysterious', 'gritty'],
                                  help='Desired tone for content')
    
    # Summary command
    summary_parser = subparsers.add_parser('summary', help='Generate session summary')
    summary_parser.add_argument('notes', help='Session notes or path to notes file')
    
    # Models command (show model status)
    subparsers.add_parser('models', help='Show available models and task assignments')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize system
    try:
        processor, vector_store, retriever, synthesizer, settings = setup_system()
    except Exception as e:
        print(f"❌ Failed to initialize system: {e}")
        sys.exit(1)
    
    # Execute command
    try:
        if args.command == 'ingest':
            ingest_documents(processor, vector_store, args.path)
        
        elif args.command == 'search':
            results = retriever.search(args.query, max_results=args.max_results)
            
            if not results:
                print("❌ No relevant content found")
            else:
                print(f"\n🎯 Search Results for: '{args.query}'\n")
                for i, result in enumerate(results, 1):
                    print(f"Result {i} (Score: {result.relevance_score:.3f})")
                    print(f"Source: {result.source_title}")
                    print(f"Type: {result.content_type}")
                    print(f"Content: {result.content[:200]}...")
                    print("-" * 40)
        
        elif args.command == 'interactive':
            interactive_search(retriever)
        
        elif args.command == 'list':
            list_documents(vector_store)
        
        elif args.command == 'stats':
            stats = vector_store.get_collection_stats()
            print("\n📊 Collection Statistics:")
            print(f"Total documents: {stats['total_documents']}")
            print(f"Total chunks: {stats['total_chunks']}")
            print(f"Content types: {stats['content_types']}")
            print(f"File types: {stats['file_types']}")
        
        elif args.command == 'reset':
            confirm = input("⚠️  This will delete all documents. Continue? (y/N): ")
            if confirm.lower() == 'y':
                vector_store.reset_collection()
                print("✅ Collection reset complete")
            else:
                print("❌ Reset cancelled")
        
        elif args.command == 'ask':
            if not synthesizer:
                print("❌ LLM integration not available. Check Ollama installation.")
                sys.exit(1)
            
            print(f"🤖 Asking AI: {args.question}")
            request = SynthesisRequest(
                query=args.question,
                intent=args.intent,
                tone=args.tone,
                max_context_docs=5
            )
            
            result = asyncio.run(synthesizer.synthesize(request))
            
            model_used = result.llm_response.metadata.get("actual_model", "unknown") if result.llm_response.metadata else "unknown"
            print(f"\n🎯 AI Response (🤖 {model_used}, Confidence: {result.confidence:.2f}):")
            print("-" * 50)
            print(result.content)
            print("-" * 50)
            print(f"📚 Sources: {', '.join(result.sources) if result.sources else 'None'}")
        
        elif args.command == 'synthesize':
            if not synthesizer:
                print("❌ LLM integration not available. Check Ollama installation.")
                sys.exit(1)
            
            print(f"🧠 Synthesizing content: {args.prompt}")
            request = SynthesisRequest(
                query=args.prompt,
                intent=args.intent,
                tone=args.tone,
                max_context_docs=5
            )
            
            result = asyncio.run(synthesizer.synthesize(request))
            
            model_used = result.llm_response.metadata.get("actual_model", "unknown") if result.llm_response.metadata else "unknown"
            print(f"\n📜 Generated Content (🤖 {model_used}, Confidence: {result.confidence:.2f}):")
            print("=" * 60)
            print(result.content)
            print("=" * 60)
            print(f"📚 Based on sources: {', '.join(result.sources) if result.sources else 'None'}")
        
        elif args.command == 'summary':
            if not synthesizer:
                print("❌ LLM integration not available. Check Ollama installation.")
                sys.exit(1)
            
            # Check if notes is a file path or direct text
            notes_path = Path(args.notes)
            if notes_path.exists():
                print(f"📄 Reading session notes from: {notes_path}")
                session_notes = notes_path.read_text()
            else:
                session_notes = args.notes
            
            print("📝 Generating session summary...")
            result = asyncio.run(synthesizer.generate_session_summary(session_notes))
            
            model_used = result.llm_response.metadata.get("actual_model", "unknown") if result.llm_response.metadata else "unknown"
            print(f"\n📋 Session Summary (🤖 {model_used}, Confidence: {result.confidence:.2f}):")
            print("=" * 60)
            print(result.content)
            print("=" * 60)
            print(f"📚 Context sources: {', '.join(result.sources) if result.sources else 'None'}")
        
        elif args.command == 'models':
            if not synthesizer:
                print("❌ LLM integration not available. Check Ollama installation.")
                sys.exit(1)
            
            print("🤖 Model Configuration & Status")
            print("=" * 50)
            
            # Get model status from multi-model service
            if hasattr(synthesizer.llm_service, 'get_task_model_status'):
                status = synthesizer.llm_service.get_task_model_status()
                
                for task, info in status.items():
                    icon = "✅" if info["available"] else "❌"
                    actual = f" → {info['actual_model']}" if info['actual_model'] != info['preferred_model'] else ""
                    print(f"{icon} {task:15} | {info['preferred_model']}{actual}")
                
                print("\n🔽 Missing Models:")
                missing = synthesizer.llm_service.suggest_missing_models()
                if missing:
                    for model in missing:
                        print(f"   ollama pull {model}")
                else:
                    print("   All preferred models available! 🎉")
                
                print(f"\n📊 Available Models: {len(synthesizer.llm_service.get_available_models())}")
                for model in synthesizer.llm_service.get_available_models():
                    print(f"   • {model}")
            else:
                print("❌ Model status not available")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()