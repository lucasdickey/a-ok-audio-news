#!/usr/bin/env python3

# Simple test to demonstrate V3 content filtering
import re

def clean_agent_output(content: str) -> str:
    """Remove AI search process text and other meta-commentary"""
    # Remove search process indicators
    search_patterns = [
        r"Let me search.*?\n",
        r"I'll search for.*?\n", 
        r"Based on the search results.*?\n",
        r"Let me verify.*?\n",
        r"I need to search.*?\n",
        r"I'll look for.*?\n",
        r"Let me find.*?\n"
    ]
    
    cleaned = content
    for pattern in search_patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE | re.MULTILINE)
    
    # Remove leading/trailing whitespace and empty lines
    lines = [line.strip() for line in cleaned.split('\n') if line.strip()]
    return '\n'.join(lines)

# Test with actual V1 problematic output
v1_output = """Let me search for current information to verify and enhance these stories.

Let me search for information about OpenAI's latest models.

Based on the search results, I'll polish the script while maintaining accuracy and proper citations. Here's the improved version:

OPENING:
"Hello world… welcome back to Apes On Knowledge, your daily dose of distilled AI news from across the planet. I'm your host, A-OK Newsbot… Let's get into today's most important headlines in artificial intelligence."

STORY 1: 
OpenAI Unveils Revolutionary Visual Reasoning Models: o3 and o4-mini

OpenAI has released two groundbreaking AI models — o3 and o4-mini..."""

print("🔍 ORIGINAL V1 OUTPUT:")
print("=" * 50)
print(v1_output)
print("\n" + "=" * 50)

print("\n🧹 V3 FILTERED OUTPUT:")
print("=" * 50)
cleaned = clean_agent_output(v1_output)
print(cleaned)
print("=" * 50)

print(f"\n📊 COMPARISON:")
print(f"Original length: {len(v1_output)} chars")
print(f"Cleaned length: {len(cleaned)} chars")
print(f"Search leakage removed: {len(v1_output) - len(cleaned)} chars")

# Check for remaining search indicators
search_indicators = ["Let me search", "I'll search for", "Based on the search results"]
has_leakage = any(indicator in cleaned for indicator in search_indicators)
print(f"Clean output: {'✅ Yes' if not has_leakage else '❌ No'}") 