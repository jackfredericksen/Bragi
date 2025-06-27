import anthropic
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
TOPIC_FILE = "topics.txt"

def expand_topics():
    system_prompt = "You are an enlightened philosopher helping generate unique esoteric content ideas for social media videos."
    user_prompt = (
        "Give me 5 new short-form content topics in the spirit of Alan Watts and Terence McKenna. "
        "Keep them poetic, mystical, and mysterious. Each on its own line."
    )

    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=300,
        temperature=1.1,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )

    new_topics = response.content[0].text.strip().split("\n")
    new_topics = [t.strip("•- ").strip() for t in new_topics if t.strip()]

    with open(TOPIC_FILE, "a", encoding="utf-8") as f:
        for topic in new_topics:
            f.write(f"{topic}\n")

    print(f"[+] Added {len(new_topics)} new topics to {TOPIC_FILE}")

if __name__ == "__main__":
    expand_topics()
