import anthropic
import os

import logging
from typing import List, Dict
from datetime import date as dt_date

# Add iterative generation by allowing feedback loops between agents
# Add a distinct editor agent step that can be toggled on or off
# Ensure the pipeline supports multiple passes and can access the web for real-time data
# Add a manual review step before finalizing the script
# Clearly define roles for each agent (Research, Prioritizer, Writer, Editor)

# Initialize the Anthropic client
anthropic_client = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))

def run_anthropic_chat(messages: List[Dict], model="claude-3-opus-20240229") -> str:
    response = anthropic_client.messages.create(
        model=model,
        messages=messages,
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search"
        }],
        max_tokens=1024
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
        {"role": "user", "content": f"Please gather the top 20 AI news items from {date}. Include citations and avoid Elon Musk companies."}
    ]
    return run_anthropic_chat(messages)

# Agent 2: Prioritizer/editor – ranks, removes redundancy, checks for exclusions (e.g., Elon Musk news).
def prioritize_and_filter(research: str) -> str:
    messages = [
        {"role": "user", "content": research}
    ]
    return run_anthropic_chat(messages)

# Agent 3: Writer/Producer – writes final script using a templated tone and intro/outro structure.
def write_script(prioritized_summary: str, target_date: str) -> str:
    messages = [
        {"role": "user", "content": f"Create the podcast script for {target_date} based on the following: {prioritized_summary}"}
    ]
    return run_anthropic_chat(messages)

# Optional Editor Agent: Polishes for clarity, tone, and citation quality.
def editorial_review(script: str) -> str:
    messages = [
        {"role": "user", "content": script}
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