#!/usr/bin/env python3
"""
Content Variety Manager
Track and manage topic and background variety
"""

import json
from pathlib import Path
from content_variety_enhancer import (
    get_content_variety_stats, 
    auto_expand_topics, 
    EXPANDED_TOPICS,
    BACKGROUND_CATEGORIES
)

def show_variety_dashboard():
    """Display content variety statistics"""
    stats = get_content_variety_stats()
    
    print("📊 CONTENT VARIETY DASHBOARD")
    print("=" * 40)
    print(f"📝 Topics:")
    print(f"   Available: {stats['total_available_topics']}")
    print(f"   Used: {stats['used_topics']}")
    
    if stats['used_topics'] > 0:
        topic_variety = (stats['used_topics'] / stats['total_available_topics']) * 100
        print(f"   Variety: {topic_variety:.1f}% explored")
    
    print(f"\n🎬 Background Videos:")
    print(f"   Search terms available: {stats['total_search_terms']}")
    print(f"   Search terms used: {stats['used_searches']}")
    
    if stats['used_searches'] > 0:
        search_variety = (stats['used_searches'] / stats['total_search_terms']) * 100
        print(f"   Variety: {search_variety:.1f}% explored")
    
    # Show freshness status
    print(f"\n🔄 Freshness Status:")
    if stats['used_topics'] < stats['total_available_topics'] * 0.3:
        print("   Topics: 🟢 Fresh (lots of unused content)")
    elif stats['used_topics'] < stats['total_available_topics'] * 0.7:
        print("   Topics: 🟡 Moderate (some repetition possible)")
    else:
        print("   Topics: 🔴 Stale (high repetition likely)")
    
    if stats['used_searches'] < stats['total_search_terms'] * 0.3:
        print("   Backgrounds: 🟢 Fresh (lots of unused searches)")
    elif stats['used_searches'] < stats['total_search_terms'] * 0.7:
        print("   Backgrounds: 🟡 Moderate (some repetition possible)")
    else:
        print("   Backgrounds: 🔴 Stale (high repetition likely)")

def show_recent_content():
    """Show recently used topics and searches"""
    used_topics_file = Path("used_topics.json")
    used_searches_file = Path("used_searches.json")
    
    print("\n📋 RECENT CONTENT")
    print("=" * 40)
    
    # Recent topics
    if used_topics_file.exists():
        try:
            with open(used_topics_file, 'r') as f:
                used_topics = json.load(f)
                recent_topics = used_topics[-10:]  # Last 10
                
            print("📝 Last 10 Topics:")
            for i, topic in enumerate(reversed(recent_topics), 1):
                print(f"   {i:2d}. {topic}")
        except:
            print("📝 No topic history found")
    else:
        print("📝 No topic history found")
    
    # Recent searches
    if used_searches_file.exists():
        try:
            with open(used_searches_file, 'r') as f:
                used_searches = json.load(f)
                recent_searches = used_searches[-10:]  # Last 10
                
            print("\n🎬 Last 10 Background Searches:")
            for i, search in enumerate(reversed(recent_searches), 1):
                print(f"   {i:2d}. {search}")
        except:
            print("\n🎬 No search history found")
    else:
        print("\n🎬 No search history found")

def reset_variety_tracking():
    """Reset variety tracking to start fresh"""
    used_topics_file = Path("used_topics.json")
    used_searches_file = Path("used_searches.json")
    
    if used_topics_file.exists():
        used_topics_file.unlink()
    if used_searches_file.exists():
        used_searches_file.unlink()
    
    print("🔄 Variety tracking reset - all content will be fresh again!")

def force_expand_topics(count=10):
    """Force generate new topics"""
    print(f"🧠 Generating {count} new topics with Claude...")
    
    generated_count = 0
    for i in range(count // 5 + 1):  # Generate in batches of 5
        new_topics = auto_expand_topics()
        generated_count += len(new_topics)
        if generated_count >= count:
            break
    
    print(f"✅ Generated {generated_count} new topics!")

def show_topic_categories():
    """Show available topic categories"""
    print("\n📚 TOPIC CATEGORIES")
    print("=" * 40)
    
    categories = {
        "Consciousness & Awareness": [t for t in EXPANDED_TOPICS if any(word in t.lower() for word in ['consciousness', 'awareness', 'observer', 'witness'])],
        "Reality & Perception": [t for t in EXPANDED_TOPICS if any(word in t.lower() for word in ['reality', 'illusion', 'perception', 'maya'])],
        "Mystical & Spiritual": [t for t in EXPANDED_TOPICS if any(word in t.lower() for word in ['mystical', 'spiritual', 'enlightenment', 'awakening'])],
        "Philosophy & Metaphysics": [t for t in EXPANDED_TOPICS if any(word in t.lower() for word in ['philosophy', 'metaphysics', 'existence', 'meaning'])],
        "Technology & Future": [t for t in EXPANDED_TOPICS if any(word in t.lower() for word in ['technology', 'ai', 'future', 'digital'])],
        "Death & Transcendence": [t for t in EXPANDED_TOPICS if any(word in t.lower() for word in ['death', 'transcendence', 'bardo', 'dying'])],
    }
    
    for category, topics in categories.items():
        print(f"\n{category} ({len(topics)} topics):")
        for topic in topics[:3]:  # Show first 3 examples
            print(f"   • {topic}")
        if len(topics) > 3:
            print(f"   ... and {len(topics) - 3} more")

def show_background_categories():
    """Show available background categories"""
    print("\n🎨 BACKGROUND CATEGORIES")
    print("=" * 40)
    
    category_names = [
        "Cosmic & Space", "Natural Phenomena", "Abstract & Artistic", 
        "Psychedelic & Trippy", "Technology & Digital", "Microscopic & Scientific"
    ]
    
    for i, (name, category) in enumerate(zip(category_names, BACKGROUND_CATEGORIES[:6])):
        print(f"\n{name} ({len(category)} search terms):")
        print(f"   {', '.join(category[:5])}")
        if len(category) > 5:
            print(f"   ... and {len(category) - 5} more")

def main():
    """Main variety manager interface"""
    print("🎨 Content Variety Manager")
    print("=" * 40)
    
    while True:
        print("\n🎛️ OPTIONS:")
        print("1. Show variety dashboard")
        print("2. Show recent content")
        print("3. Show topic categories")
        print("4. Show background categories")
        print("5. Generate new topics")
        print("6. Reset variety tracking")
        print("0. Exit")
        
        try:
            choice = input("\nSelect option: ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                show_variety_dashboard()
            elif choice == "2":
                show_recent_content()
            elif choice == "3":
                show_topic_categories()
            elif choice == "4":
                show_background_categories()
            elif choice == "5":
                try:
                    count = int(input("How many new topics to generate? (default 10): ") or "10")
                    force_expand_topics(count)
                except ValueError:
                    print("❌ Invalid number")
            elif choice == "6":
                confirm = input("Are you sure you want to reset variety tracking? (y/N): ")
                if confirm.lower() == 'y':
                    reset_variety_tracking()
            else:
                print("❌ Invalid option")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()