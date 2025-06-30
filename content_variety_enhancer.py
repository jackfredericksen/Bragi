# Enhanced topic and background variety system

import random
import json
from pathlib import Path

# Expanded esoteric topics database
EXPANDED_TOPICS = [
    # Original topics
    "The illusion of time",
    "Ego death and the dissolution of self",
    "The fractal nature of the universe",
    "Synchronicity and cosmic alignment",
    "What is consciousness?",
    "The psychedelic experience as initiation",
    "Non-duality and the self",
    "Language as a trap of thought",
    "Dreams and simulated realities",
    "Reincarnation and the eternal return",
    "Time loops and higher dimensions",
    
    # Consciousness & Awareness
    "The observer and the observed",
    "Levels of consciousness",
    "The witness consciousness",
    "Collective consciousness and the noosphere",
    "Machine consciousness and AI awakening",
    "The hard problem of consciousness",
    "Consciousness as fundamental reality",
    "The stream of consciousness",
    "Altered states and expanded awareness",
    "Consciousness after death",
    
    # Reality & Perception
    "Maya and the veil of illusion",
    "The holographic principle of reality",
    "Simulation theory and nested realities",
    "The observer effect in quantum mechanics",
    "Reality as information processing",
    "The multiverse and infinite possibilities",
    "Parallel dimensions and alternate selves",
    "The nature of space and time",
    "Reality tunnels and belief systems",
    "Consensus reality vs. personal reality",
    
    # Mystical & Spiritual
    "The mystical experience",
    "Unity consciousness and oneness",
    "The dark night of the soul",
    "Spiritual bypassing and shadow work",
    "The gateless gate of enlightenment",
    "Sacred geometry and divine patterns",
    "The chakra system and energy bodies",
    "Kundalini awakening and transformation",
    "The hermetic principles",
    "Ancient wisdom in modern times",
    
    # Philosophy & Metaphysics
    "The paradox of free will",
    "Determinism vs. quantum indeterminacy",
    "The mind-body problem",
    "Emergent properties of complex systems",
    "The anthropic principle",
    "Nihilism and the search for meaning",
    "Existential dread and cosmic insignificance",
    "The absurd condition of human existence",
    "Phenomenology and lived experience",
    "The death of God and rebirth of mystery",
    
    # Technology & Future
    "Artificial intelligence and consciousness",
    "Transhumanism and human enhancement",
    "Virtual reality and digital realms",
    "The singularity and technological transcendence",
    "Cybernetics and human-machine interfaces",
    "Blockchain and decentralized consciousness",
    "Quantum computing and reality simulation",
    "Digital immortality and uploaded minds",
    "The metaverse as collective dreaming",
    "Technology as extension of consciousness",
    
    # Ancient Wisdom & Traditions
    "The Akashic records and cosmic memory",
    "Platonic ideals and archetypal forms",
    "The Tao and the flow of existence",
    "Buddhist emptiness and dependent origination",
    "Hindu concepts of Brahman and Atman",
    "Gnostic teachings on divine spark",
    "Kabbalalistic tree of life",
    "Shamanic journeying and plant teachers",
    "Indigenous wisdom and earth connection",
    "Alchemy and inner transformation",
    
    # Science & Spirituality
    "Quantum entanglement and cosmic connection",
    "The double-slit experiment and consciousness",
    "String theory and dimensional realities",
    "Morphic resonance and collective memory",
    "Chaos theory and the butterfly effect",
    "The Gaia hypothesis and planetary consciousness",
    "Biophotons and cellular communication",
    "DNA as cosmic antenna",
    "Sacred plants and neuroplasticity",
    "Psychedelics and neural networks",
    
    # Death & Transcendence
    "The bardo and intermediate states",
    "Near-death experiences and beyond",
    "The continuity of consciousness",
    "Death as transformation, not ending",
    "Psychedelic death and rebirth",
    "The ego's fear of dissolution",
    "Preparing for conscious dying",
    "Grief as doorway to deeper love",
    "Ancestral wisdom and guidance",
    "The eternal now beyond time",
]

# Expanded background video categories
BACKGROUND_CATEGORIES = [
    # Cosmic & Space
    ["galaxy", "nebula", "stars", "cosmic", "space", "astronomy", "planets"],
    ["supernova", "black hole", "solar system", "milky way", "cosmos", "universe"],
    ["aurora", "northern lights", "solar flare", "celestial", "astral"],
    
    # Natural Phenomena
    ["ocean waves", "deep ocean", "underwater", "marine life", "coral reef"],
    ["forest", "trees", "nature", "wilderness", "jungle", "rainforest"],
    ["mountains", "landscape", "canyon", "desert", "geological"],
    ["clouds", "storm", "lightning", "weather", "atmospheric"],
    ["waterfall", "river", "flowing water", "stream", "lake"],
    ["fire", "flames", "lava", "volcanic", "magma", "heat"],
    ["ice", "snow", "frozen", "glacier", "crystal", "winter"],
    
    # Abstract & Artistic
    ["abstract", "geometric", "patterns", "shapes", "design"],
    ["fractal", "mandala", "kaleidoscope", "symmetry", "spiral"],
    ["liquid", "fluid", "flowing", "organic", "smooth"],
    ["particle", "dust", "smoke", "vapor", "ethereal"],
    ["light", "rays", "beams", "glow", "luminous", "bright"],
    ["dark", "shadow", "mysterious", "noir", "atmospheric"],
    ["color", "rainbow", "spectrum", "vibrant", "chromatic"],
    ["texture", "surface", "material", "fabric", "organic"],
    
    # Psychedelic & Trippy
    ["psychedelic", "trippy", "surreal", "dreamy", "otherworldly"],
    ["meditation", "spiritual", "zen", "peaceful", "tranquil"],
    ["hypnotic", "mesmerizing", "trance", "rhythmic", "pulsing"],
    ["morphing", "transformation", "changing", "evolution"],
    ["tunnel", "vortex", "portal", "gateway", "passage"],
    ["mirror", "reflection", "symmetrical", "infinite", "loop"],
    
    # Technology & Digital
    ["digital", "cyber", "neon", "futuristic", "tech"],
    ["circuit", "electronic", "computer", "data", "binary"],
    ["hologram", "projection", "virtual", "3d", "dimensional"],
    ["ai", "artificial", "robotic", "machine", "synthetic"],
    
    # Microscopic & Scientific
    ["microscopic", "cellular", "molecular", "atomic", "quantum"],
    ["bacteria", "virus", "organism", "biological", "medical"],
    ["chemistry", "reaction", "experiment", "laboratory"],
    ["crystal", "mineral", "geological", "structure", "formation"],
]

def get_varied_topic():
    """Get a topic with better variety tracking"""
    topic_file = Path("topics.txt")
    used_topics_file = Path("used_topics.json")
    
    # Load used topics tracking
    used_topics = []
    if used_topics_file.exists():
        try:
            with open(used_topics_file, 'r') as f:
                used_topics = json.load(f)
        except:
            used_topics = []
    
    # Get available topics (file topics + expanded topics)
    available_topics = EXPANDED_TOPICS.copy()
    
    # Add custom topics from file if it exists
    if topic_file.exists():
        with open(topic_file, 'r', encoding='utf-8') as f:
            custom_topics = [line.strip() for line in f if line.strip()]
            available_topics.extend(custom_topics)
    
    # Remove recently used topics to avoid repetition
    if len(used_topics) > 20:  # Keep last 20 topics in memory
        used_topics = used_topics[-20:]
    
    # Filter out recently used topics
    fresh_topics = [topic for topic in available_topics if topic not in used_topics]
    
    # If we've used all topics, reset and use all topics again
    if not fresh_topics:
        fresh_topics = available_topics
        used_topics = []
        print("🔄 Topic pool refreshed - starting new cycle")
    
    # Select random topic
    selected_topic = random.choice(fresh_topics)
    
    # Track usage
    used_topics.append(selected_topic)
    
    # Save usage tracking
    try:
        with open(used_topics_file, 'w') as f:
            json.dump(used_topics, f)
    except:
        pass  # Ignore save errors
    
    return selected_topic

def get_varied_background_search():
    """Get varied background video search terms"""
    used_searches_file = Path("used_searches.json")
    
    # Load used searches tracking
    used_searches = []
    if used_searches_file.exists():
        try:
            with open(used_searches_file, 'r') as f:
                used_searches = json.load(f)
        except:
            used_searches = []
    
    # Keep last 15 searches in memory
    if len(used_searches) > 15:
        used_searches = used_searches[-15:]
    
    # Flatten all background categories
    all_searches = []
    for category in BACKGROUND_CATEGORIES:
        all_searches.extend(category)
    
    # Filter out recently used searches
    fresh_searches = [search for search in all_searches if search not in used_searches]
    
    # If we've used most searches, reset
    if len(fresh_searches) < 5:
        fresh_searches = all_searches
        used_searches = []
        print("🔄 Background search pool refreshed")
    
    # Select random search term
    selected_search = random.choice(fresh_searches)
    
    # Track usage
    used_searches.append(selected_search)
    
    # Save usage tracking
    try:
        with open(used_searches_file, 'w') as f:
            json.dump(used_searches, f)
    except:
        pass
    
    return selected_search

def auto_expand_topics():
    """Automatically generate new topics using Claude"""
    try:
        import anthropic
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # Generate new topics in different categories
        categories = [
            "consciousness and awareness",
            "reality and perception", 
            "mystical experiences",
            "technology and future",
            "ancient wisdom",
            "science and spirituality",
            "death and transcendence",
            "philosophy and existence"
        ]
        
        category = random.choice(categories)
        
        prompt = f"""Generate 5 unique, thought-provoking topics related to {category} for philosophical content in the style of Alan Watts and Terence McKenna. 

Make them:
- Mysterious and intriguing
- Suitable for 60-90 second explorations
- Original and not commonly discussed
- Poetic and evocative

Format: One topic per line, no numbers or bullets."""

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=300,
            temperature=1.2,
            system="You are a mystical philosopher generating unique content ideas.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        new_topics = [line.strip() for line in response.content[0].text.strip().split('\n') if line.strip()]
        
        # Add to topics file
        topics_file = Path("topics.txt")
        with open(topics_file, 'a', encoding='utf-8') as f:
            for topic in new_topics:
                f.write(f"{topic}\n")
        
        print(f"✨ Added {len(new_topics)} new auto-generated topics")
        return new_topics
        
    except Exception as e:
        print(f"⚠️ Auto topic generation failed: {e}")
        return []

def create_expanded_topics_file():
    """Create an initial expanded topics file"""
    topics_file = Path("topics.txt")
    
    # If file doesn't exist or is small, populate with expanded topics
    if not topics_file.exists() or topics_file.stat().st_size < 500:
        with open(topics_file, 'w', encoding='utf-8') as f:
            for topic in EXPANDED_TOPICS:
                f.write(f"{topic}\n")
        print(f"📝 Created expanded topics file with {len(EXPANDED_TOPICS)} topics")

# Usage tracking for insights
def get_content_variety_stats():
    """Show variety statistics"""
    used_topics_file = Path("used_topics.json")
    used_searches_file = Path("used_searches.json")
    
    stats = {
        "total_available_topics": len(EXPANDED_TOPICS),
        "used_topics": 0,
        "total_search_terms": sum(len(cat) for cat in BACKGROUND_CATEGORIES),
        "used_searches": 0
    }
    
    if used_topics_file.exists():
        try:
            with open(used_topics_file, 'r') as f:
                used_topics = json.load(f)
                stats["used_topics"] = len(set(used_topics))
        except:
            pass
    
    if used_searches_file.exists():
        try:
            with open(used_searches_file, 'r') as f:
                used_searches = json.load(f)
                stats["used_searches"] = len(set(used_searches))
        except:
            pass
    
    return stats