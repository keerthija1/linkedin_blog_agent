import os
import anthropic
import requests
from tavily import TavilyClient
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- Clients ---
tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def search_trending_ai_topics() -> list[dict]:
    """Search for the latest and trending AI news using Tavily."""
    logger.info("Searching for trending AI topics...")

    queries = [
        "latest AI model release 2025",
        "trending artificial intelligence news this week",
        "new AI tool launched this week",
    ]

    results = []
    for query in queries:
        response = tavily.search(
            query=query,
            search_depth="advanced",
            max_results=3,
            include_answer=True,
        )
        results.extend(response.get("results", []))

    # Deduplicate by URL
    seen = set()
    unique = []
    for r in results:
        if r["url"] not in seen:
            seen.add(r["url"])
            unique.append(r)

    logger.info(f"Found {len(unique)} unique articles.")
    return unique[:6]  # Top 6 for Claude to pick the best angle


def pick_topic_and_write_post(articles: list[dict]) -> str:
    """Ask Claude to pick the best trending topic and write a LinkedIn blog post."""
    logger.info("Asking Claude to pick topic and write post...")

    articles_text = "\n\n".join([
        f"Title: {a['title']}\nURL: {a['url']}\nSummary: {a.get('content', '')[:400]}"
        for a in articles
    ])

    prompt = f"""You are an AI content strategist and LinkedIn thought leader writer.

Here are the latest trending AI news articles from this week:

{articles_text}

Your task:
1. Pick the SINGLE most interesting, trending, and impactful topic from the above.
2. Write a LinkedIn blog post about it. The post should be written as if Keerthi (an AI engineer building autonomous agents) is sharing their perspective.

LinkedIn Post Requirements:
- Length: 150–250 words
- Start with a strong hook (first line must grab attention — no "I" as the first word)
- Structure: Hook → What happened / What this means → Your take / insight → Call to action or question for readers
- Tone: Conversational, confident, knowledgeable — not robotic or overly formal
- Use line breaks between paragraphs for readability
- End with 3–5 relevant hashtags (e.g. #AI #GenerativeAI #ArtificialIntelligence)
- Do NOT use buzzword fluff like "game-changer" or "revolutionize"
- Do NOT use emojis excessively — max 2 if any

Return ONLY the final LinkedIn post text. No explanation, no preamble."""

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )

    post = response.content[0].text.strip()
    logger.info("Post written successfully.")
    return post


def send_to_telegram(post: str):
    """Send the drafted post to Telegram for review."""
    logger.info("Sending post to Telegram...")

    header = (
        "📝 *LinkedIn Blog Post — Ready for Review*\n"
        f"_Generated on {datetime.now().strftime('%A, %b %d %Y at %I:%M %p')}_\n\n"
        "---\n\n"
    )

    message = header + post + "\n\n---\n✅ Copy and post this on LinkedIn when ready."

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        logger.info("✅ Post sent to Telegram successfully.")
    else:
        logger.error(f"❌ Telegram error: {response.status_code} - {response.text}")


def run_agent():
    """Full pipeline: search → write → send."""
    logger.info("=== LinkedIn Blog Agent started ===")
    try:
        articles = search_trending_ai_topics()
        post = pick_topic_and_write_post(articles)
        send_to_telegram(post)
        logger.info("=== Agent run complete ===")
    except Exception as e:
        logger.error(f"Agent failed: {e}")
        raise


def main():
    # Run once immediately on startup (useful for testing)
    run_agent()

    # Schedule: every Tuesday and Thursday at 8:00 AM CST
    scheduler = BlockingScheduler(timezone="America/Chicago")
    scheduler.add_job(run_agent, "cron", day_of_week="tue,thu", hour=8, minute=0)
    logger.info("Scheduler started — running every Tuesday and Thursday at 8:00 AM CST.")
    scheduler.start()


if __name__ == "__main__":
    main()
