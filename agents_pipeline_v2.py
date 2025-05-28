import anthropic
import os
import logging
from typing import List, Dict
from datetime import date as dt_date

# Multi-agent pipeline for "Apes On Knowledge" - AI Daily News (Version 2)
# Features:
# - Explicit web search instructions with verification
# - Higher token limits for comprehensive research
# - Better agent chaining with debug output
# - Forced web search usage with specific queries

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

# Agent 1: Research collector with 24-hour constraint
def collect_research(date: str) -> str:
    from datetime import datetime, timedelta
    
    # Calculate the exact 24-hour window
    target_date = datetime.strptime(date, "%Y-%m-%d")
    yesterday = (target_date - timedelta(days=1)).strftime("%Y-%m-%d")
    
    messages = [
        {
            "role": "user", 
            "content": f"""
You are the Research Agent for "Apes On Knowledge" - AI Daily News. You MUST use web search to find real, current AI news for {date} as they will be cited in the transcript to ensure that listeners trust the validity and veracity of the episode. You MUST find AI news from the LAST 24 HOURS ONLY.

TARGET DATE RANGE: {yesterday} to {date} (24-hour window only)

MANDATORY SEARCH STRATEGY:
1. Search "AI news last 24 hours {date}"
2. Search "artificial intelligence breaking news today {date}"
3. Search "AI developments past day {date}"
4. Search specific sources with date constraints:
   - "site:techcrunch.com AI {date}"
   - "site:theverge.com artificial intelligence {date}"
   - "site:bloomberg.com AI news {date}"
   - "site:theinformation.com AI {date}"
5. Company-specific recent news:
   - "OpenAI news today {date}"
   - "Google AI announcement {date}"
   - "Meta AI news {date}"
   - "Anthropic news {date}"

CRITICAL DATE FILTERING:
- ONLY include stories published on {date} or {yesterday}
- REJECT any story older than 24 hours from {date}
- Verify publication dates for every story
- If unsure about date, search for the specific article to confirm

REQUIRED OUTPUT for EACH story:
- EXACT headline from source
- EXACT publication date (must be {date} or {yesterday})
- Source name and article URL if available
- 3-4 sentence summary
- Why it matters to AI practitioners

TARGET: Find 15-20 stories from the LAST 24 HOURS ONLY.

PRIORITY SOURCES (search these specifically):
- TechCrunch, The Verge, Bloomberg, The Information, Wired
- Company blogs: OpenAI, Google AI, Meta AI, Anthropic
- Industry: GitHub, Hugging Face announcements

ABSOLUTE EXCLUSIONS:
- NO stories older than {yesterday}
- NO Tesla, SpaceX, Neuralink, Elon Musk companies
- NO generic/evergreen AI content

START SEARCHING NOW - Use multiple specific searches to find recent stories.
"""
        }
    ]
    return run_anthropic_chat(messages, max_tokens=8192)

# Agent 2: Prioritizer with strict 24-hour verification
def prioritize_and_filter(research: str) -> str:
    from datetime import datetime, timedelta
    
    # Get today's date for validation
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    messages = [
        {
            "role": "user", 
            "content": f"""
You are the Prioritizer Agent. Select EXACTLY 10 stories from the LAST 24 HOURS ONLY. These stories will be read on-air with source citations, so accuracy and credibility are critical for listener trust.

CRITICAL DATE VERIFICATION:
- Today's date: {today}
- Yesterday's date: {yesterday}
- ONLY accept stories published on {today} or {yesterday}
- REJECT any story without a clear publication date
- REJECT any story older than 24 hours

STRICT REQUIREMENTS:
1. Select EXACTLY 10 stories (not more, not less)
2. Each story MUST be published within last 24 hours
3. Each story MUST have verified source citation
4. Prioritize by impact on AI practitioners

MANDATORY VERIFICATION for each story:
✓ Publication date is {today} or {yesterday}
✓ Has specific source (e.g., "TechCrunch reports on {today} in 'Article Title'")
✓ Story explains WHAT happened and WHY it matters
✓ Relevant to AI practitioners
✓ No Elon Musk companies
✓ Not generic/evergreen content

OUTPUT FORMAT (for each of the 10 stories):
STORY X: [Headline]
SOURCE: [Exact source and article title]
DATE: [Must be {today} or {yesterday}]
SUMMARY: [What happened and why it matters - 2-3 sentences]

If you cannot find 10 stories from the last 24 hours, select the most recent ones available and note which ones are from the 24-hour window.

Here's the research to analyze:

{research}

Select your 10 most recent, high-impact stories now.
"""
        }
    ]
    return run_anthropic_chat(messages, max_tokens=6144)

# Agent 3: Writer with strict format requirements
def write_script(prioritized_summary: str, target_date: str) -> str:
    messages = [
        {
            "role": "user",
            "content": f"""
You are the Writer Agent. Create a podcast script with ALL 10 stories from the prioritized list. Each story will be read on-air, so source citations must be accurate and verifiable as listeners depend on the credibility of this information.

MANDATORY STRUCTURE:

OPENING (exactly this):
"Hello world… welcome back to Apes On Knowledge, your daily dose of distilled AI news from across the planet. I'm your host, A-OK Newsbot… Let's get into today's most important headlines in artificial intelligence."

BODY - ALL 10 STORIES:
For each story use this format:
[Story Headline]

[First paragraph: What happened with source citation]

[Second paragraph: Why it matters to AI practitioners]

…

CLOSING ANALYSIS:
"Across today's stories, [identify 2-3 themes]..."

ENDING (exactly this):
"Until tomorrow, this is A-OK Newsbot… signing off."

CITATION FORMAT EXAMPLES:
- "The Verge reports in 'Article Title' that..."
- "According to Bloomberg's 'Headline'..."
- "TechCrunch details in 'Article Name' how..."

WRITE ALL 10 STORIES - do not skip any. Here's your prioritized content:

{prioritized_summary}
"""
        }
    ]
    return run_anthropic_chat(messages, max_tokens=8192)

# Agent 4: Editor with verification
def editorial_review(script: str) -> str:
    messages = [
        {
            "role": "user",
            "content": f"""
You are the Editor. Polish this script while ensuring it meets all requirements.

VERIFICATION CHECKLIST:
□ Correct opening: "Hello world… welcome back to Apes On Knowledge..."
□ Contains 10 complete stories (count them)
□ Each story has proper source citation
□ Each story explains WHAT and WHY
□ Proper closing: "Until tomorrow, this is A-OK Newsbot… signing off."
□ Professional tone throughout
□ No basic AI explanations

ONLY make improvements to:
1. Flow and transitions
2. Citation formatting
3. Clarity of explanations
4. Tone consistency

DO NOT remove stories or change the core content. Polish this script:

{script}
"""
        }
    ]
    return run_anthropic_chat(messages, max_tokens=8192)

def generate_episode_v2(date_str: str = None, with_editor: bool = True, debug: bool = True) -> Dict:
    date_str = date_str or str(dt_date.today())
    
    if debug:
        print(f"🔍 Starting research for {date_str}...")
    
    # Step 1: Research with web search
    research = collect_research(date_str)
    if debug:
        print(f"✅ Research completed: {len(research)} characters")
        print(f"Research preview: {research[:300]}...")
    
    # Step 2: Prioritize to exactly 10 stories
    summary = prioritize_and_filter(research)
    if debug:
        print(f"✅ Prioritization completed: {len(summary)} characters")
        print(f"Summary preview: {summary[:300]}...")
    
    # Step 3: Write script with all 10 stories
    script = write_script(summary, date_str)
    if debug:
        print(f"✅ Script writing completed: {len(script)} characters")
        print(f"Script preview: {script[:300]}...")
    
    # Step 4: Editorial review
    if with_editor:
        reviewed_script = editorial_review(script)
        if debug:
            print(f"✅ Editorial review completed: {len(reviewed_script)} characters")
    else:
        reviewed_script = script
    
    return {
        "date": date_str,
        "research": research,
        "summary": summary,
        "script": reviewed_script
    }

if __name__ == "__main__":
    episode = generate_episode_v2(debug=True)
    print(f"\n📊 Final Results:")
    print(f"Research: {len(episode['research'])} chars")
    print(f"Summary: {len(episode['summary'])} chars") 
    print(f"Script: {len(episode['script'])} chars") 