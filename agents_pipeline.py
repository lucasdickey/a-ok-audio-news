import anthropic
import os

import logging
from typing import List, Dict
from datetime import date as dt_date

# Multi-agent pipeline for "Apes On Knowledge" - AI Daily News
# Features:
# - Research Agent: Web-enabled AI news gathering with source prioritization
# - Prioritizer Agent: Story selection and quality control (10-12 top stories)
# - Writer Agent: Script generation following sample format and style guidelines
# - Editor Agent: Final polish for tone, citations, and structure consistency
# - All agents trained on sample script best practices for professional AI news delivery

# Initialize the Anthropic client
anthropic_client = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))

def run_anthropic_chat(messages: List[Dict], model="claude-3-5-sonnet-20241022") -> str:
    response = anthropic_client.messages.create(
        model=model,
        messages=messages,
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search"
        }],
        max_tokens=4096
    )
    # Extract text content from the response
    text_content = ""
    for content_block in response.content:
        if hasattr(content_block, "text"):
            text_content += content_block.text
    return text_content.strip()

# Agent 1: Research collector – extracts headlines and summaries with citations.
def collect_research(date: str) -> str:
    messages = [
        {
            "role": "user", 
            "content": f"""
You are the Research Agent for "Apes On Knowledge" - AI Daily News. Your job is to gather comprehensive AI news for {date}.

SEARCH CRITERIA:
- Focus on the 15-20 most significant AI developments from {date}
- Target AI practitioners (developers, researchers, business strategists, enterprise deployers)
- Include proper source attribution (e.g., "according to The Verge", "as reported by The Information")

PRIORITIZED SOURCES:
- News: The Information, The Verge, TBNP, The Gradient, Import AI (Jack Clark), Papers with Code, Semafor, Wired, Axios, Bloomberg, TechCrunch, The AI Exchange (Nathan Benaich)
- Company Blogs: Anthropic, OpenAI, Google AI/DeepMind, Meta, AWS, Hugging Face, Mistral, Cohere
- Key Industry Voices: @rowancheung, @alexalbert__, @sama, @DarioAmodei, @satyanadella, @reidhoffman

EXCLUSIONS:
- NO Tesla, Twitter/X, SpaceX, Neuralink, or other Elon Musk companies
- Avoid basic introductory AI content

For each story, provide:
1. Headline/development
2. Source and attribution
3. Key details and implications
4. Why it matters to AI practitioners

Use web search to find the most recent AI developments and ensure accuracy and recency of all information.
"""
        }
    ]
    return run_anthropic_chat(messages)

# Agent 2: Prioritizer/editor – ranks, removes redundancy, checks for exclusions (e.g., Elon Musk news).
def prioritize_and_filter(research: str) -> str:
    messages = [
        {
            "role": "user", 
            "content": f"""
You are the Prioritizer Agent for "Apes On Knowledge" - AI Daily News. 

Your task is to analyze the following research and select exactly 10-12 of the most significant stories for the podcast script.

PRIORITIZATION CRITERIA:
1. Impact on AI practitioners and the field
2. Breaking developments vs incremental updates
3. Geographic/geopolitical significance 
4. Technical breakthroughs or major business moves
5. Avoid redundant or overlapping stories

QUALITY CONTROL:
- Verify all stories have proper source attribution
- Remove any Elon Musk company content that slipped through
- Ensure stories target AI practitioners (no basic explanations needed)
- Check that each story explains both WHAT happened and WHY it matters

OUTPUT FORMAT:
For each selected story, provide:
- Clear headline
- Source citation
- 2-3 sentence summary covering what happened and why it matters
- Any relevant context for AI practitioners

Here's the research to prioritize:

{research}
"""
        }
    ]
    return run_anthropic_chat(messages)

# Agent 3: Writer/Producer – writes final script using a templated tone and intro/outro structure.
def write_script(prioritized_summary: str, target_date: str) -> str:
    messages = [
        {
            "role": "user",
            "content": f"""
You are the Writer/Producer Agent for "Apes On Knowledge" - AI Daily News. Create a podcast script for {target_date}.

SCRIPT FORMAT (follow this structure exactly):

OPENING:
"Hello world… welcome back to Apes On Knowledge, your daily dose of distilled AI news from across the planet. I'm your host, A-OK Newsbot… Let's get into today's most important headlines in artificial intelligence."

STORY STRUCTURE:
Each story should be 2-3 paragraphs:
1. Headline as section header
2. First paragraph: WHAT happened (core development/announcement) with source attribution
3. Second paragraph: WHY it matters (implications for AI practitioners and the field)
4. Optional third paragraph: Additional context or forward-looking perspective

WRITING STYLE:
- Professional yet accessible tone for AI practitioners
- No basic AI explanations needed - assume sophisticated audience
- Include proper citations: "according to The Verge", "Bloomberg reports", etc.
- Use ellipses for dramatic pause: "… and highlighting how geopolitics continues to shape silicon"
- Balance technical accuracy with engaging narrative

CLOSING SECTION:
End with "Closing Analysis" that identifies 2-3 overarching themes from the day's stories, then close with:
"Until tomorrow, this is A-OK Newsbot… signing off."

REFERENCE SAMPLE: Use the same tone and structure as this example story:
"Nvidia Introduces Cost-Effective Blackwell AI Chip for Chinese Market

In response to increasing U.S. export restrictions, Nvidia is preparing to launch a lower-spec version of its flagship Blackwell AI chip, specifically designed for the Chinese market. The Wall Street Journal reports in "Nvidia Plans China-Friendly AI Chip" that the chip will be priced between $6,500 and $8,000, offering Chinese companies a sanctioned but capable alternative amid a growing AI arms race.

This move helps Nvidia remain competitive in a critical region without violating U.S. trade policies. While stripped down, the chip maintains enough power for many commercial AI applications, offering China a foothold in its ongoing effort to maintain AI progress despite regulatory barriers… and highlighting how geopolitics continues to shape silicon."

Here are the prioritized stories to convert into the script:

{prioritized_summary}
"""
        }
    ]
    return run_anthropic_chat(messages)

# Optional Editor Agent: Polishes for clarity, tone, and citation quality.
def editorial_review(script: str) -> str:
    messages = [
        {
            "role": "user",
            "content": f"""
You are the Editorial Review Agent for "Apes On Knowledge" - AI Daily News. 

Your job is to polish the following script for final publication. Focus on:

QUALITY CHECKLIST:
✓ Opening matches format: "Hello world… welcome back to Apes On Knowledge, your daily dose of distilled AI news from across the planet. I'm your host, A-OK Newsbot…"
✓ Each story has clear headline, proper source attribution, and explains both WHAT and WHY
✓ Writing tone is professional yet engaging for AI practitioners
✓ No basic AI explanations (assumes sophisticated audience)
✓ Proper use of ellipses for dramatic pause
✓ Citations follow format: "The Verge reports", "according to Bloomberg", etc.
✓ Closing Analysis identifies overarching themes
✓ Ends with: "Until tomorrow, this is A-OK Newsbot… signing off."

IMPROVEMENTS TO MAKE:
1. Enhance clarity and flow between paragraphs
2. Strengthen the "why it matters" explanations for AI practitioners
3. Ensure consistent tone throughout
4. Fix any awkward phrasing or transitions
5. Verify all sources are properly attributed
6. Polish the Closing Analysis to draw meaningful connections

STYLE REFERENCE: Match the tone and structure of the sample script, focusing on professional analysis with engaging delivery.

Here's the script to review and polish:

{script}
"""
        }
    ]
    return run_anthropic_chat(messages)

def generate_episode(date_str: str = None, with_editor: bool = True, human_review: bool = False) -> Dict:
    date_str = date_str or str(dt_date.today())
    logging.info(f"Starting script generation for {date_str}")

    research = collect_research(date_str)
    summary = prioritize_and_filter(research)
    script = write_script(summary, date_str)
    reviewed_script = editorial_review(script) if with_editor else script

    if human_review:
        # Placeholder for human review logic
        logging.info("Human review step activated.")
        # Implement human review logic here

    return {
        "date": date_str,
        "research": research,
        "summary": summary,
        "script": reviewed_script
    }

if __name__ == "__main__":
    from pprint import pprint
    episode = generate_episode(human_review=True)
    pprint(episode) 