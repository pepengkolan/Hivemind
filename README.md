# 🧠 Hivemind — AI Debate Platform

> Multiple AI agents debate topics, argue positions, and a judge declares a winner — powered by MiMo v2.5 Pro

## How It Works

1. **You propose a topic** — any question, statement, or controversial take
2. **3 AI agents debate** — each with unique personality and strategy
3. **Judge evaluates** — scores arguments, identifies weaknesses, declares winner

## Agents

| Agent | Role | Style |
|-------|------|-------|
| 🦉 Athena | Strategist | Logical, data-driven, systematic |
| 🔥 Apollo | Innovator | Creative, contrarian, challenges assumptions |
| ⚡ Atlas | Pragmatist | Practical, real-world focused, risk-aware |

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env  # Add MiMo API key
python main.py
```

Open `http://localhost:8000` for the dashboard.

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/debate` | Start new debate |
| GET | `/api/v1/debate/{id}` | Get debate results |
| GET | `/api/v1/debates` | List all debates |
| GET | `/api/v1/health` | Health check |

## Tech Stack

- **AI**: MiMo v2.5 Pro (multi-agent reasoning)
- **Backend**: Python 3.11+, FastAPI, Pydantic v2
- **Dashboard**: Tailwind CSS, dark theme

## License

MIT
