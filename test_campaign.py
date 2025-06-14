#!/usr/bin/env python3
"""
Simple test script to verify the campaign assistant functionality.
Creates sample documents and tests ingestion and retrieval.
"""

import os
import tempfile
from pathlib import Path

from src.ingestion.document_processor import DocumentProcessor
from src.storage.vector_store import VectorStore
from src.retrieval.retriever import CampaignRetriever


def create_sample_documents():
    """Create sample campaign documents for testing."""
    temp_dir = Path(tempfile.mkdtemp(prefix="campaign_test_"))
    
    # Sample NPC document
    npc_content = """# Gareth the Wise
    
**Character Type:** NPC Ally
**Location:** Silverbrook Village
**Role:** Village Elder and Lorekeeper

## Description
Gareth is an elderly human wizard who serves as the village elder of Silverbrook. 
He has lived through many adventures and now dedicates his time to preserving 
knowledge and guiding young adventurers.

## Personality
- Wise and patient
- Sometimes cryptic in his speech
- Protective of his village
- Has a particular fondness for herbal tea

## Background
Gareth was once a member of the legendary Circle of Stars, a group of powerful 
mages who protected the realm from dark magic. After a great battle against 
the Shadow Cult, he retired to Silverbrook to live a peaceful life.

## Stats
- Level: 12 Wizard
- AC: 15 (Robes of Protection)
- HP: 78
- Notable Spells: Fireball, Counterspell, Scrying
"""
    
    # Sample location document
    location_content = """# Silverbrook Village

**Region:** Northern Highlands
**Population:** ~200
**Notable Features:** Crystal Brook, Ancient Oak, Wizard's Tower

## Overview
Silverbrook is a peaceful farming village nestled in the Northern Highlands. 
The village gets its name from the crystal-clear brook that runs through its center, 
said to have magical properties that keep the water pure.

## Key Locations

### The Ancient Oak
A massive oak tree at the village center, over 500 years old. Village meetings 
are held beneath its branches.

### Gareth's Tower
A modest stone tower where the village elder Gareth lives and conducts his research.

### The Silver Brook Inn
Run by Martha Goldenheart, serves the best meat pies in the region.

## Current Events
- Harvest Festival preparations are underway
- Strange lights have been seen in the nearby Whispering Woods
- Several livestock have gone missing
"""
    
    # Sample encounter document
    encounter_content = """# Goblin Ambush at Silverbrook Bridge

**Encounter Type:** Combat
**Difficulty:** Easy (CR 1/2)
**Location:** Stone bridge over Silver Brook

## Setup
As the party approaches Silverbrook Village, they must cross the old stone bridge 
over Silver Brook. Three goblins have set up an ambush here, demanding toll 
from travelers.

## Creatures
- 3x Goblin (HP: 7 each, AC: 15)
- 1x Goblin Boss (HP: 21, AC: 17) - hidden initially

## Tactics
The goblins start by demanding a toll of 5 gold pieces per person. If refused:
1. Two goblins attack from the bridge
2. One goblin shoots arrows from behind rocks
3. Goblin boss emerges on round 3 if combat continues

## Treasure
- 15 sp, 8 cp
- Potion of Healing
- Goblin-crafted dagger (+1 to hit)

## Aftermath
If defeated, the goblins reveal they were driven from their home by "scary shadows" 
in the Whispering Woods.
"""
    
    # Sample lore document
    lore_content = """# The Circle of Stars - Historical Account

## Origins
The Circle of Stars was founded 200 years ago by seven powerful mages who 
united to combat the rising threat of dark magic in the realm.

## Members
The original seven members were:
1. Archmage Eldrin Starweaver (Leader)
2. Gareth the Wise (Divination specialist)
3. Lyanna Moonshadow (Illusion master)
4. Thorek Stormcaller (Evocation expert)
5. Miriel Greenbough (Nature magic)
6. Daven Shadowbane (Abjuration)
7. Celeste Mindbridge (Enchantment)

## The Shadow War
The Circle's greatest challenge came during the Shadow War, when the Shadow Cult 
attempted to summon an entity of pure darkness to consume the realm.

### Key Battles
- **Battle of Thornwood:** First major engagement
- **Siege of Starfall Tower:** The Circle's stronghold under attack
- **The Final Binding:** Ultimate defeat of the Shadow Cult

## Legacy
Though the Circle disbanded after the war, their protective wards still guard 
many locations throughout the realm. Several members, like Gareth, continue 
to serve as guardians in their own ways.
"""
    
    # Write sample files
    files = [
        (temp_dir / "gareth_npc.md", npc_content),
        (temp_dir / "silverbrook_village.md", location_content),
        (temp_dir / "goblin_ambush.md", encounter_content),
        (temp_dir / "circle_of_stars_lore.md", lore_content)
    ]
    
    for file_path, content in files:
        file_path.write_text(content)
    
    return temp_dir


def test_ingestion_and_retrieval():
    """Test the complete ingestion and retrieval pipeline."""
    print("🧪 Testing Campaign Assistant POC")
    print("=" * 50)
    
    # Create sample documents
    print("📝 Creating sample documents...")
    test_dir = create_sample_documents()
    print(f"   Created test documents in: {test_dir}")
    
    # Initialize system
    print("\n🔧 Initializing system...")
    processor = DocumentProcessor()
    vector_store = VectorStore(storage_path="./data/test_chroma_db")
    retriever = CampaignRetriever(vector_store)
    
    # Reset collection for clean test
    vector_store.reset_collection()
    
    # Test document processing
    print("\n📚 Processing documents...")
    documents = processor.process_directory(str(test_dir))
    print(f"   Processed {len(documents)} documents")
    
    for doc in documents:
        print(f"   - {doc.title} ({doc.file_type}, {len(doc.chunks)} chunks)")
    
    # Test vector storage
    print("\n💾 Storing in vector database...")
    vector_store.add_documents(documents)
    
    stats = vector_store.get_collection_stats()
    print(f"   Stored {stats['total_documents']} documents, {stats['total_chunks']} chunks")
    print(f"   Content types: {stats['content_types']}")
    
    # Test retrieval with various queries
    test_queries = [
        "Who is Gareth?",
        "Tell me about Silverbrook Village",
        "What encounters are near the village?",
        "History of the Circle of Stars",
        "What magical items are available?",
        "Where can I find goblins?"
    ]
    
    print("\n🔍 Testing retrieval with sample queries:")
    print("-" * 40)
    
    for query in test_queries:
        print(f"\n❓ Query: '{query}'")
        results = retriever.search(query, max_results=2)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result.source_title} (Score: {result.relevance_score:.3f})")
                print(f"      Type: {result.content_type}")
                print(f"      Content: {result.content[:100]}...")
        else:
            print("   No results found")
    
    # Test entity-specific search
    print(f"\n🎯 Testing entity search for 'Gareth':")
    entity_results = retriever.search_by_entity("Gareth", "character")
    for result in entity_results:
        print(f"   - {result.source_title} (Score: {result.relevance_score:.3f})")
    
    # Cleanup
    print(f"\n🧹 Cleaning up test files...")
    import shutil
    shutil.rmtree(test_dir)
    print("   Test files cleaned up")
    
    print("\n✅ POC test completed successfully!")
    print("\nTo test interactively, run:")
    print("   python main.py interactive")


if __name__ == '__main__':
    test_ingestion_and_retrieval()