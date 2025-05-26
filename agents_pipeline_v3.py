import anthropic
import os
import logging
from typing import List, Dict
from datetime import date as dt_date
import re

# Multi-agent pipeline for "Apes On Knowledge" - AI Daily News (Version 3)
# Features:
# - Explicit content filtering to prevent search leakage
# - Improved agent prompts with clear output format requirements
# - Better citation enforcement
# - Content validation at each step

# Initialize the Anthropic client
anthropic_client = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))

def run_anthropic_chat(messages: List[Dict], model="claude-3-5-sonnet-20241022", max_tokens=8192) -> str:
    response = anthropic_client.messages.create(
        model=model,
        messages=messages,
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search"
        }],
        max_tokens=max_tokens
    )
    # Extract text content from the response
    text_content = ""
    for content_block in response.content:
        if hasattr(content_block, "text"):
            text_content += content_block.text
    return text_content.strip()

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

# Agent 1: Research collector with strict output format
def collect_research(date: str) -> str:
    from datetime import datetime, timedelta
    
    target_date = datetime.strptime(date, "%Y-%m-%d")
    yesterday = (target_date - timedelta(days=1)).strftime("%Y-%m-%d")
    
    messages = [
        {
            "role": "user", 
            "content": f"""
You are the Research Agent for "Apes On Knowledge" - AI Daily News. Find real AI news from the LAST 24 HOURS ONLY ({yesterday} to {date}).

MANDATORY REQUIREMENTS:
1. Use web search to find actual recent news
2. Only include stories published on {date} or {yesterday}
3. Find 15-20 stories minimum
4. Include exact source citations for each story

CRITICAL OUTPUT FORMAT:
Return ONLY a list of stories in this exact format:

STORY: [Exact headline from source]
SOURCE: [Publication name] - [Article title/URL]
DATE: {date} or {yesterday}
SUMMARY: [2-3 sentences about what happened]
IMPACT: [Why it matters to AI practitioners]

---

STORY: [Next headline]
...continue for all stories...

SEARCH STRATEGY:
1. "AI news {date}"
2. "artificial intelligence breaking news {date}"
3. Company searches: "OpenAI news {date}", "Google AI {date}", etc.
4. Source searches: "site:techcrunch.com AI {date}"

DO NOT include any search commentary, explanations, or process notes in your output. Return ONLY the formatted story list.
"""
        }
    ]
    
    result = run_anthropic_chat(messages, max_tokens=8192)
    return clean_agent_output(result)

# Agent 2: Prioritizer with exact count requirement
def prioritize_and_filter(research: str) -> str:
    from datetime import datetime, timedelta
    
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    messages = [
        {
            "role": "user", 
            "content": f"""
Select EXACTLY 10 stories from the research below. Return ONLY the formatted story list.

REQUIREMENTS:
- EXACTLY 10 stories (count them)
- Only stories from {today} or {yesterday}
- Must have verified sources
- High impact for AI practitioners

OUTPUT FORMAT (return this exact format):

STORY 1: [Headline]
SOURCE: [Publication] - [Article title]
DATE: {today} or {yesterday}
SUMMARY: [What happened - 2-3 sentences]
IMPACT: [Why it matters to AI practitioners]

STORY 2: [Headline]
...continue for all 10 stories...

Research to analyze:
{research}

Return ONLY the 10 formatted stories. No commentary or explanations.
"""
        }
    ]
    
    result = run_anthropic_chat(messages, max_tokens=6144)
    return clean_agent_output(result)

# Agent 3: Script writer with strict format
def write_script(prioritized_summary: str, target_date: str) -> str:
    messages = [
        {
            "role": "user",
            "content": f"""
Write a podcast script using ALL 10 stories from the prioritized list below.

MANDATORY FORMAT:

"Hello world… welcome back to Apes On Knowledge, your daily dose of distilled AI news from across the planet. I'm your host, A-OK Newsbot… Let's get into today's most important headlines in artificial intelligence."

[Story 1 Headline]

[First paragraph: What happened with source citation like "TechCrunch reports in 'Article Title' that..."]

[Second paragraph: Why it matters to AI practitioners]

[Story 2 Headline]
...continue for all 10 stories...

"Across today's stories, we see [identify 2-3 key themes]..."

"Until tomorrow, this is A-OK Newsbot… signing off."

CITATION EXAMPLES:
- "TechCrunch reports in 'Article Title' that..."
- "According to Bloomberg's article 'Headline'..."
- "The Verge details in 'Story Name' how..."

Stories to write about:
{prioritized_summary}

Return ONLY the formatted script. No commentary or process notes.
"""
        }
    ]
    
    result = run_anthropic_chat(messages, max_tokens=8192)
    return clean_agent_output(result)

# Agent 4: Editor with content validation
def editorial_review(script: str) -> str:
    messages = [
        {
            "role": "user",
            "content": f"""
Polish this podcast script while ensuring all requirements are met.

VALIDATION CHECKLIST:
□ Starts with "Hello world… welcome back to Apes On Knowledge..."
□ Contains exactly 10 complete stories
□ Each story has proper source citation
□ Ends with "Until tomorrow, this is A-OK Newsbot… signing off."
□ Professional flow and transitions

EDITING INSTRUCTIONS:
1. Improve transitions between stories
2. Ensure consistent citation format
3. Polish language for radio delivery
4. Maintain all story content

Script to edit:
{script}

Return ONLY the polished script. No editing commentary or process notes.
"""
        }
    ]
    
    result = run_anthropic_chat(messages, max_tokens=8192)
    return clean_agent_output(result)

def validate_output(content: str, expected_stories: int = 10) -> Dict:
    """Validate agent output quality"""
    issues = []
    
    # Check for search leakage
    search_indicators = ["Let me search", "I'll search for", "Based on the search results"]
    has_leakage = any(indicator in content for indicator in search_indicators)
    if has_leakage:
        issues.append("Search process leakage detected")
    
    # Count stories
    story_count = len(re.findall(r'STORY \d+:', content))
    if story_count != expected_stories:
        issues.append(f"Expected {expected_stories} stories, found {story_count}")
    
    # Check citations
    citation_count = len(re.findall(r'reports|according to|announced', content, re.IGNORECASE))
    if citation_count < 5:
        issues.append(f"Insufficient citations: {citation_count}")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "story_count": story_count,
        "citation_count": citation_count,
        "has_leakage": has_leakage
    }

def generate_episode_v3(date_str: str = None, with_editor: bool = True, debug: bool = True) -> Dict:
    date_str = date_str or str(dt_date.today())
    
    if debug:
        print(f"🔍 Starting V3 research for {date_str}...")
    
    # Step 1: Research with validation
    research = collect_research(date_str)
    research_validation = validate_output(research, expected_stories=15)
    
    if debug:
        print(f"✅ Research completed: {len(research)} characters")
        print(f"   Validation: {research_validation}")
    
    # Step 2: Prioritize with validation
    summary = prioritize_and_filter(research)
    summary_validation = validate_output(summary, expected_stories=10)
    
    if debug:
        print(f"✅ Prioritization completed: {len(summary)} characters")
        print(f"   Validation: {summary_validation}")
    
    # Step 3: Write script with validation
    script = write_script(summary, date_str)
    script_validation = validate_output(script, expected_stories=10)
    
    if debug:
        print(f"✅ Script writing completed: {len(script)} characters")
        print(f"   Validation: {script_validation}")
    
    # Step 4: Editorial review
    if with_editor:
        reviewed_script = editorial_review(script)
        final_validation = validate_output(reviewed_script, expected_stories=10)
        if debug:
            print(f"✅ Editorial review completed: {len(reviewed_script)} characters")
            print(f"   Final validation: {final_validation}")
    else:
        reviewed_script = script
        final_validation = script_validation
    
    return {
        "date": date_str,
        "research": research,
        "summary": summary,
        "script": reviewed_script,
        "validations": {
            "research": research_validation,
            "summary": summary_validation,
            "script": script_validation,
            "final": final_validation
        }
    }

if __name__ == "__main__":
    episode = generate_episode_v3(debug=True)
    print(f"\n📊 Final Results:")
    print(f"Research: {len(episode['research'])} chars")
    print(f"Summary: {len(episode['summary'])} chars") 
    print(f"Script: {len(episode['script'])} chars")
    print(f"Final validation: {episode['validations']['final']}") 