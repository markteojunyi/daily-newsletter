import anthropic
from config import ANTHROPIC_API_KEY, MODEL, MAX_TOKENS
from tools import WEB_SEARCH_TOOL

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


# -----------------------------------------------------------
# Agent 1: Researcher
# Role: search the web and return structured story summaries
# Tools: web_search
# -----------------------------------------------------------
def researcher_agent(topic: str, audience: str, focus: str) -> str:
    print("Researcher agent is searching the web...")

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        tools=[WEB_SEARCH_TOOL],
        system=f"""You are a research assistant preparing content for a daily newsletter.

Your audience: {audience}

{focus}

Search the web and find exactly 5 stories published in the last 3 days.
Return a JSON list with this exact format:
[
  {{
    "headline": "...",
    "source_name": "...",
    "url": "...",
    "summary": "2-3 sentence summary written for the audience above",
    "actionable_insight": "One concrete thing a transformation or innovation leader can do or consider based on this story"
  }}
]
Return only the JSON list. No extra text, no markdown fences.""",
        messages=[
            {"role": "user", "content": f"Find the top 5 stories about: {topic}"}
        ]
    )

    for block in response.content:
        if block.type == "text":
            return block.text

    return "[]"


# -----------------------------------------------------------
# Agent 2: Writer
# Role: turn research summaries into a readable newsletter draft
# Tools: none (pure writing)
# -----------------------------------------------------------
def writer_agent(topic: str, audience: str, research: str) -> str:
    print("Writer agent is drafting the newsletter...")

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=f"""You are a newsletter writer crafting a daily briefing.

Your audience: {audience}

Structure the newsletter exactly like this:

1. A short intro (2 sentences max) — what's the theme connecting today's stories?

2. For each story:
   **[Headline]**
   [2-3 sentence summary with organisational context]
   What this means for you: [1 sentence strategic implication]
   Actionable insight: [the actionable_insight from the research]
   Read more: [url]

3. A closing line (1 sentence) — a forward-looking thought for innovation leaders.

Rules:
- Write for a senior professional, not a general audience
- No technical jargon unless explained
- Keep the whole newsletter under 500 words
- Every story must have a link and an actionable insight""",
        messages=[
            {"role": "user", "content": f"Topic: {topic}\n\nResearch:\n{research}"}
        ]
    )

    for block in response.content:
        if block.type == "text":
            return block.text

    return ""


# -----------------------------------------------------------
# Agent 3: Editor
# Role: polish the draft — fix grammar, improve flow, trim length
# Tools: none (pure editing)
# -----------------------------------------------------------
def editor_agent(draft: str) -> str:
    print("Editor agent is polishing the newsletter...")

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system="""You are a sharp editor for a senior professional newsletter.

Review the draft and:
- Fix grammar and spelling
- Ensure every story has a link, a "What this means for you" line, and an actionable insight
- Cut anything purely technical with no organisational relevance
- Keep the tone confident, clear, and respected — like HBR, not a tech blog
- Trim to under 500 words if needed
- Do not add new content, only refine what is there

Return only the final polished newsletter. No commentary.""",
        messages=[
            {"role": "user", "content": f"Please edit this newsletter draft:\n\n{draft}"}
        ]
    )

    for block in response.content:
        if block.type == "text":
            return block.text

    return draft