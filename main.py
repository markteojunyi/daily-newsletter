import time
from agents import researcher_agent, writer_agent, editor_agent
from sender import send_newsletter

# -----------------------------------------------------------
# Configuration — edit these to change your newsletter
# -----------------------------------------------------------
TOPIC = "AI and technology — latest LLM model updates and organisational impact"

AUDIENCE = """A senior transformation and innovation professional with a Lean Six Sigma background,
aspiring to become an Innovation Director. Wants to understand not just what is new in AI and LLMs,
but what it means for organisations — how to adopt it, what the obstacles are, and what leaders
should do about it. Prefers concise, strategic insights over technical detail."""

RESEARCH_FOCUS = """Focus on:
- Latest model releases and updates from major LLM providers (OpenAI, Anthropic, Google, Meta, Mistral)
- Thought leadership on AI adoption in organisations (prioritise HBR, McKinsey, MIT Sloan)
- Practical examples of AI transformation — wins, failures, and lessons learned
- Insights from credible thought leaders (e.g. YouTube creators like NateBJones, newsletters, podcasts)
- Key obstacles organisations face when adopting AI

For each story:
- Include the source URL (article link or video link)
- Include a 2-3 sentence summary written for a senior transformation professional
- Include one concrete actionable insight"""


# -----------------------------------------------------------
# Orchestrator — runs the 3 agents in sequence
# -----------------------------------------------------------
def run():
    print("Starting Newsletter Agent...\n")

    # Step 1: Researcher searches the web
    research = researcher_agent(
        topic=TOPIC,
        audience=AUDIENCE,
        focus=RESEARCH_FOCUS
    )
    print("\nResearch complete.")
    print("-" * 40)
    print(research)
    print("-" * 40 + "\n")

    # Pause to avoid hitting the API rate limit
    print("Waiting 75 seconds before next agent...")
    time.sleep(75)

    # Step 2: Writer drafts the newsletter
    draft = writer_agent(
        topic=TOPIC,
        audience=AUDIENCE,
        research=research
    )
    print("\nDraft complete.")
    print("-" * 40)
    print(draft)
    print("-" * 40 + "\n")

    # Pause again before the editor
    print("Waiting 75 seconds before next agent...")
    time.sleep(75)

    # Step 3: Editor polishes the draft
    final = editor_agent(draft=draft)
    print("\nFinal newsletter ready.")
    print("-" * 40)
    print(final)
    print("-" * 40 + "\n")

    # Step 4: Send via Gmail
    send_newsletter(newsletter_text=final, topic="AI & Technology")
    print("\nDone!")


if __name__ == "__main__":
    run()