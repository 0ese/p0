# JX-ANTI BOT

This is a robust Discord anti-bot/filter bot written in Python. It uses advanced detection techniques for ASCII art, Unicode bypasses, and more.

## How to Deploy (Render or Locally)

### 1. Configure Environment Variable
- In your Render dashboard (or locally in a `.env`), set:
  - `TOKEN=your-discord-bot-token`

### 2. Install Requirements (Locally)
```bash
pip install -r requirements.txt
```

### 3. Run Bot
```bash
python bot.py
```

### 4. Deploy to Render
- Push this folder to GitHub.
- Create a new Web Service on render.com.
- Set the start command: `python bot.py`
- Set your Discord bot token as the environment variable `TOKEN`.

## Notes
- `.env` is in .gitignore, never push it to GitHub.
- Requires intents to be enabled in the Discord Developer Portal for message content and members.
