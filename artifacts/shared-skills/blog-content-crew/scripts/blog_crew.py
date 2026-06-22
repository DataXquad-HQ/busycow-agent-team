"""
Blog Content Crew — core research, drafting, and review stage for a blog-post workflow

4-agent CrewAI crew:
  1. Keyword Researcher  — finds real search data via Tavily
  2. Context Researcher  — reads existing content, finds gaps
  3. Writer              — produces draft from research
  4. Reviewer            — evaluates against Quality Standard, requests revisions

Uses Tavily for real web search (not model memory).
"""

import os
import json
from dotenv import load_dotenv

# Load environment from the active runtime first, then Hermes home if present
load_dotenv()
load_dotenv(os.path.expanduser("~/.hermes/.env"))

from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import TavilySearchTool

# ── LLM Setup ──────────────────────────────────────────────────────────────
# Use Anthropic Claude if available, else OpenAI
def get_llm():
    preferred_model = os.getenv("BLOG_CREW_MODEL")
    if os.getenv("ANTHROPIC_API_KEY"):
        return LLM(
            model=preferred_model or "anthropic/claude-sonnet-4-5",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
        )
    if os.getenv("OPENAI_API_KEY"):
        return LLM(
            model=preferred_model or "gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
        )
    raise RuntimeError("Set ANTHROPIC_API_KEY or OPENAI_API_KEY before running blog-content-crew.")


# ── Tools ──────────────────────────────────────────────────────────────────
search_tool = TavilySearchTool(
    api_key=os.getenv("TAVILY_API_KEY"),
    search_depth="advanced",
    max_results=8,
)


# ── Quality Standard (shared reference) ───────────────────────────────────
QUALITY_STANDARD = """
QUALITY STANDARD — all criteria must pass before article is approved:

STRUCTURE:
- Opens with a hook that earns attention in the first sentence (not "In today's...")
- Has a TL;DR section of 150 words or fewer
- Each section has a clear argument, not just a topic header with padding
- Closes with a specific, actionable CTA

SEO:
- Primary keyword appears in: title, first paragraph, at least one H2 subheading
- Meta description is 155 characters or fewer
- Contains at least one [INTERNAL LINK: topic] placeholder

DEPTH:
- Contains an original insight, specific data point, or concrete scenario
- Does not restate what the reader already knows from generic summaries
- Cites real sources or examples found in research

STYLE:
- Written in brand voice: direct, technical confidence, not corporate, not hype
- NO AI filler phrases: "deeply", "notably", "it's worth noting", "in conclusion",
  "delve into", "game-changing", "revolutionary", "it's important to note"
- Concrete language throughout — no vague claims
- 800–1,200 words (flexible if topic genuinely requires more depth)
"""


def run_blog_crew(brief: dict) -> dict:
    """
    Run the Blog Content Crew with a given brief.

    Args:
        brief: dict with keys:
            - topic (str): article topic
            - angle (str): specific angle or argument
            - target_audience (str): who will read this
            - keyword_direction (str): hint for keyword research
            - word_count (int, optional): target word count, default 900
            - brand_voice (str, optional): brand voice description

    Returns:
        dict with keys:
            - draft (str): full article in markdown
            - keywords (dict): primary and secondary keywords
            - meta_description (str): ≤155 char meta description
            - reviewer_notes (str): reviewer's evaluation notes
            - passed (bool): whether article passed quality standard
    """

    topic = brief["topic"]
    angle = brief["angle"]
    target_audience = brief["target_audience"]
    keyword_direction = brief.get("keyword_direction", "")
    word_count = brief.get("word_count", 900)
    brand_voice = brief.get("brand_voice", "Direct, technical confidence. Not corporate. Not hype.")

    llm = get_llm()

    # ── Agents ────────────────────────────────────────────────────────────

    keyword_researcher = Agent(
        role="Keyword Research Specialist",
        goal=(
            f"Find the best keywords for an article about '{topic}'. "
            "Identify what real people are searching for, not what sounds good."
        ),
        backstory=(
            "You are an SEO expert who finds keywords by looking at real search data. "
            "You search for the topic and analyze what appears in autocomplete, "
            "related searches, and competitor article titles. "
            "You never guess — you verify with actual search results."
        ),
        tools=[search_tool],
        llm=llm,
        verbose=True,
        max_iter=3,
    )

    context_researcher = Agent(
        role="Content Intelligence Researcher",
        goal=(
            f"Research existing content about '{topic}' and find what's missing. "
            "Read actual articles, not just titles. Find the gaps."
        ),
        backstory=(
            "You read the top-ranking articles on any topic and identify: "
            "what they all say (the common ground to avoid repeating), "
            "what none of them say well (the gap to fill), "
            "and what specific data, examples, or insights are available "
            "that could make our article more credible and useful."
        ),
        tools=[search_tool],
        llm=llm,
        verbose=True,
        max_iter=4,
    )

    writer = Agent(
        role="Expert Content Writer",
        goal=(
            f"Write a high-quality blog post about '{topic}' from the angle: '{angle}'. "
            f"Target audience: {target_audience}. "
            f"Target length: {word_count} words."
        ),
        backstory=(
            f"You are a skilled writer who writes in this voice: {brand_voice}. "
            "You use the keyword research and content gaps provided to write an article "
            "that is genuinely useful, not a generic overview. "
            "You write concrete, specific content backed by the research. "
            "You never use filler phrases or AI-speak."
        ),
        tools=[],
        llm=llm,
        verbose=True,
        max_iter=3,
    )

    reviewer = Agent(
        role="Content Quality Reviewer",
        goal=(
            "Review the draft article against the quality standard. "
            "Either approve it or return specific, actionable revision requests."
        ),
        backstory=(
            "You are a meticulous editor who applies a strict quality standard. "
            "You do not give vague feedback like 'improve the tone'. "
            "You identify exactly which criteria failed and what needs to change. "
            "If the article passes all criteria, you approve it clearly."
        ),
        tools=[],
        llm=llm,
        verbose=True,
        max_iter=2,
    )

    # ── Tasks ─────────────────────────────────────────────────────────────

    keyword_task = Task(
        description=(
            f"Research keywords for this article brief:\n"
            f"Topic: {topic}\n"
            f"Angle: {angle}\n"
            f"Target audience: {target_audience}\n"
            f"Keyword direction hint: {keyword_direction}\n\n"
            "Use Tavily to search for:\n"
            "1. The topic itself — look at titles and headings of top results\n"
            "2. Related questions people ask about this topic\n"
            "3. Competitor articles — what keywords do they target?\n\n"
            "Output a JSON object:\n"
            "{\n"
            '  "primary_keyword": "...",\n'
            '  "secondary_keywords": ["...", "...", "..."],\n'
            '  "search_intent": "informational | commercial | mixed",\n'
            '  "reasoning": "why these keywords"\n'
            "}"
        ),
        expected_output="JSON with primary_keyword, secondary_keywords, search_intent, reasoning",
        agent=keyword_researcher,
    )

    context_task = Task(
        description=(
            f"Research existing content about this topic and find gaps:\n"
            f"Topic: {topic}\n"
            f"Angle we want to take: {angle}\n\n"
            "Use Tavily to:\n"
            "1. Search the topic and read the top 5 results\n"
            "2. Identify what all articles say (common ground — avoid repeating)\n"
            "3. Identify what is missing or underdeveloped (the gap to fill)\n"
            "4. Find specific data points, statistics, or case examples available\n\n"
            "Output a structured summary:\n"
            "COMMON GROUND (what everyone says — avoid):\n"
            "CONTENT GAPS (what's missing — our opportunity):\n"
            "USEFUL DATA POINTS (specific numbers, examples, sources found):\n"
            "SUGGESTED SOURCES TO CITE: (URLs)"
        ),
        expected_output="Structured research summary with common ground, gaps, data points, and sources",
        agent=context_researcher,
        context=[keyword_task],
    )

    writing_task = Task(
        description=(
            f"Write a blog post using the keyword research and content analysis provided.\n\n"
            f"Brief:\n"
            f"Topic: {topic}\n"
            f"Angle: {angle}\n"
            f"Target audience: {target_audience}\n"
            f"Target word count: {word_count} words\n"
            f"Brand voice: {brand_voice}\n\n"
            "Structure required:\n"
            "1. Title (include primary keyword)\n"
            "2. Hook (first sentence grabs attention — no 'In today's world...')\n"
            "3. TL;DR (≤150 words summary)\n"
            "4. Body sections with H2 subheadings (at least one H2 includes primary keyword)\n"
            "5. At least one [INTERNAL LINK: topic] placeholder\n"
            "6. CTA at the end (specific, actionable)\n\n"
            "Rules:\n"
            "- Use content gaps from research — fill what others missed\n"
            "- Include specific data points found in research\n"
            "- No filler phrases: deeply, notably, it's worth noting, in conclusion,\n"
            "  game-changing, revolutionary, it's important to note, delve into\n"
            "- Write for the target audience's level of expertise\n\n"
            "Also output at the end:\n"
            "META_DESCRIPTION: [≤155 chars]"
        ),
        expected_output="Full blog post in markdown with title, hook, TL;DR, body, CTA, and meta description",
        agent=writer,
        context=[keyword_task, context_task],
    )

    review_task = Task(
        description=(
            f"Review the draft article against this quality standard:\n\n"
            f"{QUALITY_STANDARD}\n\n"
            "Check every criterion. For each one, note PASS or FAIL with specific evidence.\n\n"
            "If ALL criteria pass:\n"
            "Output: APPROVED\n"
            "Then output the final polished article.\n\n"
            "If ANY criterion fails:\n"
            "Output: REVISION REQUIRED\n"
            "Then list exactly what needs to change (specific, actionable).\n"
            "Then output the revised article with your corrections applied.\n\n"
            "Always output the article at the end — either approved or revised."
        ),
        expected_output="Review result (APPROVED or REVISION REQUIRED with specific notes) followed by the final article",
        agent=reviewer,
        context=[writing_task],
    )

    # ── Crew ──────────────────────────────────────────────────────────────

    crew = Crew(
        agents=[keyword_researcher, context_researcher, writer, reviewer],
        tasks=[keyword_task, context_task, writing_task, review_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()

    # ── Parse output ──────────────────────────────────────────────────────

    raw_output = str(result)

    # Extract keyword data from keyword_task output
    kw_output = str(keyword_task.output) if keyword_task.output else ""
    try:
        # Try to parse JSON from keyword output
        import re
        json_match = re.search(r'\{.*\}', kw_output, re.DOTALL)
        kw_data = json.loads(json_match.group()) if json_match else {}
    except Exception:
        kw_data = {"primary_keyword": keyword_direction, "secondary_keywords": []}

    # Extract meta description
    meta_match = None
    import re
    meta_search = re.search(r'META_DESCRIPTION:\s*(.+?)(?:\n|$)', raw_output)
    meta_description = meta_search.group(1).strip()[:155] if meta_search else ""

    # Determine pass/fail
    passed = "APPROVED" in raw_output and "REVISION REQUIRED" not in raw_output

    # Extract reviewer notes
    review_output = str(review_task.output) if review_task.output else ""
    reviewer_notes = review_output[:500] if review_output else ""

    # The final draft is the full raw output (reviewer outputs the article)
    draft = raw_output

    return {
        "draft": draft,
        "keywords": kw_data,
        "meta_description": meta_description,
        "reviewer_notes": reviewer_notes,
        "passed": passed,
    }


if __name__ == "__main__":
    # Test run
    test_brief = {
        "topic": "How AI autopilot reduces pump station energy costs",
        "angle": "Use real operational data to show measurable energy savings",
        "target_audience": "Water utility engineers and procurement managers",
        "keyword_direction": "pump station energy efficiency, smart water management",
        "word_count": 900,
        "brand_voice": "Direct, technical confidence. Speaks to field operators and decision-makers equally.",
    }

    print("Running Blog Content Crew...")
    result = run_blog_crew(test_brief)

    print("\n=== RESULT ===")
    print(f"Passed: {result['passed']}")
    print(f"Keywords: {result['keywords']}")
    print(f"Meta: {result['meta_description']}")
    print(f"\nDraft (first 500 chars):\n{result['draft'][:500]}")
