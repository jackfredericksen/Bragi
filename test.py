#!/usr/bin/env python3
"""
Test Dynamic Captions & Hashtags
See how varied and engaging your captions will be
"""

from dynamic_captions_hashtags import (
    create_tiktok_caption,
    create_youtube_title_and_description,
    get_caption_variety_stats,
    test_caption_variety,
    HASHTAG_CATEGORIES
)
import random

def test_caption_system():
    """Test the dynamic caption system"""
    print("🎬 Dynamic Caption & Hashtag System Test")
    print("=" * 50)
    
    # Test topics
    test_topics = [
        "The nature of consciousness",
        "Time as an illusion", 
        "Ego death and rebirth",
        "Sacred geometry",
        "Quantum consciousness"
    ]
    
    print("🧪 Testing Caption Variety...")
    print("=" * 30)
    
    for i, topic in enumerate(test_topics, 1):
        print(f"\n{i}. Topic: {topic}")
        print("-" * 25)
        
        # TikTok caption
        tiktok_caption = create_tiktok_caption(topic)
        print(f"TikTok: {tiktok_caption}")
        
        # YouTube
        yt_title, yt_desc = create_youtube_title_and_description(topic)
        print(f"YouTube Title: {yt_title}")
        print(f"YouTube Desc: {yt_desc[:80]}...")
        
        if i < len(test_topics):  # Don't add separator after last item
            print()

def show_hashtag_categories():
    """Show available hashtag categories"""
    print("\n📋 AVAILABLE HASHTAG CATEGORIES")
    print("=" * 40)
    
    for category, tags in HASHTAG_CATEGORIES.items():
        print(f"\n{category.upper().replace('_', ' ')} ({len(tags)} tags):")
        # Show first few examples
        sample_tags = tags[:6]
        print(f"   {' '.join(sample_tags)}")
        if len(tags) > 6:
            print(f"   ... and {len(tags) - 6} more")

def test_hashtag_variety():
    """Test hashtag combination variety"""
    print("\n🏷️ HASHTAG COMBINATION VARIETY TEST")
    print("=" * 45)
    
    from dynamic_captions_hashtags import generate_varied_hashtags
    
    print("Generating 5 different hashtag combinations:\n")
    
    for i in range(5):
        hashtags = generate_varied_hashtags()
        hashtag_string = " ".join(hashtags)
        print(f"{i+1}. {hashtag_string}")
    
    print(f"\n💡 Each combination is unique and covers different spiritual themes!")

def show_caption_styles():
    """Show different caption style examples"""
    print("\n✍️ CAPTION STYLE VARIATIONS")
    print("=" * 35)
    
    topic = "consciousness"
    
    print(f"Topic: {topic}")
    print("Different style variations:\n")
    
    # Generate several variations
    for i in range(6):
        caption = create_tiktok_caption(topic)
        # Extract just the main caption part (before hashtags)
        main_caption = caption.split('#')[0].strip()
        print(f"{i+1}. {main_caption}")

def analyze_current_variety():
    """Analyze current variety statistics"""
    print("\n📊 CURRENT VARIETY STATISTICS")
    print("=" * 35)
    
    stats = get_caption_variety_stats()
    
    print(f"Total captions generated: {stats['total_captions_used']}")
    print(f"Unique captions: {stats['unique_captions']}")
    print(f"Variety score: {stats['variety_score']:.1f}%")
    
    if stats['total_captions_used'] == 0:
        print("\n💡 No captions generated yet - run main.py to start tracking!")
    elif stats['variety_score'] > 80:
        print("\n✅ Excellent variety! Your captions are highly diverse.")
    elif stats['variety_score'] > 60:
        print("\n🟡 Good variety, but could be more diverse.")
    else:
        print("\n🔴 Low variety - captions may be repetitive.")

def interactive_test():
    """Interactive caption testing"""
    print("\n🎯 INTERACTIVE CAPTION TESTER")
    print("=" * 35)
    
    while True:
        topic = input("\nEnter a topic to test (or 'quit' to exit): ").strip()
        
        if topic.lower() in ['quit', 'exit', 'q']:
            break
        
        if not topic:
            topic = "consciousness"  # Default
        
        print(f"\n🎬 Testing: {topic}")
        print("-" * 20)
        
        # Generate content
        tiktok_caption = create_tiktok_caption(topic)
        yt_title, yt_desc = create_youtube_title_and_description(topic)
        
        print(f"TikTok: {tiktok_caption}")
        print(f"YouTube: {yt_title}")
        print(f"Description: {yt_desc[:100]}...")

def main():
    """Main testing interface"""
    while True:
        print("\n🎨 Dynamic Caption & Hashtag Tester")
        print("=" * 40)
        print("1. Test caption variety")
        print("2. Show hashtag categories") 
        print("3. Test hashtag combinations")
        print("4. Show caption style variations")
        print("5. Analyze current variety")
        print("6. Interactive tester")
        print("0. Exit")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "0":
            print("👋 Goodbye!")
            break
        elif choice == "1":
            test_caption_system()
        elif choice == "2":
            show_hashtag_categories()
        elif choice == "3":
            test_hashtag_variety()
        elif choice == "4":
            show_caption_styles()
        elif choice == "5":
            analyze_current_variety()
        elif choice == "6":
            interactive_test()
        else:
            print("❌ Invalid option")

if __name__ == "__main__":
    main()