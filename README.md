# LinkedIn Blog Agent 🤖

An autonomous AI agent that searches for trending AI news, writes a LinkedIn blog post, and delivers it to Telegram for your review — twice a week, fully automated.

## How It Works

```
Tavily (trending AI news search)
        ↓
Claude (picks best topic + writes LinkedIn post)
        ↓
Telegram (sends to you for review)
        ↓
You copy-paste and post on LinkedIn
```

## Schedule
Runs every **Tuesday and Thursday at 8:00 AM CST** automatically on Railway.

## Stack
- **Tavily API** — AI-powered web search for trending topics
- **Anthropic Claude** — writes the LinkedIn post
- **Telegram Bot API** — delivers post to your phone for review
- **APScheduler** — cron scheduling
- **Railway** — cloud deployment

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/keerthija1/linkedin-blog-agent
cd linkedin-blog-agent
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set environment variables
Copy `.env.example` and fill in your keys:
```
ANTHROPIC_API_KEY=
TAVILY_API_KEY=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

### 4. Test locally
```bash
python agent.py
```
This runs the agent once immediately, then starts the scheduler.

### 5. Deploy to Railway
1. Push to GitHub
2. Create new Railway project → Deploy from GitHub repo
3. Add environment variables in Railway dashboard
4. Deploy ✅

## Getting API Keys
- **Anthropic**: https://console.anthropic.com
- **Tavily**: https://app.tavily.com (free tier: 1,000 searches/month)
- **Telegram Bot**: Message @BotFather on Telegram → `/newbot`
- **Telegram Chat ID**: Message @userinfobot on Telegram

## Cost
~$0–2/month (Tavily free tier covers 2 posts/week easily)
