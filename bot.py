import discord
from discord.ext import commands, tasks
import os
import emoji
import re
import asyncio
import datetime
from dotenv import load_dotenv
import unicodedata
from aiohttp import web

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.messages = True

bot = commands.Bot(command_prefix='$', intents=intents)

# === SETTINGS ===

BYPASS_ROLES = [1353000809171783752, 1417111559075004488, 1356539491090694198]
LOG_CHANNEL_ID = 1352874878298099712

MONITORED_CHANNELS = [
    1350460442354651179,
    1387751360593924207,
    1352874878298099712,
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
    "ghost writer", "ghosting", "ghostly", "ghosted", "copy"
]

# === AUTO-REPLY PATTERNS ===

AUTO_REPLY_PATTERNS = {
    r'(?i)(?:does|do|is)\s+(?:melee\s+)?(?:reach|aura)\s+(?:work|working)\s*(?:with|on)?\s*(?:fire\s+axe|axe)?': {
        'response': "Yes, it's working! 🔥",
        'description': 'Melee reach/aura functionality'
    },
    r'(?i)(?:where|how)\s+(?:is|to\s+get|can\s+i\s+get|do\s+i\s+get)\s+(?:the\s+)?script': {
        'response': "You can get/copy the script at this link: https://getjx.vercel.app/ 📜",
        'description': 'Script download location'
    },
    r'(?i)(?:wheres?|where\s+is)\s+(?:the\s+)?script': {
        'response': "You can get/copy the script at this link: https://getjx.vercel.app/ 📜",
        'description': 'Script location'
    },
    r'(?i)(?:where|how)\s+(?:to\s+get|can\s+i\s+get|do\s+i\s+get)\s+(?:a\s+)?key': {
        'response': "Please read https://discord.com/channels/1350403770986528779/1390636325752934430 to get your key, or you can buy a premium key at https://discord.com/channels/1350403770986528779/1423933307137163274 🔑",
        'description': 'Key acquisition guide'
    },
    r'(?i)(?:where|how)\s+(?:to\s+buy|can\s+i\s+buy)\s+(?:premium\s+)?key': {
        'response': "You can buy a premium key at https://discord.com/channels/1350403770986528779/1423933307137163274 💎",
        'description': 'Premium key purchase'
    },
    r'(?i)why\s+(?:is\s+)?my\s+key\s+(?:not\s+working|broken|invalid)': {
        'response': "Try turning off your VPN and make sure you're using the correct key format. If the issue persists, please contact support! 🛠️",
        'description': 'Key troubleshooting'
    },
    r'(?i)(?:how\s+to\s+get|where\s+to\s+find|need)\s+(?:the\s+)?script': {
        'response': "You can get/copy the script at this link: https://getjx.vercel.app/ 📜",
        'description': 'Script access'
    }
}

# === HELPER FUNCTIONS ===

def advanced_ascii_art_extraction(text):
    if not text or len(text) < 5:
        return []
    extracted_sequences = []
    lines = text.split('\n')
    
    if len(lines) >= 3:
        max_length = max(len(line) for line in lines) if lines else 0
        for col in range(min(100, max_length)):
            vertical_chars = []
            for line in lines:
                if col < len(line) and line[col].isalpha():
                    vertical_chars.append(line[col].lower())
            if len(vertical_chars) >= 3:
                vertical_word = ''.join(vertical_chars)
                if len(vertical_word) >= 3:
                    extracted_sequences.append(vertical_word)
    
    for line in lines:
        cleaned = re.sub(r'[|/\\()[\]{}#@*=_\-+<>~^`.:;\'"!?$%&]', ' ', line)
        words = cleaned.split()
        for word in words:
            if len(word) >= 3 and word.isalpha():
                extracted_sequences.append(word.lower())
    
    full_text = ' '.join(lines)
    letters_only = re.sub(r'[^a-zA-Z]', '', full_text).lower()
    
    if letters_only:
        for i in range(len(letters_only) - 2):
            chunk = letters_only[i:i+10]
            if len(chunk) >= 3:
                extracted_sequences.append(chunk[:8])
    
    return extracted_sequences

def comprehensive_unicode_to_ascii(text):
    if not text:
        return ""
    result = list(text)
    for i, char in enumerate(result):
        code = ord(char)
        if 0x1D400 <= code <= 0x1D419:
            result[i] = chr(ord('A') + (code - 0x1D400))
        elif 0x1D41A <= code <= 0x1D433:
            result[i] = chr(ord('a') + (code - 0x1D41A))
        elif 0xFF21 <= code <= 0xFF3A:
            result[i] = chr(ord('A') + (code - 0xFF21))
        elif 0xFF41 <= code <= 0xFF5A:
            result[i] = chr(ord('a') + (code - 0xFF41))
        elif char in 'АВСЕНІКМОРТУХавсеікморстух':
            cyrillic_map = {'А':'A','В':'B','С':'C','Е':'E','Н':'H','І':'I','К':'K','М':'M','О':'O','Р':'P','Т':'T','У':'Y','Х':'X','а':'a','в':'b','с':'c','е':'e','і':'i','к':'k','м':'m','о':'o','р':'p','т':'t','у':'u','х':'x'}
            result[i] = cyrillic_map.get(char, char)
    return ''.join(result)

def detect_multi_line_art(text):
    if not text or len(text) < 20:
        return False
    lines = text.split('\n')
    if len(lines) > 6:
        return True
    if len(lines) >= 3:
        lengths = [len(line) for line in lines if line.strip()]
        if lengths:
            avg_length = sum(lengths) / len(lengths)
            if avg_length > 30 and len([l for l in lengths if abs(l - avg_length) < 10]) >= 3:
                return True
    return False

def is_whitelisted_word(word):
    word_lower = word.lower()
    for whitelist_word in WHITELIST_WORDS:
        if word_lower == whitelist_word.lower():
            return True
    return False

def check_blocked_words_ultimate(text):
    if not text:
        return False, []
    violations = []
    converted = comprehensive_unicode_to_ascii(text)
    normalized = re.sub(r'[^a-z0-9\s]', '', converted.lower())
    words = normalized.split()
    
    for word in words:
        if len(word) < 3 or is_whitelisted_word(word):
            continue
        for blocked in BLOCKED_WORDS:
            blocked_clean = re.sub(r'[^a-z]', '', blocked.lower())
            if len(blocked_clean) >= 3:
                if word == blocked_clean:
                    violations.append(f"Blocked word: '{blocked}'")
                elif blocked_clean in word and len(word) <= len(blocked_clean) + 3:
                    if not is_whitelisted_word(word):
                        violations.append(f"Blocked word (obfuscated): '{blocked}' in '{word}'")
    
    return len(violations) > 0, list(set(violations))

def detect_non_english(text):
    if not text or len(text.strip()) < 3:
        return False
    cleaned_text = re.sub(r'http[s]?://\S+', '', text)
    cleaned_text = re.sub(r'<@[!&]?\d+>', '', cleaned_text)
    try:
        cleaned_text = emoji.demojize(cleaned_text)
        cleaned_text = re.sub(r':[a-z_]+:', '', cleaned_text)
    except:
        pass
    text_only = re.sub(r'[^a-zA-ZÀ-ÿĀ-žА-я\u4e00-\u9fff\u0600-\u06ff\s]', '', cleaned_text)
    text_only = text_only.strip()
    if len(text_only) < 3:
        return False
    total_chars = len(text_only.replace(' ', ''))
    if total_chars == 0:
        return False
    english_chars = len(re.findall(r'[a-zA-Z]', text_only))
    english_ratio = english_chars / total_chars
    cyrillic_chars = len(re.findall(r'[А-я]', text_only))
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text_only))
    arabic_chars = len(re.findall(r'[\u0600-\u06ff]', text_only))
    if english_ratio < 0.7 and (cyrillic_chars > 2 or chinese_chars > 1 or arabic_chars > 2):
        return True
    return False

def analyze_message_content(content):
    if not content or len(content) < 2:
        return False, []
    violations = []
    if detect_multi_line_art(content):
        violations.append("Multi-line ASCII art detected (likely bypass attempt)")
    has_blocked, blocked_violations = check_blocked_words_ultimate(content)
    violations.extend(blocked_violations)
    converted = comprehensive_unicode_to_ascii(content).lower()
    for blocked_msg in BLOCKED_MESSAGES:
        if blocked_msg.lower() in converted:
            violations.append(f"Blocked content: '{blocked_msg}'")
    return len(violations) > 0, violations

def check_auto_reply(message_content):
    if not message_content or len(message_content.strip()) < 3:
        return None
    cleaned_content = message_content.strip()
    for pattern, reply_data in AUTO_REPLY_PATTERNS.items():
        if re.search(pattern, cleaned_content):
            return reply_data['response']
    return None

async def process_message(message, is_edit=False):
    if message.author.bot or not message.guild:
        return
    if message.channel.id not in MONITORED_CHANNELS:
        await bot.process_commands(message)
        return
    guild_member = message.guild.get_member(message.author.id)
    if not guild_member:
        return
    if any(role.id in BYPASS_ROLES for role in guild_member.roles):
        auto_reply = check_auto_reply(message.content)
        if auto_reply:
            try:
                await message.reply(auto_reply)
            except:
                pass
        return
    
    auto_reply = check_auto_reply(message.content)
    if auto_reply:
        try:
            await message.reply(auto_reply)
        except:
            pass
    
    if detect_non_english(message.content):
        try:
            await message.delete()
        except discord.Forbidden:
            pass
        try:
            embed = discord.Embed(title="🌐 Language Notice", description="Please speak English only.", color=0x3498db)
            await message.channel.send(embed=embed, delete_after=10)
        except:
            pass
        return
    
    is_violation, violation_reasons = analyze_message_content(message.content)
    if is_violation:
        try:
            await message.delete()
        except discord.Forbidden:
            pass
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            violation_text = '\n'.join(f"• {reason}" for reason in violation_reasons[:5])
            display_content = message.content[:497] + "..." if len(message.content) > 500 else message.content
            title = "🚫 Message Blocked" if not is_edit else "🚫 Edited Message Blocked"
            embed = discord.Embed(title=title, description=f"**User:** {guild_member.mention}\n**Channel:** {message.channel.mention}", color=0xff4444, timestamp=datetime.datetime.now(datetime.timezone.utc))
            embed.add_field(name="Violations", value=violation_text, inline=False)
            embed.add_field(name="Original Message", value=f"```\n{display_content}\n```", inline=False)
            try:
                await log_channel.send(embed=embed)
            except:
                pass
        return
    await bot.process_commands(message)

# === HEALTH CHECK SERVER (RUNS ALONGSIDE BOT) ===

async def health_check_server():
    """Simple health check server for Render"""
    async def health(request):
        return web.Response(text="✅ Bot is running!")
    
    app = web.Application()
    app.router.add_get('/', health)
    app.router.add_get('/health', health)
    
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv('PORT', 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Health server running on port {port}")

# === BOT EVENTS ===

@bot.event
async def on_ready():
    print(f'✅ {bot.user} is online!')
    print(f'📢 Monitoring {len(MONITORED_CHANNELS)} channels')
    print(f'🛡️ Protecting against {len(BLOCKED_WORDS)} blocked words')
    print(f'🤖 Auto-reply patterns: {len(AUTO_REPLY_PATTERNS)}')
    # Start health server
    bot.loop.create_task(health_check_server())

@bot.event
async def on_message(message):
    await process_message(message, is_edit=False)

@bot.event
async def on_message_edit(before, after):
    await process_message(after, is_edit=True)

# === ADMIN COMMANDS (SHORTENED FOR SPACE) ===

@bot.command(name="filterhelp")
@commands.has_permissions(administrator=True)
async def filter_help(ctx):
    embed = discord.Embed(title="🛡️ Filter Bot Commands", color=0x3498db)
    embed.add_field(name="Commands", value="`$addchannel` `$removechannel` `$listchannels`\n`$addblockedword` `$removeblockedword` `$testmessage`", inline=False)
    await ctx.send(embed=embed, delete_after=30)

@bot.command(name="stats")
@commands.has_permissions(administrator=True)
async def show_stats(ctx):
    embed = discord.Embed(title="📊 Bot Stats", color=0x2ecc71)
    embed.add_field(name="Status", value=f"🟢 Online in {len(bot.guilds)} servers", inline=False)
    embed.add_field(name="Monitoring", value=f"{len(MONITORED_CHANNELS)} channels", inline=True)
    embed.add_field(name="Protection", value=f"{len(BLOCKED_WORDS)} blocked words", inline=True)
    await ctx.send(embed=embed, delete_after=20)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ No permission", delete_after=5)

# === START BOT ===

if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN")
    
    if not token:
        print("❌ No token found! Set DISCORD_TOKEN in environment")
        exit(1)
    
    print("🚀 Starting bot...")
    try:
        bot.run(token)
    except Exception as e:
        print(f"❌ Error: {e}")

