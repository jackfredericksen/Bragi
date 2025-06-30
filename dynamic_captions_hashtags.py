import random
import json
from pathlib import Path

# Varied caption starters and styles
CAPTION_STYLES = [
    # Question-based openings
    [
        "What if {topic_lower}?",
        "Have you ever wondered about {topic_lower}?", 
        "Ever notice how {topic_lower}?",
        "Why is {topic_lower} so mysterious?",
        "What does {topic_lower} really mean?",
        "How does {topic_lower} change everything?",
        "What secrets does {topic_lower} hold?",
        "Why does {topic_lower} fascinate us?",
    ],
    
    # Declarative/Mystical openings
    [
        "Deep dive into {topic_lower}",
        "Exploring the mystery of {topic_lower}",
        "The hidden truth about {topic_lower}",
        "Ancient wisdom on {topic_lower}",
        "Modern insights into {topic_lower}",
        "The profound nature of {topic_lower}",
        "Unveiling {topic_lower}",
        "The sacred aspect of {topic_lower}",
    ],
    
    # Experiential openings
    [
        "A journey through {topic_lower}",
        "Experiencing {topic_lower} differently",
        "The reality of {topic_lower}",
        "Living with {topic_lower}",
        "Embracing {topic_lower}",
        "Understanding {topic_lower} deeply",
        "The practice of {topic_lower}",
        "Awakening to {topic_lower}",
    ],
    
    # Contemplative openings
    [
        "Reflecting on {topic_lower}",
        "The deeper meaning of {topic_lower}",
        "Contemplating {topic_lower}",
        "The essence of {topic_lower}",
        "The mystery behind {topic_lower}",
        "Finding truth in {topic_lower}",
        "The wisdom of {topic_lower}",
        "Sacred thoughts on {topic_lower}",
    ]
]

# Diverse hashtag categories
HASHTAG_CATEGORIES = {
    "spiritual_core": [
        "#spirituality", "#awakening", "#consciousness", "#enlightenment",
        "#mindfulness", "#meditation", "#innerwork", "#souljourney",
        "#spiritualwisdom", "#divinetruth", "#sacredknowledge", "#mysticwisdom"
    ],
    
    "philosophy_core": [
        "#philosophy", "#wisdom", "#truth", "#existence", "#reality",
        "#metaphysics", "#ontology", "#epistemology", "#phenomenology",
        "#contemplation", "#reflection", "#inquiry", "#understanding"
    ],
    
    "esoteric_core": [
        "#esoteric", "#occult", "#hermetic", "#gnostic", "#mystical",
        "#alchemical", "#kabbalah", "#tarot", "#astrology", "#numerology",
        "#sacred", "#divine", "#transcendent", "#numinous"
    ],
    
    "consciousness_themes": [
        "#higherself", "#thirdeye", "#chakras", "#aura", "#energy",
        "#vibration", "#frequency", "#manifestation", "#intention",
        "#awareness", "#presence", "#beingness", "#unity"
    ],
    
    "wisdom_traditions": [
        "#ancientwisdom", "#perennialphilosophy", "#universaltruth",
        "#timelesswisdom", "#sacredtradition", "#mystictradition",
        "#spiritualheritage", "#divineteaching", "#eternaltruth"
    ],
    
    "modern_spiritual": [
        "#newage", "#holistic", "#integral", "#transpersonal",
        "#psychedelic", "#plantmedicine", "#shamanwisdom",
        "#quantumconsciousness", "#universalmind", "#cosmicconsciousness"
    ],
    
    "personal_growth": [
        "#selfdiscovery", "#personalgrowth", "#transformation",
        "#healing", "#wholeness", "#integration", "#balance",
        "#harmony", "#peace", "#love", "#compassion", "#wisdom"
    ],
    
    "platform_generic": [
        "#shorts", "#viral", "#fyp", "#foryou", "#explore",
        "#trending", "#deep", "#profound", "#mindblowing", "#perspective"
    ]
}

# Caption endings for variety
CAPTION_ENDINGS = [
    "💭 What are your thoughts?",
    "🤔 How do you see this?",
    "✨ Share your perspective below",
    "🔮 Does this resonate with you?",
    "🌟 What's your experience?",
    "💫 Tell us what you think",
    "🙏 Your insights welcome",
    "💎 Drop your wisdom below",
    "🌙 Share your journey",
    "🔥 What resonates most?",
    "",  # Sometimes no ending
    "",
    "",
]

def generate_dynamic_caption(topic):
    """Generate a varied, engaging caption for the topic"""
    
    # Select random caption style
    style_category = random.choice(CAPTION_STYLES)
    caption_template = random.choice(style_category)
    
    # Format with topic
    topic_lower = topic.lower()
    main_caption = caption_template.format(topic_lower=topic_lower)
    
    # Add optional ending
    ending = random.choice(CAPTION_ENDINGS)
    
    if ending:
        full_caption = f"{main_caption} {ending}"
    else:
        full_caption = main_caption
    
    return full_caption

def generate_varied_hashtags():
    """Generate a varied combination of hashtags"""
    
    hashtag_sets = []
    
    # Always include 2-3 core spiritual/philosophy tags
    core_tags = random.sample(
        HASHTAG_CATEGORIES["spiritual_core"] + HASHTAG_CATEGORIES["philosophy_core"],
        k=random.randint(2, 3)
    )
    hashtag_sets.extend(core_tags)
    
    # Add 1-2 esoteric tags
    esoteric_tags = random.sample(HASHTAG_CATEGORIES["esoteric_core"], k=random.randint(1, 2))
    hashtag_sets.extend(esoteric_tags)
    
    # Add consciousness/awareness tags (50% chance)
    if random.random() < 0.5:
        consciousness_tags = random.sample(HASHTAG_CATEGORIES["consciousness_themes"], k=1)
        hashtag_sets.extend(consciousness_tags)
    
    # Add wisdom tradition tags (30% chance)
    if random.random() < 0.3:
        wisdom_tags = random.sample(HASHTAG_CATEGORIES["wisdom_traditions"], k=1)
        hashtag_sets.extend(wisdom_tags)
    
    # Add modern spiritual tags (40% chance)
    if random.random() < 0.4:
        modern_tags = random.sample(HASHTAG_CATEGORIES["modern_spiritual"], k=1)
        hashtag_sets.extend(modern_tags)
    
    # Add personal growth tags (60% chance)
    if random.random() < 0.6:
        growth_tags = random.sample(HASHTAG_CATEGORIES["personal_growth"], k=random.randint(1, 2))
        hashtag_sets.extend(growth_tags)
    
    # Add platform tags (always include 1-2)
    platform_tags = random.sample(HASHTAG_CATEGORIES["platform_generic"], k=random.randint(1, 2))
    hashtag_sets.extend(platform_tags)
    
    # Remove duplicates and limit total
    unique_hashtags = list(dict.fromkeys(hashtag_sets))  # Preserve order while removing dupes
    
    # Limit to reasonable number (8-12 hashtags)
    max_hashtags = random.randint(8, 12)
    final_hashtags = unique_hashtags[:max_hashtags]
    
    return final_hashtags

def create_tiktok_caption(topic):
    """Create complete TikTok caption with topic and hashtags"""
    
    # Generate dynamic caption
    main_caption = generate_dynamic_caption(topic)
    
    # Generate varied hashtags
    hashtags = generate_varied_hashtags()
    hashtag_string = " ".join(hashtags)
    
    # Combine
    full_caption = f"{main_caption} {hashtag_string}"
    
    # Ensure it's not too long for TikTok (150 char recommended)
    if len(full_caption) > 150:
        # Trim hashtags if needed
        while len(full_caption) > 150 and len(hashtags) > 6:
            hashtags.pop()
            hashtag_string = " ".join(hashtags)
            full_caption = f"{main_caption} {hashtag_string}"
    
    return full_caption

def create_youtube_title_and_description(topic):
    """Create YouTube title and description with maximum variety"""
    
    # Expanded title variations
    title_templates = [
        "{topic} - Ancient Wisdom Revealed",
        "The Truth About {topic}",
        "Understanding {topic} Deeply", 
        "{topic} - A Spiritual Perspective",
        "The Mystery of {topic}",
        "{topic} - Profound Insights",
        "Exploring {topic} - Mystical Philosophy",
        "{topic} - Timeless Wisdom",
        "The Nature of {topic}",
        "{topic} - Sacred Knowledge",
        "Contemplating {topic}",
        "{topic} - Higher Understanding",
        "The Secret of {topic}",
        "{topic} - Spiritual Awakening",
        "Discovering {topic}",
        "{topic} - Inner Truth",
        "The Path of {topic}",
        "{topic} - Cosmic Wisdom",
        "Unveiling {topic}",
        "{topic} - Divine Insight",
        "The Journey of {topic}",
        "{topic} - Metaphysical Truth"
    ]
    
    title_template = random.choice(title_templates)
    title = f"{title_template.format(topic=topic)} #Shorts"
    
    # Greatly expanded description variations
    description_templates = [
        # Wisdom-focused
        "Dive deep into {topic_lower} through the lens of ancient wisdom and modern insight.",
        "Exploring {topic_lower} from a spiritual and philosophical perspective.", 
        "A contemplative journey into the nature of {topic_lower}.",
        "Ancient teachings meet modern understanding in this exploration of {topic_lower}.",
        "Timeless wisdom on {topic_lower} for the modern seeker.",
        "Sacred insights into {topic_lower} and its deeper meaning.",
        
        # Mystery-focused
        "Uncover the hidden mysteries surrounding {topic_lower} in this profound exploration.",
        "What ancient sages knew about {topic_lower} that we're only beginning to understand.",
        "The secret teachings about {topic_lower} revealed through mystical philosophy.",
        "Journey beyond the veil to discover the true nature of {topic_lower}.",
        
        # Experience-focused
        "A mystical exploration of {topic_lower} and its profound implications for human experience.",
        "How {topic_lower} transforms our understanding of reality and existence.",
        "Experience {topic_lower} through the eyes of mystics and philosophers throughout history.",
        "The transformative power of {topic_lower} in spiritual awakening and growth.",
        
        # Knowledge-focused
        "Philosophical reflections on {topic_lower} and its significance in our lives.",
        "What modern science and ancient wisdom tell us about {topic_lower}.",
        "The intersection of spirituality and {topic_lower} in contemporary understanding.",
        "Bridging ancient mysticism and modern insight in this study of {topic_lower}.",
        
        # Journey-focused
        "Embark on a spiritual journey to understand the depths of {topic_lower}.",
        "Navigate the sacred landscape of {topic_lower} with wisdom from mystics and sages.",
        "A guided meditation on the profound implications of {topic_lower}.",
        "Walk the path of understanding through the gateway of {topic_lower}.",
        
        # Awakening-focused
        "Awaken to new possibilities through a deeper understanding of {topic_lower}.",
        "How {topic_lower} serves as a catalyst for spiritual transformation and growth.",
        "The role of {topic_lower} in the evolution of human consciousness.",
        "Discover how {topic_lower} opens doorways to higher states of awareness."
    ]
    
    description_template = random.choice(description_templates)
    main_description = description_template.format(topic_lower=topic.lower())
    
    # Add varied call-to-action endings
    cta_endings = [
        "What insights does this bring to your spiritual journey?",
        "How has this perspective shifted your understanding?", 
        "Share your thoughts on this mystical exploration below.",
        "What resonates most deeply with your inner wisdom?",
        "How does this align with your spiritual practices?",
        "What questions arise from this contemplation?",
        "Join the conversation about consciousness and awakening.",
        "Dive deeper into the mysteries that call to you.",
        ""  # Sometimes no CTA
    ]
    
    cta = random.choice(cta_endings)
    
    # Add varied hashtags for YouTube
    youtube_hashtags = generate_varied_hashtags()
    # Add some YouTube-specific tags
    youtube_specific = ["#youtube", "#shorts", "#philosophy", "#spirituality", "#wisdom", "#deepthoughts"]
    youtube_hashtags.extend(random.sample(youtube_specific, 2))
    
    # Remove duplicates
    youtube_hashtags = list(dict.fromkeys(youtube_hashtags))[:15]  # YouTube allows more hashtags
    
    hashtag_string = " ".join(youtube_hashtags)
    
    # Combine description parts
    if cta:
        full_description = f"{main_description}\n\n{cta}\n\n{hashtag_string}"
    else:
        full_description = f"{main_description}\n\n{hashtag_string}"
    
    return title, full_description

def track_caption_hashtag_usage():
    """Track usage to ensure variety over time"""
    usage_file = Path("caption_hashtag_usage.json")
    
    # Load existing usage
    usage_data = {"captions": [], "hashtag_combos": []}
    if usage_file.exists():
        try:
            with open(usage_file, 'r') as f:
                usage_data = json.load(f)
        except:
            pass
    
    return usage_data

def save_caption_hashtag_usage(caption, hashtags):
    """Save usage for variety tracking"""
    usage_file = Path("caption_hashtag_usage.json")
    usage_data = track_caption_hashtag_usage()
    
    # Add new usage
    usage_data["captions"].append(caption)
    usage_data["hashtag_combos"].append(hashtags)
    
    # Keep only last 50 to avoid infinite growth
    usage_data["captions"] = usage_data["captions"][-50:]
    usage_data["hashtag_combos"] = usage_data["hashtag_combos"][-50:]
    
    # Save
    try:
        with open(usage_file, 'w') as f:
            json.dump(usage_data, f)
    except:
        pass  # Ignore save errors

def get_caption_variety_stats():
    """Get statistics on caption/hashtag variety"""
    usage_data = track_caption_hashtag_usage()
    
    stats = {
        "total_captions_used": len(usage_data["captions"]),
        "unique_captions": len(set(usage_data["captions"])),
        "total_hashtag_combos": len(usage_data["hashtag_combos"]),
        "variety_score": 0
    }
    
    if stats["total_captions_used"] > 0:
        stats["variety_score"] = (stats["unique_captions"] / stats["total_captions_used"]) * 100
    
    return stats

def test_caption_variety(topic, count=5):
    """Test caption variety for a given topic"""
    print(f"🎬 Caption Variety Test for: {topic}")
    print("=" * 50)
    
    for i in range(count):
        print(f"\n{i+1}. TikTok Caption:")
        tiktok_caption = create_tiktok_caption(topic)
        print(f"   {tiktok_caption}")
        
        print(f"\n   YouTube:")
        yt_title, yt_desc = create_youtube_title_and_description(topic)
        print(f"   Title: {yt_title}")
        print(f"   Desc: {yt_desc[:100]}...")
        print("-" * 30)