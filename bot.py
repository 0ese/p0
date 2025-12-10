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
    1369709315274965082
]

BLOCKED_MESSAGES = [
    "https://raw.githubusercontent.com/ayawtandogaakongotin/buangka",
    "🄷🅃🅃🄿🅂",
    "🅃🄴🄻🄴",
    "ayawtandogaakongotin",
    "raw.githubusercontent.com",
     "SKIDDER"
]

BLOCKED_WORDS = [
    "crack", "cracked", "copypaster", "paster", "ghost", "niga", "skid", "skidded", 
    "skidder", "skidding", "script kiddie", "scriptkiddie", "sk1d", "sk!d", "sk!dded",
    "skidd", "skido"
]

WHITELIST_WORDS = [
    "recoil", "external", "solara", "solar", "recollect", "recover", "record", "recommend",
    "skeleton", "skilled", "skiing", "skincare", "asking", "risking", "whisker", "brisket",
    "basket", "casket", "gasket", "masked", "asked", "tasked", "flask", "mask",
    "fantastic", "astic", "drastic", "plastic", "elastic", "classic", "jurassic",
    "ghost writer", "ghosting", "ghostly", "ghosted", "past", "paste", "pasted"
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

# === COMPREHENSIVE ASCII ART DETECTION ===

def advanced_ascii_art_extraction(text):
    """Extract text from ASCII art using multiple pattern recognition techniques"""
    if not text or len(text) < 5:
        return []
    
    extracted_sequences = []
    lines = text.split('\n')
    
    # Method 1: Vertical reading (column-by-column)
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
    
    # Method 2: Horizontal reading with ASCII art character removal
    for line in lines:
        cleaned = re.sub(r'[|/\\()[\]{}#@*=_\-+<>~^`.:;\'"!?$%&]', ' ', line)
        words = cleaned.split()
        for word in words:
            if len(word) >= 3 and word.isalpha():
                extracted_sequences.append(word.lower())
    
    # Method 3: Dense character block detection
    full_text = ' '.join(lines)
    letters_only = re.sub(r'[^a-zA-Z]', '', full_text).lower()
    
    if letters_only:
        for i in range(len(letters_only) - 2):
            chunk = letters_only[i:i+10]
            if len(chunk) >= 3:
                extracted_sequences.append(chunk[:8])
    
    return extracted_sequences

def comprehensive_unicode_to_ascii(text):
    """Convert ALL Unicode variations to ASCII - EXPANDED with Mathematical Alphanumeric"""
    if not text:
        return ""
    
    result = list(text)
    
    for i, char in enumerate(result):
        code = ord(char)
        
        # Mathematical Alphanumeric Symbols (0x1D400 - 0x1D7FF) - ALL variants
        # Bold uppercase (𝐀-𝐙)
        if 0x1D400 <= code <= 0x1D419:
            result[i] = chr(ord('A') + (code - 0x1D400))
        # Bold lowercase (𝐚-𝐳)
        elif 0x1D41A <= code <= 0x1D433:
            result[i] = chr(ord('a') + (code - 0x1D41A))
        # Italic uppercase (𝐴-𝑍)
        elif 0x1D434 <= code <= 0x1D44D:
            result[i] = chr(ord('A') + (code - 0x1D434))
        # Italic lowercase (𝑎-𝑧)
        elif 0x1D44E <= code <= 0x1D467:
            result[i] = chr(ord('a') + (code - 0x1D44E))
        # Bold Italic uppercase (𝑨-𝒁)
        elif 0x1D468 <= code <= 0x1D481:
            result[i] = chr(ord('A') + (code - 0x1D468))
        # Bold Italic lowercase (𝒂-𝒛)
        elif 0x1D482 <= code <= 0x1D49B:
            result[i] = chr(ord('a') + (code - 0x1D482))
        # Script uppercase (𝒜-𝒵)
        elif 0x1D49C <= code <= 0x1D4B5:
            result[i] = chr(ord('A') + (code - 0x1D49C))
        # Script lowercase (𝒶-𝓏)
        elif 0x1D4B6 <= code <= 0x1D4CF:
            result[i] = chr(ord('a') + (code - 0x1D4B6))
        # Bold Script uppercase (𝓐-𝓩)
        elif 0x1D4D0 <= code <= 0x1D4E9:
            result[i] = chr(ord('A') + (code - 0x1D4D0))
        # Bold Script lowercase (𝓪-𝔃)
        elif 0x1D4EA <= code <= 0x1D503:
            result[i] = chr(ord('a') + (code - 0x1D4EA))
        # Fraktur uppercase (𝔄-𝔜)
        elif 0x1D504 <= code <= 0x1D51D:
            result[i] = chr(ord('A') + (code - 0x1D504))
        # Fraktur lowercase (𝔞-𝔷)
        elif 0x1D51E <= code <= 0x1D537:
            result[i] = chr(ord('a') + (code - 0x1D51E))
        # Double-struck uppercase (𝔸-ℤ)
        elif 0x1D538 <= code <= 0x1D551:
            result[i] = chr(ord('A') + (code - 0x1D538))
        # Double-struck lowercase (𝕒-𝕫)
        elif 0x1D552 <= code <= 0x1D56B:
            result[i] = chr(ord('a') + (code - 0x1D552))
        # Bold Fraktur uppercase (𝕬-𝖅)
        elif 0x1D56C <= code <= 0x1D585:
            result[i] = chr(ord('A') + (code - 0x1D56C))
        # Bold Fraktur lowercase (𝖆-𝖟)
        elif 0x1D586 <= code <= 0x1D59F:
            result[i] = chr(ord('a') + (code - 0x1D586))
        # Sans-serif uppercase (𝖠-𝖹)
        elif 0x1D5A0 <= code <= 0x1D5B9:
            result[i] = chr(ord('A') + (code - 0x1D5A0))
        # Sans-serif lowercase (𝖺-𝗓)
        elif 0x1D5BA <= code <= 0x1D5D3:
            result[i] = chr(ord('a') + (code - 0x1D5BA))
        # Sans-serif bold uppercase (𝗔-𝗭)
        elif 0x1D5D4 <= code <= 0x1D5ED:
            result[i] = chr(ord('A') + (code - 0x1D5D4))
        # Sans-serif bold lowercase (𝗮-𝘇)
        elif 0x1D5EE <= code <= 0x1D607:
            result[i] = chr(ord('a') + (code - 0x1D5EE))
        # Sans-serif italic uppercase (𝘈-𝘡)
        elif 0x1D608 <= code <= 0x1D621:
            result[i] = chr(ord('A') + (code - 0x1D608))
        # Sans-serif italic lowercase (𝘢-𝘻)
        elif 0x1D622 <= code <= 0x1D63B:
            result[i] = chr(ord('a') + (code - 0x1D622))
        # Sans-serif bold italic uppercase (𝘼-𝙕)
        elif 0x1D63C <= code <= 0x1D655:
            result[i] = chr(ord('A') + (code - 0x1D63C))
        # Sans-serif bold italic lowercase (𝙖-𝙯)
        elif 0x1D656 <= code <= 0x1D66F:
            result[i] = chr(ord('a') + (code - 0x1D656))
        # Monospace uppercase (𝙰-𝚉)
        elif 0x1D670 <= code <= 0x1D689:
            result[i] = chr(ord('A') + (code - 0x1D670))
        # Monospace lowercase (𝚊-𝚣)
        elif 0x1D68A <= code <= 0x1D6A3:
            result[i] = chr(ord('a') + (code - 0x1D68A))
        
        # Mathematical digits
        elif 0x1D7CE <= code <= 0x1D7D7:
            result[i] = chr(ord('0') + (code - 0x1D7CE))
        elif 0x1D7D8 <= code <= 0x1D7E1:
            result[i] = chr(ord('0') + (code - 0x1D7D8))
        elif 0x1D7E2 <= code <= 0x1D7EB:
            result[i] = chr(ord('0') + (code - 0x1D7E2))
        elif 0x1D7EC <= code <= 0x1D7F5:
            result[i] = chr(ord('0') + (code - 0x1D7EC))
        elif 0x1D7F6 <= code <= 0x1D7FF:
            result[i] = chr(ord('0') + (code - 0x1D7F6))
        
        # Fullwidth forms
        elif 0xFF21 <= code <= 0xFF3A:
            result[i] = chr(ord('A') + (code - 0xFF21))
        elif 0xFF41 <= code <= 0xFF5A:
            result[i] = chr(ord('a') + (code - 0xFF41))
        elif 0xFF10 <= code <= 0xFF19:
            result[i] = chr(ord('0') + (code - 0xFF10))
        
        # Enclosed Alphanumerics
        elif 0x24B6 <= code <= 0x24CF:
            result[i] = chr(ord('A') + (code - 0x24B6))
        elif 0x24D0 <= code <= 0x24E9:
            result[i] = chr(ord('a') + (code - 0x24D0))
        
        # Regional Indicators (flags)
        elif 0x1F1E6 <= code <= 0x1F1FF:
            result[i] = chr(ord('A') + (code - 0x1F1E6))
        
        # Squared/Negative Squared Latin
        elif 0x1F130 <= code <= 0x1F149:
            result[i] = chr(ord('A') + (code - 0x1F130))
        elif 0x1F170 <= code <= 0x1F189:
            result[i] = chr(ord('A') + (code - 0x1F170))
        
        # Box Drawing - convert to space
        elif 0x2500 <= code <= 0x257F:
            result[i] = ' '
        
        # Block Elements - convert to space
        elif 0x2580 <= code <= 0x259F:
            result[i] = ' '
        
        # Cyrillic look-alikes
        elif char in 'АВСЕНІКМОРТУХавсеікморстух':
            cyrillic_map = {
                'А':'A','В':'B','С':'C','Е':'E','Н':'H','І':'I','К':'K','М':'M',
                'О':'O','Р':'P','Т':'T','У':'Y','Х':'X',
                'а':'a','в':'b','с':'c','е':'e','і':'i','к':'k','м':'m',
                'о':'o','р':'p','т':'t','у':'u','х':'x'
            }
            result[i] = cyrillic_map.get(char, char)
        
        # Greek look-alikes
        elif char in 'ΑΒΕΖΗΙΚΜΝΟΡΤΥΧαβεικοπτυχ':
            greek_map = {
                'Α':'A','Β':'B','Ε':'E','Ζ':'Z','Η':'H','Ι':'I','Κ':'K','Μ':'M',
                'Ν':'N','Ο':'O','Ρ':'P','Τ':'T','Υ':'Y','Χ':'X',
                'α':'a','β':'b','ε':'e','ι':'i','κ':'k','ο':'o','π':'p',
                'τ':'t','υ':'u','χ':'x'
            }
            result[i] = greek_map.get(char, char)
    
    return ''.join(result)

def detect_multi_line_art(text):
    """Detect if message is ASCII art based on structure"""
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
    
    for line in lines:
        if len(line) > 20:
            special_count = sum(1 for c in line if c in '|/\\()[]{}#@*=_-+<>~^`.:;')
            if special_count > len(line) * 0.3:
                return True
    
    return False

def is_whitelisted_word(word):
    """Check if word is whitelisted"""
    word_lower = word.lower()
    for whitelist_word in WHITELIST_WORDS:
        if word_lower == whitelist_word.lower():
            return True
    return False

def check_blocked_words_ultimate(text):
    """Ultimate blocked word detection with all extraction methods"""
    if not text:
        return False, []
    
    violations = []
    converted = comprehensive_unicode_to_ascii(text)
    normalized = re.sub(r'[^a-z0-9\s]', '', converted.lower())
    words = normalized.split()
    
    for word in words:
        if len(word) < 2 or is_whitelisted_word(word):
            continue
        
        for blocked in BLOCKED_WORDS:
            blocked_clean = re.sub(r'[^a-z]', '', blocked.lower())
            if len(blocked_clean) >= 2:
                if word == blocked_clean:
                    violations.append(f"Blocked word: '{blocked}'")
                elif blocked_clean in word and len(word) <= len(blocked_clean) + 3:
                    if not is_whitelisted_word(word):
                        violations.append(f"Blocked word (obfuscated): '{blocked}' in '{word}'")
    
    full_letters = re.sub(r'[^a-z]', '', converted.lower())
    for blocked in BLOCKED_WORDS:
        blocked_clean = re.sub(r'[^a-z]', '', blocked.lower())
        if len(blocked_clean) >= 2 and blocked_clean in full_letters:
            is_in_whitelist = False
            for word in words:
                if is_whitelisted_word(word) and blocked_clean in word.lower():
                    is_in_whitelist = True
                    break
            
            if not is_in_whitelist:
                violations.append(f"Blocked word (hidden): '{blocked}'")
    
    if '\n' in text or len(text) > 50:
        extracted_words = advanced_ascii_art_extraction(text)
        for extracted in extracted_words:
            for blocked in BLOCKED_WORDS:
                blocked_clean = re.sub(r'[^a-z]', '', blocked.lower())
                if len(blocked_clean) >= 2:
                    if blocked_clean in extracted:
                        violations.append(f"Blocked word (ASCII art): '{blocked}' detected in art")
    
    return len(violations) > 0, list(set(violations))

def detect_non_english(text):
    """Detect non-English language"""
    if not text or len(text.strip()) < 3:
        return False
    
    cleaned_text = re.sub(r'http[s]?://\S+', '', text)
    cleaned_text = re.sub(r'<@[!&]?\d+>', '', cleaned_text)
    cleaned_text = re.sub(r'<#\d+>', '', cleaned_text)
    cleaned_text = re.sub(r'<:\w+:\d+>', '', cleaned_text)
    
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
    """Main analysis with comprehensive detection"""
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
    
    markdown_chars = content.count('*') + content.count('_') + content.count('~') + content.count('|') + content.count('`')
    if len(content) > 10 and markdown_chars > len(content) * 0.5:
        violations.append("Excessive formatting (possible bypass)")
    
    return len(violations) > 0, violations

def check_auto_reply(message_content):
    """Check if message matches auto-reply pattern"""
    if not message_content or len(message_content.strip()) < 3:
        return None
    
    cleaned_content = message_content.strip()
    for pattern, reply_data in AUTO_REPLY_PATTERNS.items():
        if re.search(pattern, cleaned_content):
            return reply_data['response']
    return None

# === MESSAGE PROCESSING ===

async def process_message(message, is_edit=False):
    if message.author.bot or not message.guild:
        return
    
    if message.channel.id not in MONITORED_CHANNELS:
        await bot.process_commands(message)
        return
    
    guild_member = message.guild.get_member(message.author.id)
    if not guild_member:
        return
    
    # Check auto-reply first (works for everyone including bypass roles)
    auto_reply = check_auto_reply(message.content)
    if auto_reply:
        try:
            await message.reply(auto_reply)
        except:
            pass
    
    # If user has bypass role, skip moderation
    if any(role.id in BYPASS_ROLES for role in guild_member.roles):
        return
    
    # Check non-English
    if detect_non_english(message.content):
        try:
            await message.delete()
        except discord.Forbidden:
            pass
        
        try:
            embed = discord.Embed(
                title="🌐 Language Notice",
                description="Please speak English only.",
                color=0x3498db
            )
            await message.channel.send(embed=embed, delete_after=10)
        except:
            pass
        return
    
    # Analyze content
    is_violation, violation_reasons = analyze_message_content(message.content)
    
    if is_violation:
        try:
            await message.delete()
        except discord.Forbidden:
            pass
        
        # Log
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            violation_text = '\n'.join(f"• {reason}" for reason in violation_reasons[:5])
            
            display_content = message.content
            if len(display_content) > 500:
                display_content = display_content[:497] + "..."
            
            title = "🚫 Message Blocked" if not is_edit else "🚫 Edited Message Blocked"
            embed = discord.Embed(
                title=title,
                description=f"**User:** {guild_member.mention}\n**Channel:** {message.channel.mention}",
                color=0xff4444,
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            embed.add_field(name="Violations", value=violation_text, inline=False)
            embed.add_field(name="Original Message", value=f"```\n{display_content}\n```", inline=False)
            
            converted = comprehensive_unicode_to_ascii(message.content)
            if converted != message.content and len(converted) < 300:
                embed.add_field(name="Converted", value=f"```\n{converted[:200]}\n```", inline=False)
            
            if detect_multi_line_art(message.content):
                extracted = advanced_ascii_art_extraction(message.content)
                if extracted:
                    embed.add_field(name="Extracted from Art", value=f"`{', '.join(extracted[:10])}`", inline=False)
            
            try:
                await log_channel.send(embed=embed)
            except Exception as e:
                print(f"Error sending to log: {e}")
        
        # DM user
        try:
            embed = discord.Embed(
                title="⚠️ Message Removed",
                description="Your message was removed for violating server rules.",
                color=0xffaa00
            )
            embed.add_field(
                name="Server Rules",
                value="• Use appropriate language\n• No unauthorized links\n• No filter bypass attempts\n• No ASCII art to hide words\n• Keep messages respectful",
                inline=False
            )
            await guild_member.send(embed=embed)
        except:
            pass
        
        return
    
    await bot.process_commands(message)

# === CHANNEL SCANNER (SCANS ON BOT START) ===

@tasks.loop(count=1)
async def scan_channels_on_startup():
    """Scan all monitored channels for violations when bot starts"""
    await bot.wait_until_ready()
    print("🔍 Starting channel scan for existing messages...")
    
    deleted_count = 0
    for channel_id in MONITORED_CHANNELS:
        try:
            channel = bot.get_channel(channel_id)
            if not channel:
                continue
            
            async for message in channel.history(limit=100):
                if message.author.bot:
                    continue
                
                guild_member = message.guild.get_member(message.author.id)
                if not guild_member:
                    continue
                
                if any(role.id in BYPASS_ROLES for role in guild_member.roles):
                    continue
                
                # Check violations
                is_violation, violation_reasons = analyze_message_content(message.content)
                is_non_english = detect_non_english(message.content)
                
                if is_violation or is_non_english:
                    try:
                        await message.delete()
                        deleted_count += 1
                        print(f"   Deleted old message from {message.author.name} in #{channel.name}")
                        await asyncio.sleep(1)  # Rate limit protection
                    except:
                        pass
        except Exception as e:
            print(f"Error scanning channel {channel_id}: {e}")
    
    print(f"✅ Channel scan complete! Deleted {deleted_count} violating messages.")

# === HEALTH CHECK SERVER ===

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

# === EVENTS ===

@bot.event
async def on_ready():
    print(f'✅ {bot.user} is online!')
    print(f'📢 Monitoring channels: {MONITORED_CHANNELS}')
    print(f'🛡️ Ultimate ASCII art detection: ENABLED')
    print(f'🔍 Scanning for: {len(BLOCKED_WORDS)} blocked words')
    print(f'🤖 Auto-reply patterns: {len(AUTO_REPLY_PATTERNS)} active')
    
    # Start health server
    bot.loop.create_task(health_check_server())
    
    # Start channel scanner
    scan_channels_on_startup.start()

@bot.event
async def on_message(message):
    await process_message(message, is_edit=False)

@bot.event
async def on_message_edit(before, after):
    await process_message(after, is_edit=True)

# === ADMIN COMMANDS ===

@bot.command(name="addchannel")
@commands.has_permissions(administrator=True)
async def add_channel(ctx, channel: discord.TextChannel):
    if channel.id in MONITORED_CHANNELS:
        await ctx.send(f"⚠️ {channel.mention} already monitored.", delete_after=10)
    else:
        MONITORED_CHANNELS.append(channel.id)
        await ctx.send(f"✅ Now monitoring {channel.mention}", delete_after=10)

@bot.command(name="removechannel")
@commands.has_permissions(administrator=True)
async def remove_channel(ctx, channel: discord.TextChannel):
    if channel.id in MONITORED_CHANNELS:
        MONITORED_CHANNELS.remove(channel.id)
        await ctx.send(f"✅ Stopped monitoring {channel.mention}", delete_after=10)
    else:
        await ctx.send(f"⚠️ {channel.mention} not monitored.", delete_after=10)

@bot.command(name="listchannels")
@commands.has_permissions(administrator=True)
async def list_channels(ctx):
    if MONITORED_CHANNELS:
        channels = [f"<#{ch_id}>" for ch_id in MONITORED_CHANNELS]
        await ctx.send(f"📢 **Monitored channels:**\n" + "\n".join(channels), delete_after=30)
    else:
        await ctx.send("⚠️ No channels monitored.", delete_after=10)

@bot.command(name="rescan")
@commands.has_permissions(administrator=True)
async def rescan_channels(ctx):
    """Manually trigger a channel rescan"""
    await ctx.send("🔍 Starting channel rescan...", delete_after=5)
    
    deleted_count = 0
    for channel_id in MONITORED_CHANNELS:
        try:
            channel = bot.get_channel(channel_id)
            if not channel:
                continue
            
            async for message in channel.history(limit=100):
                if message.author.bot:
                    continue
                
                guild_member = message.guild.get_member(message.author.id)
                if not guild_member or any(role.id in BYPASS_ROLES for role in guild_member.roles):
                    continue
                
                is_violation, _ = analyze_message_content(message.content)
                is_non_english = detect_non_english(message.content)
                
                if is_violation or is_non_english:
                    try:
                        await message.delete()
                        deleted_count += 1
                        await asyncio.sleep(1)
                    except:
                        pass
        except:
            pass
    
    await ctx.send(f"✅ Rescan complete! Deleted {deleted_count} messages.", delete_after=15)

@bot.command(name="testmessage")
@commands.has_permissions(administrator=True)
async def test_message(ctx, *, text: str):
    """Test if a message would be blocked"""
    is_violation, violations = analyze_message_content(text)
    
    embed = discord.Embed(
        title="🔍 Ultimate Scanner Test",
        color=0xff4444 if is_violation else 0x44ff44
    )
    
    if is_violation:
        embed.add_field(name="🚫 BLOCKED", value="Message would be deleted", inline=False)
        embed.add_field(name="Violations", value='\n'.join(f"• {v}" for v in violations[:5]), inline=False)
    else:
        embed.add_field(name="✅ ALLOWED", value="Message would pass", inline=False)
    
    embed.add_field(name="Original", value=f"```{text[:150]}```", inline=False)
    
    converted = comprehensive_unicode_to_ascii(text)
    if converted != text:
        embed.add_field(name="Unicode→ASCII", value=f"```{converted[:150]}```", inline=False)
    
    if detect_multi_line_art(text):
        extracted = advanced_ascii_art_extraction(text)
        if extracted:
            embed.add_field(name="ASCII Art Extraction", value=f"`{', '.join(extracted[:8])}`", inline=False)
    
    await ctx.send(embed=embed, delete_after=60)

@bot.command(name="filterhelp")
@commands.has_permissions(administrator=True)
async def filter_help(ctx):
    """Show all commands"""
    embed = discord.Embed(
        title="🛡️ Ultimate Filter Bot Commands",
        description="Comprehensive bypass detection system",
        color=0x3498db
    )
    
    embed.add_field(
        name="📢 Channel Management",
        value="`$addchannel #channel` - Monitor channel\n"
              "`$removechannel #channel` - Stop monitoring\n"
              "`$listchannels` - Show monitored channels\n"
              "`$rescan` - Scan channels for violations",
        inline=False
    )
    
    embed.add_field(
        name="🔍 Testing Tools",
        value="`$testmessage <text>` - Full message test\n"
              "`$stats` - Show bot statistics",
        inline=False
    )
    
    embed.add_field(
        name="🎯 Features",
        value="✅ Auto-scans on startup\n"
              "✅ Auto-reply system\n"
              "✅ 500+ Unicode fonts detected\n"
              "✅ ASCII art extraction\n"
              "✅ Language detection\n"
              "✅ Health check for Render",
        inline=False
    )
    
    await ctx.send(embed=embed, delete_after=90)

@bot.command(name="stats")
@commands.has_permissions(administrator=True)
async def show_stats(ctx):
    """Show bot statistics"""
    embed = discord.Embed(
        title="📊 Filter Bot Statistics",
        color=0x2ecc71
    )
    
    embed.add_field(name="Monitored Channels", value=str(len(MONITORED_CHANNELS)), inline=True)
    embed.add_field(name="Blocked Words", value=str(len(BLOCKED_WORDS)), inline=True)
    embed.add_field(name="Auto-Reply Patterns", value=str(len(AUTO_REPLY_PATTERNS)), inline=True)
    embed.add_field(name="Servers", value=str(len(bot.guilds)), inline=True)
    embed.add_field(name="Status", value="🟢 Active", inline=True)
    
    await ctx.send(embed=embed, delete_after=30)

# === ERROR HANDLING ===

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.", delete_after=10)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing required argument. Use `$filterhelp` for command list.", delete_after=10)
    else:
        print(f"Command error: {error}")

# === START BOT ===

if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN")
    
    if not token:
        print("❌ Bot token not found! Set DISCORD_TOKEN or TOKEN in your .env file.")
        exit(1)
    
    print("🚀 Starting Ultimate Filter Bot...")
    try:
        bot.run(token)
    except discord.LoginFailure:
        print("❌ Invalid bot token!")
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
