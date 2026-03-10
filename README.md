# 💼 BriefCase

**Your AI morning brief. Intel. Impact. Angles.**

Wake up to a personalized briefing that tells you what happened overnight, what it means for your decisions, and how to use it for content and thought leadership.

No noise. No 47 open tabs. Just the signal that matters — delivered before your first coffee.

---

## What You Get

Every morning, BriefCase delivers three sections:

### 🔍 Intel
What happened in your world overnight. Industry moves, competitor signals, market shifts — filtered through your role and interests.

### ⚡ Impact
The "so what." How each development affects your decisions, strategy, and business. Not just news — context.

### 💡 Angles
Content and thought leadership opportunities hiding in the headlines. LinkedIn posts, talking points, contrarian takes — ready to use.

---

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/briefcase-ai.git
cd briefcase-ai
```

### 2. Create your config

```bash
cp config.example.yml config.yml
```

Edit `config.yml` with your role, industry, and interests.

### 3. Set your API keys

```bash
cp .env.example .env
```

Add your LLM API key and (optionally) a web search API key.

### 4. Run it

```bash
# One-time brief
python briefcase.py

# Or schedule it (cron example for 6am daily)
0 6 * * * cd /path/to/briefcase-ai && python briefcase.py
```

---

## Configuration

BriefCase is built to be personal. Your `config.yml` defines everything:

```yaml
# Who you are
role: "VP of Marketing at a B2B SaaS company"
industry: "Enterprise software"

# What you care about
topics:
  - AI and enterprise technology
  - SaaS growth strategies
  - Content marketing trends
  - Competitive intelligence

# Optional: specific companies or people to track
watchlist:
  companies:
    - OpenAI
    - HubSpot
    - Gartner
  people:
    - Satya Nadella
    - Dharmesh Shah

# How you want it
tone: "sharp and direct"  # or: casual, executive, detailed
max_items: 10             # total items across all sections
language: "en"

# Where you want it
delivery:
  method: "markdown"      # markdown | telegram | discord | slack | email
  time: "06:00"
  timezone: "America/New_York"

  # Telegram (optional)
  # telegram_bot_token: "your-bot-token"
  # telegram_chat_id: "your-chat-id"

  # Discord (optional)
  # discord_webhook_url: "your-webhook-url"

  # Slack (optional)
  # slack_webhook_url: "your-webhook-url"

  # Email (optional)
  # smtp_host: "smtp.gmail.com"
  # smtp_port: 587
  # email_from: "briefcase@yourdomain.com"
  # email_to: "you@yourdomain.com"
```

---

## Delivery Options

| Method | Setup | Best For |
|--------|-------|----------|
| **Markdown** | None — outputs to `briefs/` folder | Reading locally, piping to other tools |
| **Telegram** | Bot token + chat ID | Mobile-first, instant delivery |
| **Discord** | Webhook URL | Team channels, communities |
| **Slack** | Webhook URL | Workplace teams |
| **Email** | SMTP credentials | Traditional, archivable |

---

## How It Works

1. **Search** — Queries the web for your topics using your preferred search API
2. **Filter** — AI reads results through the lens of your role and industry
3. **Curate** — Selects the highest-signal items (not the most popular)
4. **Frame** — Writes each item with intel, impact, AND a usable angle
5. **Deliver** — Sends to your chosen channel in clean, scannable format

The entire pipeline runs in under 60 seconds.

---

## Example Output

> ## 💼 BriefCase — Monday, March 9, 2026
>
> ### 🔍 Intel
>
> • **Bain Releases "The AI Enterprise: Code Red" Report** — Most Fortune 500 still stuck in AI pilot phase, not scaled deployment. The gap between "we're using AI" and "AI is transforming our business" is massive.
>
> • **Meta Opens WhatsApp to Rival AI Chatbots in EU** — Antitrust pressure forcing open distribution. New channel opportunity for B2B messaging.
>
> ### ⚡ Impact
>
> • The Bain report gives you air cover to push AI adoption internally — "even Bain says most companies are behind." Use this in your next board deck.
>
> • WhatsApp opening means your conversational AI strategy just got a new distribution channel. Start testing now before competitors figure it out.
>
> ### 💡 Angles
>
> • **LinkedIn post:** "Companies adopted AI. Now they're finding out nobody knows how to use it." — Pair the Bain report with Workera's AI fluency testing data for a contrarian take.
>
> • **Talking point for your next podcast:** "We're in the AI literacy gap — the space between adoption and competence."

---

## Advanced Usage

### OpenClaw Integration

If you run [OpenClaw](https://github.com/openclaw/openclaw), BriefCase works as a skill:

```bash
# Install as an OpenClaw skill
cp -r briefcase-ai ~/.openclaw/workspace/skills/briefcase
```

Then it runs automatically via heartbeats or cron — no separate infrastructure needed.

### Custom Prompts

Want to change how BriefCase writes? Edit `prompts/` to adjust:

- `intel.md` — How intel items are selected and framed
- `impact.md` — How decisions/impact is analyzed
- `angles.md` — How content opportunities are identified

### Multiple Profiles

Run briefs for different contexts:

```bash
python briefcase.py --config config.marketing.yml
python briefcase.py --config config.investing.yml
```

---

## Requirements

- Python 3.10+
- An LLM API key (OpenAI, Anthropic, or any OpenAI-compatible endpoint)
- A web search API key (Brave Search, SerpAPI, or Tavily) — or use the built-in scraper

---

## Contributing

PRs welcome. The best briefs come from people who actually use them.

---

## License

MIT

---

**Built by [Sarah Evans](https://twitter.com/PRsarahevans)** — because the morning shouldn't start with 47 open tabs.
