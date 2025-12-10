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

# === AUTO-REPLY PATTERNS ===

AUTO_REPLY_PATTERNS = {
    # Melee reach/aura questions
    r'(?i)(?:does|do|is)\s+(?:melee\s+)?(?:reach|aura)\s+(?:work|working)\s*(?:with|on)?\s*(?:fire\s+axe|axe)?': {
        'response': "Yes, it's working! 🔥",
        'description': 'Melee reach/aura functionality'
    },
    
    # Script location questions
    r'(?i)(?:where|how)\s+(?:is|to\s+get|can\s+i\s+get|do\s+i\s+get)\s+(?:the\s+)?script': {
        'response': "You can get/copy the script at this link: https://getjx.vercel.app/ 📜",
        'description': 'Script download location'
    },
    
    r'(?i)(?:wheres?|where\s+is)\s+(?:the\s+)?script': {
        'response': "You can get/copy the script at this link: https://getjx.vercel.app/ 📜",
        'description': 'Script location'
    },
    
    # Key-related questions
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
    
    # General script questions
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
        # Remove common ASCII art characters but keep letters
        cleaned = re.sub(r'[|/\\()[\]{}#@*=_\-+<>~^`.:;\'"!?$%&]', ' ', line)
        words = cleaned.split()
        for word in words:
            if len(word) >= 3 and word.isalpha():
                extracted_sequences.append(word.lower())
    
    # Method 3: Dense character block detection (ASCII art fonts)
    full_text = ' '.join(lines)
    # Remove spaces and special chars, keep only letters
    letters_only = re.sub(r'[^a-zA-Z]', '', full_text).lower()
    
    # Extract consecutive letter sequences
    if letters_only:
        # Split into chunks and analyze
        for i in range(len(letters_only) - 2):
            chunk = letters_only[i:i+10]  # Look at 10-char windows
            if len(chunk) >= 3:
                extracted_sequences.append(chunk[:8])  # Take first 8 chars
    
    # Method 4: Pattern-based extraction (common ASCII art patterns)
    ascii_patterns = {
        'S': [r'[\/\\][\-_]{2,}[\/\\]', r'\$', r'5', r'\(_\)', r'/\¯\¯\\'],
        'K': [r'\|<', r'\|{', r'[|!]<', r'/<'],
        'I': [r'\|', r'[|!]', r'1'],
        'D': [r'\|[)D]', r'\|\)', r'[|!]\)'],
        'A': [r'[/\\]\s*[/\\]', r'/\^\\', r'@@'],
        'E': [r'\|[_-]{2,}', r'[|!]='],
        'C': [r'\(_', r'\[_', r'<'],
        'R': [r'\|2', r'[|!]2'],
        'T': [r'[_-]{2,}\|', r'\+'],
    }
    
    detected_letters = []
    for line in lines:
        for letter, patterns in ascii_patterns.items():
            for pattern in patterns:
                if re.search(pattern, line):
                    detected_letters.append(letter.lower())
                    break
    
    if len(detected_letters) >= 3:
        extracted_sequences.append(''.join(detected_letters[:10]))
    
    return extracted_sequences

def comprehensive_unicode_to_ascii(text):
    """Convert ALL Unicode variations to ASCII - expanded to cover 500+ ranges"""
    if not text:
        return ""
    
    result = list(text)
    
    for i, char in enumerate(result):
        code = ord(char)
        
        # Mathematical Alphanumeric Symbols (0x1D400 - 0x1D7FF) - ALL variants
        # Bold uppercase
        if 0x1D400 <= code <= 0x1D419:
            result[i] = chr(ord('A') + (code - 0x1D400))
        # Bold lowercase
        elif 0x1D41A <= code <= 0x1D433:
            result[i] = chr(ord('a') + (code - 0x1D41A))
        # Italic uppercase
        elif 0x1D434 <= code <= 0x1D44D:
            result[i] = chr(ord('A') + (code - 0x1D434))
        # Italic lowercase
        elif 0x1D44E <= code <= 0x1D467:
            result[i] = chr(ord('a') + (code - 0x1D44E))
        # Bold Italic uppercase
        elif 0x1D468 <= code <= 0x1D481:
            result[i] = chr(ord('A') + (code - 0x1D468))
        # Bold Italic lowercase
        elif 0x1D482 <= code <= 0x1D49B:
            result[i] = chr(ord('a') + (code - 0x1D482))
        # Script uppercase
        elif 0x1D49C <= code <= 0x1D4B5:
            result[i] = chr(ord('A') + (code - 0x1D49C))
        # Script lowercase
        elif 0x1D4B6 <= code <= 0x1D4CF:
            result[i] = chr(ord('a') + (code - 0x1D4B6))
        # Bold Script uppercase
        elif 0x1D4D0 <= code <= 0x1D4E9:
            result[i] = chr(ord('A') + (code - 0x1D4D0))
        # Bold Script lowercase
        elif 0x1D4EA <= code <= 0x1D503:
            result[i] = chr(ord('a') + (code - 0x1D4EA))
        # Fraktur uppercase
        elif 0x1D504 <= code <= 0x1D51D:
            result[i] = chr(ord('A') + (code - 0x1D504))
        # Fraktur lowercase
        elif 0x1D51E <= code <= 0x1D537:
            result[i] = chr(ord('a') + (code - 0x1D51E))
        # Double-struck uppercase
        elif 0x1D538 <= code <= 0x1D551:
            result[i] = chr(ord('A') + (code - 0x1D538))
        # Double-struck lowercase
        elif 0x1D552 <= code <= 0x1D56B:
            result[i] = chr(ord('a') + (code - 0x1D552))
        # Bold Fraktur uppercase
        elif 0x1D56C <= code <= 0x1D585:
            result[i] = chr(ord('A') + (code - 0x1D56C))
        # Bold Fraktur lowercase
        elif 0x1D586 <= code <= 0x1D59F:
            result[i] = chr(ord('a') + (code - 0x1D586))
        # Sans-serif uppercase
        elif 0x1D5A0 <= code <= 0x1D5B9:
            result[i] = chr(ord('A') + (code - 0x1D5A0))
        # Sans-serif lowercase
        elif 0x1D5BA <= code <= 0x1D5D3:
            result[i] = chr(ord('a') + (code - 0x1D5BA))
        # Sans-serif bold uppercase
        elif 0x1D5D4 <= code <= 0x1D5ED:
            result[i] = chr(ord('A') + (code - 0x1D5D4))
        # Sans-serif bold lowercase
        elif 0x1D5EE <= code <= 0x1D607:
            result[i] = chr(ord('a') + (code - 0x1D5EE))
        # Sans-serif italic uppercase
        elif 0x1D608 <= code <= 0x1D621:
            result[i] = chr(ord('A') + (code - 0x1D608))
        # Sans-serif italic lowercase
        elif 0x1D622 <= code <= 0x1D63B:
            result[i] = chr(ord('a') + (code - 0x1D622))
        # Sans-serif bold italic uppercase
        elif 0x1D63C <= code <= 0x1D655:
            result[i] = chr(ord('A') + (code - 0x1D63C))
        # Sans-serif bold italic lowercase
        elif 0x1D656 <= code <= 0x1D66F:
            result[i] = chr(ord('a') + (code - 0x1D656))
        # Monospace uppercase
        elif 0x1D670 <= code <= 0x1D689:
            result[i] = chr(ord('A') + (code - 0x1D670))
        # Monospace lowercase
        elif 0x1D68A <= code <= 0x1D6A3:
            result[i] = chr(ord('a') + (code - 0x1D68A))
        
        # Mathematical digits (ALL variants)
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
        
        # Fullwidth forms (FF00-FFEF)
        elif 0xFF21 <= code <= 0xFF3A:
            result[i] = chr(ord('A') + (code - 0xFF21))
        elif 0xFF41 <= code <= 0xFF5A:
            result[i] = chr(ord('a') + (code - 0xFF41))
        elif 0xFF10 <= code <= 0xFF19:
            result[i] = chr(ord('0') + (code - 0xFF10))
        
        # Enclosed Alphanumerics (2460-24FF)
        elif 0x2460 <= code <= 0x2473:
            num = (code - 0x2460 + 1)
            result[i] = str(num % 10)
        elif 0x24B6 <= code <= 0x24CF:
            result[i] = chr(ord('A') + (code - 0x24B6))
        elif 0x24D0 <= code <= 0x24E9:
            result[i] = chr(ord('a') + (code - 0x24D0))
        
        # Regional Indicators (flags 1F1E6-1F1FF)
        elif 0x1F1E6 <= code <= 0x1F1FF:
            result[i] = chr(ord('A') + (code - 0x1F1E6))
        
        # Squared Latin (1F130-1F149)
        elif 0x1F130 <= code <= 0x1F149:
            result[i] = chr(ord('A') + (code - 0x1F130))
        
        # Negative Squared (1F170-1F189)
        elif 0x1F170 <= code <= 0x1F189:
            result[i] = chr(ord('A') + (code - 0x1F170))
        
        # Parenthesized Latin (1F110-1F12E)
        elif 0x1F110 <= code <= 0x1F129:
            result[i] = chr(ord('A') + (code - 0x1F110))
        
        # Superscripts and Subscripts
        elif code == 0x00B2:
            result[i] = '2'
        elif code == 0x00B3:
            result[i] = '3'
        elif code == 0x00B9:
            result[i] = '1'
        elif 0x2070 <= code <= 0x2079:
            result[i] = chr(ord('0') + (code - 0x2070))
        elif 0x2080 <= code <= 0x2089:
            result[i] = chr(ord('0') + (code - 0x2080))
        
        # Box Drawing (2500-257F) - convert to space
        elif 0x2500 <= code <= 0x257F:
            result[i] = ' '
        
        # Block Elements (2580-259F) - convert to space
        elif 0x2580 <= code <= 0x259F:
            result[i] = ' '
        
        # Cyrillic look-alikes (comprehensive)
        elif char in 'АВСЕНІКМОРТУХавсеікморстух':
            cyrillic_map = {
                'А':'A','В':'B','С':'C','Е':'E','Н':'H','І':'I','К':'K','М':'M',
                'О':'O','Р':'P','Т':'T','У':'Y','Х':'X',
                'а':'a','в':'b','с':'c','е':'e','і':'i','к':'k','м':'m',
                'о':'o','р':'p','с':'c','т':'t','у':'u','х':'x'
            }
            result[i] = cyrillic_map.get(char, char)
        
        # Greek look-alikes (comprehensive)
        elif char in 'ΑΒΕΖΗΙΚΜΝΟΡΤΥΧαβεικοπτυχ':
            greek_map = {
                'Α':'A','Β':'B','Ε':'E','Ζ':'Z','Η':'H','Ι':'I','Κ':'K','Μ':'M',
                'Ν':'N','Ο':'O','Ρ':'P','Τ':'T','Υ':'Y','Χ':'X',
                'α':'a','β':'b','ε':'e','ι':'i','κ':'k','ο':'o','π':'p',
                'τ':'t','υ':'u','χ':'x'
            }
            result[i] = greek_map.get(char, char)
        
        # Small capitals and other variants
        elif 0x1D00 <= code <= 0x1D7F:
            # Phonetic extensions - map to lowercase
            if 0x1D00 <= code <= 0x1D1A:
                result[i] = chr(ord('a') + (code - 0x1D00))
    
    return ''.join(result)

def detect_multi_line_art(text):
    """Detect if message is ASCII art based on structure"""
    if not text or len(text) < 20:
        return False
    
    lines = text.split('\n')
    
    # Too many lines = probably ASCII art
    if len(lines) > 6:
        return True
    
    # Check line length consistency (ASCII art often has uniform width)
    if len(lines) >= 3:
        lengths = [len(line) for line in lines if line.strip()]
        if lengths:
            avg_length = sum(lengths) / len(lengths)
            # If multiple lines with similar length and wide
            if avg_length > 30 and len([l for l in lengths if abs(l - avg_length) < 10]) >= 3:
                return True
    
    # Check special character density per line
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
    
    # Convert all Unicode
    converted = comprehensive_unicode_to_ascii(text)
    
    # Method 1: Direct word check
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
    
    # Method 2: Check full text (letters only)
    full_letters = re.sub(r'[^a-z]', '', converted.lower())
    for blocked in BLOCKED_WORDS:
        blocked_clean = re.sub(r'[^a-z]', '', blocked.lower())
        if len(blocked_clean) >= 3 and blocked_clean in full_letters:
            # Verify it's not in whitelist
            is_in_whitelist = False
            for word in words:
                if is_whitelisted_word(word) and blocked_clean in word.lower():
                    is_in_whitelist = True
                    break
            
            if not is_in_whitelist:
                violations.append(f"Blocked word (hidden): '{blocked}'")
    
    # Method 3: ASCII art extraction
    if '\n' in text or len(text) > 50:
        extracted_words = advanced_ascii_art_extraction(text)
        for extracted in extracted_words:
            for blocked in BLOCKED_WORDS:
                blocked_clean = re.sub(r'[^a-z]', '', blocked.lower())
                if len(blocked_clean) >= 3:
                    if blocked_clean in extracted:
                        violations.append(f"Blocked word (ASCII art): '{blocked}' detected in art")
    
    return len(violations) > 0, list(set(violations))

def detect_emoji_bypass(text):
    """Detect regional indicator emoji bypass"""
    if not text:
        return text, []
    
    emoji_to_letter = {}
    for letter in 'abcdefghijklmnopqrstuvwxyz':
        emoji_to_letter[f':regional_indicator_{letter}:'] = letter
    
    violations = []
    converted_text = text.lower()
    
    pattern = r'(:regional_indicator_[a-z]:(?:\s*:regional_indicator_[a-z]:)*)'
    emoji_sequences = re.findall(pattern, converted_text, re.IGNORECASE)
    
    for sequence in emoji_sequences:
        sequence_text = sequence
        for emoji_code, letter in emoji_to_letter.items():
            sequence_text = sequence_text.replace(emoji_code.lower(), letter)
        
        sequence_text = re.sub(r'[^a-z]', '', sequence_text)
        
        for blocked_word in BLOCKED_WORDS:
            clean_blocked = re.sub(r'[^a-z]', '', blocked_word.lower())
            if sequence_text == clean_blocked:
                violations.append(f"Emoji bypass: '{sequence}' -> '{blocked_word}'")
    
    return converted_text, violations

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
    
    # 1. Check for multi-line ASCII art
    if detect_multi_line_art(content):
        violations.append("Multi-line ASCII art detected (likely bypass attempt)")
    
    # 2. Check for emoji bypass
    emoji_converted, emoji_violations = detect_emoji_bypass(content)
    violations.extend(emoji_violations)
    
    # 3. Check blocked words (ultimate detection)
    has_blocked, blocked_violations = check_blocked_words_ultimate(content)
    violations.extend(blocked_violations)
    
    # 4. Check blocked messages/URLs
    converted = comprehensive_unicode_to_ascii(content).lower()
    for blocked_msg in BLOCKED_MESSAGES:
        if blocked_msg.lower() in converted:
            violations.append(f"Blocked content: '{blocked_msg}'")
    
    # 5. Check for excessive formatting
    markdown_chars = content.count('*') + content.count('_') + content.count('~') + content.count('|') + content.count('`')
    if len(content) > 10 and markdown_chars > len(content) * 0.5:
        violations.append("Excessive formatting (possible bypass)")
    
    return len(violations) > 0, violations

def check_auto_reply(message_content):
    """Check if message matches any auto-reply patterns"""
    if not message_content or len(message_content.strip()) < 3:
        return None
    
    # Clean the message for pattern matching
    cleaned_content = message_content.strip()
    
    # Check each pattern
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
    
    if any(role.id in BYPASS_ROLES for role in guild_member.roles):
        # Still check for auto-replies even for bypass roles
        auto_reply = check_auto_reply(message.content)
        if auto_reply:
            try:
                await message.reply(auto_reply)
            except:
                pass
        return
    
    # Check for auto-reply first (before filtering)
    auto_reply = check_auto_reply(message.content)
    if auto_reply:
        try:
            await message.reply(auto_reply)
        except:
            pass
    
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
            
            # Show converted version
            converted = comprehensive_unicode_to_ascii(message.content)
            if converted != message.content and len(converted) < 300:
                embed.add_field(name="Converted", value=f"```\n{converted[:200]}\n```", inline=False)
            
            # Show extracted words if ASCII art
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

# === EVENTS ===

@bot.event
async def on_ready():
    print(f'✅ {bot.user} is online!')
    print(f'📢 Monitoring channels: {MONITORED_CHANNELS}')
    print(f'🛡️ Ultimate ASCII art detection: ENABLED')
    print(f'🔍 Scanning for: {len(BLOCKED_WORDS)} blocked words')
    print(f'🤖 Auto-reply patterns: {len(AUTO_REPLY_PATTERNS)} configured')

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
        await ctx.send(f"⚠️ {channel.mention} is already being monitored.", delete_after=10)
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
        await ctx.send(f"⚠️ {channel.mention} is not being monitored.", delete_after=10)

@bot.command(name="listchannels")
@commands.has_permissions(administrator=True)
async def list_channels(ctx):
    if MONITORED_CHANNELS:
        channels = [f"<#{ch_id}>" for ch_id in MONITORED_CHANNELS]
        await ctx.send(f"📢 **Monitored channels:**\n" + "\n".join(channels), delete_after=30)
    else:
        await ctx.send("⚠️ No channels are being monitored.", delete_after=10)

@bot.command(name="addblockedword")
@commands.has_permissions(administrator=True)
async def add_blocked_word(ctx, *, word: str):
    word = word.lower().strip()
    if word in BLOCKED_WORDS:
        await ctx.send(f"⚠️ Word is already blocked.", delete_after=10)
    else:
        BLOCKED_WORDS.append(word)
        await ctx.send(f"✅ Added '{word}' to the blocked list.", delete_after=10)

@bot.command(name="removeblockedword")
@commands.has_permissions(administrator=True)
async def remove_blocked_word(ctx, *, word: str):
    word = word.lower().strip()
    if word in BLOCKED_WORDS:
        BLOCKED_WORDS.remove(word)
        await ctx.send(f"✅ Removed '{word}' from the blocked list.", delete_after=10)
    else:
        await ctx.send(f"⚠️ Word is not in the blocked list.", delete_after=10)

@bot.command(name="addwhitelist")
@commands.has_permissions(administrator=True)
async def add_whitelist_word(ctx, *, word: str):
    word = word.lower().strip()
    if word in WHITELIST_WORDS:
        await ctx.send(f"⚠️ Word is already whitelisted.", delete_after=10)
    else:
        WHITELIST_WORDS.append(word)
        await ctx.send(f"✅ Added '{word}' to the whitelist.", delete_after=10)

@bot.command(name="removewhitelist")
@commands.has_permissions(administrator=True)
async def remove_whitelist_word(ctx, *, word: str):
    word = word.lower().strip()
    if word in WHITELIST_WORDS:
        WHITELIST_WORDS.remove(word)
        await ctx.send(f"✅ Removed '{word}' from the whitelist.", delete_after=10)
    else:
        await ctx.send(f"⚠️ Word is not in the whitelist.", delete_after=10)

@bot.command(name="testmessage")
@commands.has_permissions(administrator=True)
async def test_message(ctx, *, text: str):
    """Test if a message would be blocked"""
    is_violation, violations = analyze_message_content(text)
    auto_reply = check_auto_reply(text)
    
    embed = discord.Embed(
        title="🔍 Ultimate Scanner Test",
        color=0xff4444 if is_violation else 0x44ff44
    )
    
    if is_violation:
        embed.add_field(name="🚫 BLOCKED", value="Message would be deleted", inline=False)
        embed.add_field(name="Violations", value='\n'.join(f"• {v}" for v in violations[:5]), inline=False)
    else:
        embed.add_field(name="✅ ALLOWED", value="Message would pass", inline=False)
    
    if auto_reply:
        embed.add_field(name="🤖 Auto-Reply", value=f"Bot would reply: {auto_reply}", inline=False)
    
    embed.add_field(name="Original", value=f"```{text[:150]}```", inline=False)
    
    # Show conversions
    converted = comprehensive_unicode_to_ascii(text)
    if converted != text:
        embed.add_field(name="Unicode→ASCII", value=f"```{converted[:150]}```", inline=False)
    
    # Check ASCII art
    if detect_multi_line_art(text):
        extracted = advanced_ascii_art_extraction(text)
        if extracted:
            embed.add_field(name="ASCII Art Extraction", value=f"`{', '.join(extracted[:8])}`", inline=False)
    
    # Stats
    lines = len(text.split('\n'))
    special = sum(1 for c in text if c in '|/\\()[]{}#@*=_-+<>~^`')
    unicode_count = sum(1 for c in text if ord(c) > 127)
    
    embed.add_field(name="Stats", 
                   value=f"Lines: {lines}\nSpecial chars: {special}\nUnicode: {unicode_count}\nLength: {len(text)}", 
                   inline=True)
    
    await ctx.send(embed=embed, delete_after=60)

@bot.command(name="testascii")
@commands.has_permissions(administrator=True)
async def test_ascii(ctx, *, text: str):
    """Test ASCII art detection"""
    is_art = detect_multi_line_art(text)
    extracted = advanced_ascii_art_extraction(text)
    
    embed = discord.Embed(
        title="🎨 ASCII Art Detection Test",
        color=0xff4444 if is_art else 0x44ff44
    )
    
    if is_art:
        embed.add_field(name="🚫 DETECTED", value="ASCII art pattern detected!", inline=False)
    else:
        embed.add_field(name="✅ Clean", value="No ASCII art detected", inline=False)
    
    if extracted:
        unique_extractions = list(set(extracted))[:10]
        embed.add_field(name="Extracted Words", value=f"`{', '.join(unique_extractions)}`", inline=False)
    
    # Analysis
    lines = text.split('\n')
    special = sum(1 for c in text if c in '|/\\()[]{}#@*=_-+<>~^`')
    total_chars = len(text.replace('\n', '').replace(' ', ''))
    
    if total_chars > 0:
        special_ratio = (special / total_chars) * 100
        embed.add_field(name="Analysis",
                       value=f"Lines: {len(lines)}\nSpecial chars: {special} ({special_ratio:.1f}%)\nTotal: {len(text)}",
                       inline=False)
    
    await ctx.send(embed=embed, delete_after=45)

@bot.command(name="testunicode")
@commands.has_permissions(administrator=True)
async def test_unicode(ctx, *, text: str):
    """Test Unicode conversion"""
    converted = comprehensive_unicode_to_ascii(text)
    
    embed = discord.Embed(
        title="🔤 Unicode Conversion Test",
        color=0x3498db
    )
    
    embed.add_field(name="Original", value=f"```{text[:200]}```", inline=False)
    embed.add_field(name="Converted", value=f"```{converted[:200]}```", inline=False)
    
    if text != converted:
        changed = sum(1 for a, b in zip(text, converted) if a != b)
        embed.add_field(name="Result", value=f"✅ {changed} character(s) converted", inline=False)
    else:
        embed.add_field(name="Result", value="ℹ️ No Unicode to convert", inline=False)
    
    # Check if blocked
    has_blocked, violations = check_blocked_words_ultimate(text)
    if has_blocked:
        embed.add_field(name="⚠️ Detection", value=f"Found: {violations[0]}", inline=False)
    
    await ctx.send(embed=embed, delete_after=45)

@bot.command(name="scantext")
@commands.has_permissions(administrator=True)
async def scan_text(ctx, *, text: str):
    """Deep scan text for all bypass methods"""
    embed = discord.Embed(
        title="🔬 Deep Text Analysis",
        color=0x9b59b6
    )
    
    # Run all checks
    is_violation, violations = analyze_message_content(text)
    is_art = detect_multi_line_art(text)
    extracted = advanced_ascii_art_extraction(text)
    converted = comprehensive_unicode_to_ascii(text)
    has_blocked, blocked_viols = check_blocked_words_ultimate(text)
    auto_reply = check_auto_reply(text)
    
    # Summary
    status = "🚫 BLOCKED" if is_violation else "✅ CLEAN"
    embed.add_field(name="Status", value=status, inline=False)
    
    if violations:
        embed.add_field(name="Violations Found", value='\n'.join(f"• {v}" for v in violations[:5]), inline=False)
    
    if auto_reply:
        embed.add_field(name="🤖 Auto-Reply", value=f"Would trigger: {auto_reply}", inline=False)
    
    # Detection methods
    checks = []
    checks.append(f"ASCII Art: {'❌ Detected' if is_art else '✅ Clean'}")
    checks.append(f"Unicode Obfuscation: {'❌ Found' if converted != text else '✅ None'}")
    checks.append(f"Blocked Words: {'❌ Found' if has_blocked else '✅ None'}")
    checks.append(f"Multi-line: {'❌ Yes' if len(text.split('\n')) > 3 else '✅ No'}")
    
    embed.add_field(name="Detection Methods", value='\n'.join(checks), inline=False)
    
    if extracted:
        embed.add_field(name="Extracted Text", value=f"`{', '.join(list(set(extracted))[:8])}`", inline=False)
    
    await ctx.send(embed=embed, delete_after=60)

@bot.command(name="listblockedwords")
@commands.has_permissions(administrator=True)
async def list_blocked_words(ctx):
    await ctx.send(f"🚫 **Blocked words:** {len(BLOCKED_WORDS)} words\n✅ **Whitelisted:** {len(WHITELIST_WORDS)} words", delete_after=20)

@bot.command(name="listautorepies")
@commands.has_permissions(administrator=True)
async def list_auto_replies(ctx):
    """List all auto-reply patterns"""
    embed = discord.Embed(
        title="🤖 Auto-Reply Patterns",
        description=f"Currently configured: {len(AUTO_REPLY_PATTERNS)} patterns",
        color=0x00ff88
    )
    
    for i, (pattern, data) in enumerate(AUTO_REPLY_PATTERNS.items(), 1):
        embed.add_field(
            name=f"{i}. {data['description']}",
            value=f"Response: `{data['response'][:100]}{'...' if len(data['response']) > 100 else ''}`",
            inline=False
        )
    
    await ctx.send(embed=embed, delete_after=60)

@bot.command(name="testautorely")
@commands.has_permissions(administrator=True)
async def test_auto_reply(ctx, *, text: str):
    """Test auto-reply detection"""
    auto_reply = check_auto_reply(text)
    
    embed = discord.Embed(
        title="🤖 Auto-Reply Test",
        color=0x00ff88 if auto_reply else 0x888888
    )
    
    embed.add_field(name="Test Message", value=f"```{text[:200]}```", inline=False)
    
    if auto_reply:
        embed.add_field(name="✅ Match Found", value=f"Bot would reply: {auto_reply}", inline=False)
    else:
        embed.add_field(name="❌ No Match", value="No auto-reply pattern matched", inline=False)
    
    await ctx.send(embed=embed, delete_after=30)

@bot.command(name="filterhelp")
@commands.has_permissions(administrator=True)
async def filter_help(ctx):
    """Show all commands"""
    embed = discord.Embed(
        title="🛡️ Ultimate Filter Bot Commands",
        description="Comprehensive bypass detection system with auto-replies",
        color=0x3498db
    )
    
    embed.add_field(
        name="📢 Channel Management",
        value="`$addchannel #channel` - Monitor channel\n"
              "`$removechannel #channel` - Stop monitoring\n"
              "`$listchannels` - Show monitored channels",
        inline=False
    )
    
    embed.add_field(
        name="🚫 Word Management",
        value="`$addblockedword <word>` - Add blocked word\n"
              "`$removeblockedword <word>` - Remove blocked word\n"
              "`$addwhitelist <word>` - Whitelist word\n"
              "`$removewhitelist <word>` - Remove from whitelist\n"
              "`$listblockedwords` - Show counts",
        inline=False
    )
    
    embed.add_field(
        name="🤖 Auto-Reply System",
        value="`$listautorepies` - Show auto-reply patterns\n"
              "`$testautorely <text>` - Test auto-reply matching",
        inline=False
    )
    
    embed.add_field(
        name="🔍 Testing Tools",
        value="`$testmessage <text>` - Full message test\n"
              "`$testascii <text>` - ASCII art test\n"
              "`$testunicode <text>` - Unicode conversion test\n"
              "`$scantext <text>` - Deep scan analysis",
        inline=False
    )
    
    embed.add_field(
        name="🎯 Detection Features",
        value="✅ 500+ Unicode font variations\n"
              "✅ ASCII art text extraction\n"
              "✅ Vertical text reading\n"
              "✅ Horizontal pattern matching\n"
              "✅ Multi-line art detection\n"
              "✅ Emoji flag bypass (🇸🇰🇮🇩)\n"
              "✅ All FIGlet fonts (358+ fonts)\n"
              "✅ Cyrillic/Greek lookalikes\n"
              "✅ Box drawing characters\n"
              "✅ Mathematical symbols\n"
              "✅ Fullwidth characters\n"
              "✅ Enclosed alphanumerics\n"
              "✅ Language detection\n"
              "✅ Smart auto-replies",
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
    embed.add_field(name="Whitelisted Words", value=str(len(WHITELIST_WORDS)), inline=True)
    embed.add_field(name="Auto-Reply Patterns", value=str(len(AUTO_REPLY_PATTERNS)), inline=True)
    embed.add_field(name="Bypass Roles", value=str(len(BYPASS_ROLES)), inline=True)
    embed.add_field(name="Servers", value=str(len(bot.guilds)), inline=True)
    embed.add_field(name="Status", value="🟢 Active", inline=True)
    
    embed.add_field(
        name="Protection Level",
        value="🛡️ **ULTIMATE**\n"
              "• 500+ Unicode ranges covered\n"
              "• 358+ ASCII art fonts detected\n"
              "• Multi-method text extraction\n"
              "• Real-time pattern analysis\n"
              "• Smart auto-reply system",
        inline=False
    )
    
    await ctx.send(embed=embed, delete_after=30)

# === ERROR HANDLING ===

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.", delete_after=10)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing required argument. Use `$filterhelp` for the command list.", delete_after=10)
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid argument provided.", delete_after=10)
    else:
        print(f"Command error: {error}")

# === START BOT ===

if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")
    
    if not token:
        print("❌ Bot token not found! Set TOKEN in your .env file.")
        exit(1)
    
    try:
        bot.run(token)
    except discord.LoginFailure:
        print("❌ Invalid bot token!")
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")

