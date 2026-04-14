import json
import time

import anthropic

from config import ANTHROPIC_API_KEY, AUDIENCE, MAX_TOKENS, MODEL

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY, max_retries=0)


def write_newsletter(stories: list[dict]) -> str:
    print("Writing newsletter...")

    stories_json = json.dumps(stories, indent=2)

    response = _call_with_retry(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=f"""You are a senior editor writing a daily AI & technology briefing.

Your audience:
{AUDIENCE}

You will receive a JSON list of recent news items pulled from RSS feeds. In a single pass:
1. Select the 5 most relevant stories for this audience. Prioritise LLM model releases,
   enterprise AI adoption, and credible strategic commentary (HBR, MIT Sloan, McKinsey-style).
   Skip purely technical or consumer-gadget items.
2. For each selected story, write a 2-3 sentence summary framed for a transformation leader
   and one concrete actionable insight.
3. Produce the final newsletter in this exact structure:

[2-sentence intro tying the day's stories together]

**[Headline]**
[2-3 sentence summary with organisational context]
What this means for you: [1-sentence strategic implication]
Actionable insight: [1 concrete action]
Read more: [url]

[... repeat for each of the 5 stories ...]

[1-sentence forward-looking closing thought]

Rules:
- Keep the entire newsletter under 500 words.
- No jargon without explanation.
- Every story must include its source URL from the input.
- Tone: confident, clear, HBR-style — not a tech blog.
- Return ONLY the final newsletter text. No preamble, no commentary, no markdown fences.""",
        messages=[
            {"role": "user", "content": f"Today's candidate stories:\n\n{stories_json}"}
        ],
    )

    for block in response.content:
        if block.type == "text":
            return block.text

    return ""


def _call_with_retry(**kwargs):
    """Call Claude with long-wait retry on 429 (per-minute rate limit)."""
    max_attempts = 4
    wait_seconds = 70
    for attempt in range(1, max_attempts + 1):
        try:
            return client.messages.create(**kwargs)
        except anthropic.RateLimitError:
            if attempt == max_attempts:
                raise
            print(f"Rate limited (attempt {attempt}/{max_attempts}). "
                  f"Waiting {wait_seconds}s for the per-minute bucket to reset...")
            time.sleep(wait_seconds)
