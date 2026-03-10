#!/usr/bin/env python3
"""
💼 BriefCase — Your AI Morning Brief
Intel. Impact. Angles.
"""

import os
import sys
import json
import yaml
import argparse
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_config(config_path: str = "config.yml") -> dict:
    """Load and validate the user config."""
    path = Path(config_path)
    if not path.exists():
        print("❌ Config file not found. Run: cp config.example.yml config.yml")
        sys.exit(1)
    with open(path) as f:
        config = yaml.safe_load(f)
    # Defaults
    config.setdefault("tone", "sharp and direct")
    config.setdefault("max_items", 10)
    config.setdefault("language", "en")
    config.setdefault("delivery", {"method": "markdown", "output_dir": "briefs"})
    config.setdefault("llm", {"provider": "openai", "model": "gpt-4o"})
    config.setdefault("search", {"provider": "brave"})
    return config


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def search_web(query: str, config: dict, count: int = 5) -> list[dict]:
    """Search the web using the configured provider. Returns [{title, url, snippet}]."""
    provider = config["search"]["provider"]

    if provider == "brave":
        return _search_brave(query, count)
    elif provider == "serpapi":
        return _search_serpapi(query, count)
    elif provider == "tavily":
        return _search_tavily(query, count)
    else:
        print(f"⚠️  Unknown search provider: {provider}. Skipping search.")
        return []


def _search_brave(query: str, count: int) -> list[dict]:
    import requests
    key = os.getenv("BRAVE_SEARCH_API_KEY")
    if not key:
        print("❌ BRAVE_SEARCH_API_KEY not set")
        return []
    resp = requests.get(
        "https://api.search.brave.com/res/v1/web/search",
        headers={"X-Subscription-Token": key, "Accept": "application/json"},
        params={"q": query, "count": count, "freshness": "pd"},
    )
    resp.raise_for_status()
    results = resp.json().get("web", {}).get("results", [])
    return [{"title": r["title"], "url": r["url"], "snippet": r.get("description", "")} for r in results]


def _search_serpapi(query: str, count: int) -> list[dict]:
    import requests
    key = os.getenv("SERPAPI_API_KEY")
    if not key:
        print("❌ SERPAPI_API_KEY not set")
        return []
    resp = requests.get(
        "https://serpapi.com/search",
        params={"q": query, "api_key": key, "num": count, "tbs": "qdr:d"},
    )
    resp.raise_for_status()
    results = resp.json().get("organic_results", [])
    return [{"title": r["title"], "url": r["link"], "snippet": r.get("snippet", "")} for r in results[:count]]


def _search_tavily(query: str, count: int) -> list[dict]:
    import requests
    key = os.getenv("TAVILY_API_KEY")
    if not key:
        print("❌ TAVILY_API_KEY not set")
        return []
    resp = requests.post(
        "https://api.tavily.com/search",
        json={"api_key": key, "query": query, "max_results": count, "search_depth": "advanced"},
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    return [{"title": r["title"], "url": r["url"], "snippet": r.get("content", "")} for r in results]


# ---------------------------------------------------------------------------
# LLM
# ---------------------------------------------------------------------------

def call_llm(prompt: str, config: dict) -> str:
    """Call the configured LLM and return the response text."""
    provider = config["llm"]["provider"]
    model = config["llm"]["model"]

    if provider in ("openai", "openai-compatible"):
        return _call_openai(prompt, model, config["llm"].get("base_url"))
    elif provider == "anthropic":
        return _call_anthropic(prompt, model)
    else:
        print(f"❌ Unknown LLM provider: {provider}")
        sys.exit(1)


def _call_openai(prompt: str, model: str, base_url: str | None = None) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=base_url)
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return resp.choices[0].message.content


def _call_anthropic(prompt: str, model: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    resp = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text


# ---------------------------------------------------------------------------
# Prompt Building
# ---------------------------------------------------------------------------

def load_prompt_template(section: str) -> str:
    """Load a prompt template from the prompts/ directory."""
    path = Path(__file__).parent / "prompts" / f"{section}.md"
    if not path.exists():
        return ""
    return path.read_text()


def build_search_queries(config: dict) -> list[str]:
    """Generate search queries from config topics and watchlist."""
    queries = []
    for topic in config.get("topics", []):
        queries.append(f"{topic} latest news today")
    for company in config.get("watchlist", {}).get("companies", []):
        queries.append(f"{company} news today")
    for person in config.get("watchlist", {}).get("people", []):
        queries.append(f"{person} latest news")
    return queries if queries else ["latest business and technology news today"]


def build_brief_prompt(config: dict, search_results: list[dict]) -> str:
    """Build the full prompt for generating the brief."""
    # Format search results
    sources = "\n".join(
        f"- [{r['title']}]({r['url']}): {r['snippet']}"
        for r in search_results
    )

    # Load section templates
    intel_prompt = load_prompt_template("intel")
    impact_prompt = load_prompt_template("impact")
    angles_prompt = load_prompt_template("angles")

    today = datetime.now().strftime("%A, %B %d, %Y")
    topics_str = ", ".join(config.get("topics", []))
    watchlist_str = json.dumps(config.get("watchlist", {}), indent=2)

    return f"""You are BriefCase, an AI morning brief generator.

Today is {today}.

## The Person You're Briefing
- **Role:** {config.get('role', 'Professional')}
- **Industry:** {config.get('industry', 'General')}
- **Topics:** {topics_str}
- **Watchlist:** {watchlist_str}
- **Tone:** {config.get('tone', 'sharp and direct')}
- **Max items:** {config.get('max_items', 10)} total across all sections

## Raw Sources (from today's web search)
{sources}

## Your Task
Generate a morning brief with exactly three sections. Use ONLY information from the sources above.

### Section Guidelines

{intel_prompt}

---

{impact_prompt}

---

{angles_prompt}

## Output Format
Use this exact structure:

## 💼 BriefCase — {today}

### 🔍 Intel
(items here)

### ⚡ Impact
(items here)

### 💡 Angles
(items here)

---
Include source links. Be specific. No filler. Make every word count.
"""


# ---------------------------------------------------------------------------
# Delivery
# ---------------------------------------------------------------------------

def deliver(brief: str, config: dict):
    """Deliver the brief via the configured method."""
    method = config["delivery"]["method"]

    if method == "markdown":
        _deliver_markdown(brief, config)
    elif method == "telegram":
        _deliver_telegram(brief, config)
    elif method == "discord":
        _deliver_discord(brief, config)
    elif method == "slack":
        _deliver_slack(brief, config)
    elif method == "email":
        _deliver_email(brief, config)
    else:
        print(f"⚠️  Unknown delivery method: {method}. Printing to stdout.")
        print(brief)


def _deliver_markdown(brief: str, config: dict):
    output_dir = Path(config["delivery"].get("output_dir", "briefs"))
    output_dir.mkdir(exist_ok=True)
    filename = datetime.now().strftime("%Y-%m-%d") + ".md"
    path = output_dir / filename
    path.write_text(brief)
    print(f"✅ Brief saved to {path}")


def _deliver_telegram(brief: str, config: dict):
    import requests
    token = config["delivery"].get("telegram_bot_token") or os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = config["delivery"].get("telegram_chat_id") or os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("❌ Telegram bot token or chat ID not configured")
        return
    # Telegram has a 4096 char limit — split if needed
    chunks = [brief[i:i+4000] for i in range(0, len(brief), 4000)]
    for chunk in chunks:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": chunk, "parse_mode": "Markdown"},
        )
    print("✅ Brief sent to Telegram")


def _deliver_discord(brief: str, config: dict):
    import requests
    url = config["delivery"].get("discord_webhook_url") or os.getenv("DISCORD_WEBHOOK_URL")
    if not url:
        print("❌ Discord webhook URL not configured")
        return
    chunks = [brief[i:i+1900] for i in range(0, len(brief), 1900)]
    for chunk in chunks:
        requests.post(url, json={"content": chunk})
    print("✅ Brief sent to Discord")


def _deliver_slack(brief: str, config: dict):
    import requests
    url = config["delivery"].get("slack_webhook_url") or os.getenv("SLACK_WEBHOOK_URL")
    if not url:
        print("❌ Slack webhook URL not configured")
        return
    requests.post(url, json={"text": brief})
    print("✅ Brief sent to Slack")


def _deliver_email(brief: str, config: dict):
    import smtplib
    from email.mime.text import MIMEText
    d = config["delivery"]
    host = d.get("smtp_host", "smtp.gmail.com")
    port = d.get("smtp_port", 587)
    user = d.get("smtp_user", "")
    passwd = d.get("smtp_pass") or os.getenv("SMTP_PASS", "")
    email_from = d.get("email_from", user)
    email_to = d.get("email_to", "")
    if not all([user, passwd, email_to]):
        print("❌ Email credentials not fully configured")
        return
    today = datetime.now().strftime("%B %d, %Y")
    msg = MIMEText(brief)
    msg["Subject"] = f"💼 BriefCase — {today}"
    msg["From"] = email_from
    msg["To"] = email_to
    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, passwd)
        server.send_message(msg)
    print("✅ Brief sent via email")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="💼 BriefCase — Your AI Morning Brief")
    parser.add_argument("--config", default="config.yml", help="Path to config file")
    parser.add_argument("--stdout", action="store_true", help="Print to stdout instead of delivering")
    args = parser.parse_args()

    config = load_config(args.config)

    print("🔍 Searching the web...")
    queries = build_search_queries(config)
    all_results = []
    for query in queries:
        results = search_web(query, config)
        all_results.extend(results)

    # Deduplicate by URL
    seen = set()
    unique_results = []
    for r in all_results:
        if r["url"] not in seen:
            seen.add(r["url"])
            unique_results.append(r)

    if not unique_results:
        print("⚠️  No search results found. Check your API keys and topics.")
        sys.exit(1)

    print(f"📰 Found {len(unique_results)} unique sources")
    print("🧠 Generating brief...")

    prompt = build_brief_prompt(config, unique_results)
    brief = call_llm(prompt, config)

    if args.stdout:
        print(brief)
    else:
        deliver(brief, config)
        # Also save a copy as markdown
        if config["delivery"]["method"] != "markdown":
            _deliver_markdown(brief, config)


if __name__ == "__main__":
    main()
