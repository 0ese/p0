import discord
from discord.ext import commands
import os
import emoji
import re
import asyncio
import datetime
from dotenv import load_dotenv
import unicodedata

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.messages = True

bot1 = commands.Bot(command_prefix='$', intents=intents)

# === SETTINGS ===

BYPASS_ROLES = [1353000809171783752, 1417111559075004488, 1356539491090694198]
LOG_CHANNEL_ID = 1352874878298099712

MONITORED_CHANNELS = [
    1350460442354651179,
    1387751360593924207,
    1369709315274965082
]

BLOCKED_MESSAGES = [
    "https://raw.githubusercontent.com/ayawtandogaakongotin/buangka",
    "🄷🅃🅃🄿🅂",
    "🅃🄴🄻🄴",
    "ayawtandogaakongotin",
    "raw.githubusercontent.com"
]

BLOCKED_WORDS = [
    "crack", "cracked", "copypaster", "paster", "ghost", "niga", "skid", "skidded", 
    "skidder", "skidding", "script kiddie", "scriptkiddie", "sk1d", "sk!d", "sk!dded"
]

WHITELIST_WORDS = [
    "recoil", "external", "solara", "solar", "recollect", "recover", "record", "recommend",
    "skeleton", "skilled", "skiing", "skincare", "asking", "risking", "whisker", "brisket",
    "basket", "casket", "gasket", "masked", "asked", "tasked", "flask", "mask",
    "fantastic", "astic", "drastic", "plastic", "elastic", "classic", "jurassic",
    "ghost writer", "ghosting", "ghostly", "ghosted", "past", "paste", "pasted", "copy"
]

# (All code logic from user's bot.py inserted here, replacing all 'bot' with 'bot1')
# ...
# you would continue with all defs, events, commands, etc., using 'bot1' below
#
#
# At the very bottom:
async def run_bot1(token=None):
    load_dotenv()
    if not token:
        token = os.getenv("TOKEN1")
    await bot1.start(token)
