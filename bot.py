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

BYPASS_ROLES = [1453188702984601673, 1453188706541240330, 1453188775973884126]
LOG_CHANNEL_ID = 1453066942532554802

MONITORED_CHANNELS = [
    1453067297743704217,
    1453067980878512290
]

BLOCKED_MESSAGES = [
    "https://raw.githubusercontent.com/ayawtandogaakongotin/buangka",
    "🄷🅃🅃🄿🅂",
    "🅃🄴🄻🄴",
    "ayawtandogaakongotin",
    "jxbadscript",
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

# === COMPREHENSIVE UNICODE DETECTION ===

def comprehensive_unicode_to_ascii(text):
    """Convert ALL Unicode variations to ASCII - COMPLETE A-Z MATHEMATICAL SYMBOLS"""
    if not text:
        return ""
    
    result = list(text)
    
    for i, char in enumerate(result):
        code = ord(char)
        
        # === MATHEMATICAL ALPHANUMERIC SYMBOLS - ALL COMPLETE A-Z RANGES ===
        
        # Mathematical Bold (𝐀-𝐙, 𝐚-𝐳) - COMPLETE A-Z
        if 0x1D400 <= code <= 0x1D419:  # 𝐀-𝐙
            result[i] = chr(ord('A') + (code - 0x1D400))
        elif 0x1D41A <= code <= 0x1D433:  # 𝐚-𝐳
            result[i] = chr(ord('a') + (code - 0x1D41A))
        
        # Mathematical Italic (𝐴-𝑍, 𝑎-𝑧) - COMPLETE A-Z
        elif 0x1D434 <= code <= 0x1D44D:  # 𝐴-�Z
            result[i] = chr(ord('A') + (code - 0x1D434))
        elif 0x1D44E <= code <= 0x1D467:  # 𝑎-𝑧
            result[i] = chr(ord('a') + (code - 0x1D44E))
        
        # Mathematical Bold Italic (𝑨-𝒁, 𝒂-𝒛) - COMPLETE A-Z
        elif 0x1D468 <= code <= 0x1D481:  # 𝑨-𝒁
            result[i] = chr(ord('A') + (code - 0x1D468))
        elif 0x1D482 <= code <= 0x1D49B:  # 𝒂-𝒛
            result[i] = chr(ord('a') + (code - 0x1D482))
        
        # Mathematical Script (𝒜-𝒵, 𝒶-𝓏) - COMPLETE A-Z
        elif 0x1D49C <= code <= 0x1D4B5:  # 𝒜-𝒵
            result[i] = chr(ord('A') + (code - 0x1D49C))
        elif 0x1D4B6 <= code <= 0x1D4CF:  # 𝒶-𝓏
            result[i] = chr(ord('a') + (code - 0x1D4B6))
        
        # Mathematical Bold Script (𝓐-𝓩, 𝓪-𝔃) - COMPLETE A-Z
        elif 0x1D4D0 <= code <= 0x1D4E9:  # 𝓐-𝓩
            result[i] = chr(ord('A') + (code - 0x1D4D0))
        elif 0x1D4EA <= code <= 0x1D503:  # 𝓪-𝔃
            result[i] = chr(ord('a') + (code - 0x1D4EA))
        
        # Mathematical Fraktur (𝔄-𝔜, 𝔞-𝔷) - COMPLETE A-Z
        elif 0x1D504 <= code <= 0x1D51D:  # 𝔄-𝔜
            result[i] = chr(ord('A') + (code - 0x1D504))
        elif 0x1D51E <= code <= 0x1D537:  # 𝔞-𝔷
            result[i] = chr(ord('a') + (code - 0x1D51E))
        
        # Mathematical Double-Struck (𝔸-ℤ, 𝕒-𝕫) - COMPLETE A-Z
        elif 0x1D538 <= code <= 0x1D551:  # 𝔸-ℤ (THIS IS THE STYLE YOU MENTIONED!)
            result[i] = chr(ord('A') + (code - 0x1D538))
        elif 0x1D552 <= code <= 0x1D56B:  # 𝕒-𝕫
            result[i] = chr(ord('a') + (code - 0x1D552))
        
        # Mathematical Bold Fraktur (𝕬-𝖅, 𝖆-𝖟) - COMPLETE A-Z
        elif 0x1D56C <= code <= 0x1D585:  # 𝕬-𝖅
            result[i] = chr(ord('A') + (code - 0x1D56C))
        elif 0x1D586 <= code <= 0x1D59F:  # 𝖆-𝖟
            result[i] = chr(ord('a') + (code - 0x1D586))
        
        # Mathematical Sans-Serif (𝖠-𝖹, 𝖺-𝗓) - COMPLETE A-Z
        elif 0x1D5A0 <= code <= 0x1D5B9:  # 𝖠-𝖹
            result[i] = chr(ord('A') + (code - 0x1D5A0))
        elif 0x1D5BA <= code <= 0x1D5D3:  # 𝖺-𝗓
            result[i] = chr(ord('a') + (code - 0x1D5BA))
        
        # Mathematical Sans-Serif Bold (𝗔-𝗭, 𝗮-𝘇) - COMPLETE A-Z
        elif 0x1D5D4 <= code <= 0x1D5ED:  # 𝗔-𝗭
            result[i] = chr(ord('A') + (code - 0x1D5D4))
        elif 0x1D5EE <= code <= 0x1D607:  # 𝗮-𝘇
            result[i] = chr(ord('a') + (code - 0x1D5EE))
        
        # Mathematical Sans-Serif Italic (𝘈-𝘡, 𝘢-𝘻) - COMPLETE A-Z
        elif 0x1D608 <= code <= 0x1D621:  # 𝘈-𝘡
            result[i] = chr(ord('A') + (code - 0x1D608))
        elif 0x1D622 <= code <= 0x1D63B:  # 𝘢-𝘻
            result[i] = chr(ord('a') + (code - 0x1D622))
        
        # Mathematical Sans-Serif Bold Italic (𝘼-𝙕, 𝙖-𝙯) - COMPLETE A-Z
        elif 0x1D63C <= code <= 0x1D655:  # 𝘼-𝙕
            result[i] = chr(ord('A') + (code - 0x1D63C))
        elif 0x1D656 <= code <= 0x1D66F:  # 𝙖-𝙯
            result[i] = chr(ord('a') + (code - 0x1D656))
        
        # Mathematical Monospace (𝙰-𝚉, 𝚊-𝚣) - COMPLETE A-Z
        elif 0x1D670 <= code <= 0x1D689:  # 𝙰-𝚉
            result[i] = chr(ord('A') + (code - 0x1D670))
        elif 0x1D68A <= code <= 0x1D6A3:  # 𝚊-𝚣
            result[i] = chr(ord('a') + (code - 0x1D68A))
        
        # === ALL FLAG EMOJIS DETECTION ===
        # Regional Indicator Symbols (🇦-🇿) - ALL FLAGS
        elif 0x1F1E6 <= code <= 0x1F1FF:  # 🇦-🇿 (ALL COUNTRY FLAGS)
            result[i] = chr(ord('A') + (code - 0x1F1E6))
        
        # Mathematical digits - ALL VARIANTS
        elif 0x1D7CE <= code <= 0x1D7D7:  # Bold 𝟎-𝟗
            result[i] = chr(ord('0') + (code - 0x1D7CE))
        elif 0x1D7D8 <= code <= 0x1D7E1:  # Double-struck 𝟘-𝟡
            result[i] = chr(ord('0') + (code - 0x1D7D8))
        elif 0x1D7E2 <= code <= 0x1D7EB:  # Sans-serif 𝟢-𝟫
            result[i] = chr(ord('0') + (code - 0x1D7E2))
        elif 0x1D7EC <= code <= 0x1D7F5:  # Sans-serif bold 𝟬-𝟵
            result[i] = chr(ord('0') + (code - 0x1D7EC))
        elif 0x1D7F6 <= code <= 0x1D7FF:  # Monospace 𝟶-𝟿
            result[i] = chr(ord('0') + (code - 0x1D7F6))
        
        # Fullwidth forms (Ａ-Ｚ, ａ-ｚ, ０-９)
        elif 0xFF21 <= code <= 0xFF3A:  # Ａ-Ｚ
            result[i] = chr(ord('A') + (code - 0xFF21))
        elif 0xFF41 <= code <= 0xFF5A:  # ａ-ｚ
            result[i] = chr(ord('a') + (code - 0xFF41))
        elif 0xFF10 <= code <= 0xFF19:  # ０-９
            result[i] = chr(ord('0') + (code - 0xFF10))
        
        # Enclosed Alphanumerics (Ⓐ-Ⓩ, ⓐ-ⓩ)
        elif 0x24B6 <= code <= 0x24CF:  # Ⓐ-Ⓩ
            result[i] = chr(ord('A') + (code - 0x24B6))
        elif 0x24D0 <= code <= 0x24E9:  # ⓐ-ⓩ
            result[i] = chr(ord('a') + (code - 0x24D0))
        
        # Squared Latin Letters (🄰-🅉, 🅰-🆉)
        elif 0x1F130 <= code <= 0x1F149:  # 🄰-🅉
            result[i] = chr(ord('A') + (code - 0x1F130))
        elif 0x1F170 <= code <= 0x1F189:  # 🅰-🆉
            result[i] = chr(ord('A') + (code - 0x1F170))
        
        # Box Drawing and Block Elements - convert to space
        elif 0x2500 <= code <= 0x257F or 0x2580 <= code <= 0x259F:
            result[i] = ' '
        
        # Cyrillic look-alikes - EXPANDED
        elif char in 'АВСЕНІКМОРТУХЅаевсікморстухѕ':
            cyrillic_map = {
                'А':'A','В':'B','С':'C','Е':'E','Н':'H','І':'I','К':'K','М':'M',
                'О':'O','Р':'P','Т':'T','У':'Y','Х':'X','Ѕ':'S',
                'а':'a','е':'e','в':'b','с':'c','і':'i','к':'k','м':'m',
                'о':'o','р':'p','т':'t','у':'u','х':'x','ѕ':'s'
            }
            result[i] = cyrillic_map.get(char, char)
        
        # Greek look-alikes - EXPANDED
        elif char in 'ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδεζηθικλμνξοπρστυφχψω':
            greek_map = {
                'Α':'A','Β':'B','Γ':'G','Δ':'D','Ε':'E','Ζ':'Z','Η':'H','Θ':'T',
                'Ι':'I','Κ':'K','Λ':'L','Μ':'M','Ν':'N','Ξ':'X','Ο':'O','Π':'P',
                'Ρ':'P','Σ':'S','Τ':'T','Υ':'Y','Φ':'F','Χ':'X','Ψ':'P','Ω':'O',
                'α':'a','β':'b','γ':'g','δ':'d','ε':'e','ζ':'z','η':'h','θ':'t',
                'ι':'i','κ':'k','λ':'l','μ':'m','ν':'n','ξ':'x','ο':'o','π':'p',
                'ρ':'r','σ':'s','τ':'t','υ':'u','φ':'f','χ':'x','ψ':'p','ω':'o'
            }
            result[i] = greek_map.get(char, char)
        
        # Additional Unicode ranges for symbols and special characters
        elif 0x2100 <= code <= 0x214F:  # Letterlike Symbols
            letterlike_map = {
                '℀':'a/c', '℁':'a/s', 'ℂ':'C', '℃':'C', '℄':'CL', '℅':'c/o', '℆':'c/u',
                'ℇ':'E', '℈':'g', '℉':'F', 'ℊ':'g', 'ℋ':'H', 'ℌ':'H', 'ℍ':'H',
                'ℎ':'h', 'ℏ':'h', 'ℐ':'I', 'ℑ':'I', 'ℒ':'L', 'ℓ':'l', '℔':'lb',
                'ℕ':'N', '№':'No', '℗':'P', '℘':'P', 'ℙ':'P', 'ℚ':'Q', 'ℛ':'R',
                'ℜ':'R', 'ℝ':'R', '℞':'Rx', '℟':'R', '℠':'SM', '℡':'TEL', '™':'TM',
                '℣':'V', 'ℤ':'Z', '℥':'oz', 'Ω':'O', '℧':'O', 'ℨ':'Z', '℩':'i',
                'K':'K', 'Å':'A', 'ℬ':'B', 'ℭ':'C', 'ℯ':'e', 'ℰ':'E', 'ℱ':'F',
                'Ⅎ':'F', 'ℳ':'M', 'ℴ':'o', 'ℵ':'N', 'ℶ':'B', 'ℷ':'G', 'ℸ':'P',
                'ℹ':'i', '℺':'Q', '℻':'FAX', 'ℼ':'P', 'ℽ':'G', 'ℾ':'P', 'ℿ':'S',
                '⅀':'S', '⅁':'G', '⅂':'L', '⅃':'L', '⅄':'Y', 'ⅅ':'D', 'ⅆ':'d',
                'ⅇ':'e', 'ⅈ':'i', 'ⅉ':'j'
            }
            result[i] = letterlike_map.get(char, char)
        
        # Roman Numerals - ALL
        elif 0x2160 <= code <= 0x217F:
            roman_map = {
                'Ⅰ':'I', 'Ⅱ':'II', 'Ⅲ':'III', 'Ⅳ':'IV', 'Ⅴ':'V', 'Ⅵ':'VI',
                'Ⅶ':'VII', 'Ⅷ':'VIII', 'Ⅸ':'IX', 'Ⅹ':'X', 'Ⅺ':'XI', 'Ⅻ':'XII',
                'Ⅼ':'L', 'Ⅽ':'C', 'Ⅾ':'D', 'Ⅿ':'M',
                'ⅰ':'i', 'ⅱ':'ii', 'ⅲ':'iii', 'ⅳ':'iv', 'ⅴ':'v', 'ⅵ':'vi',
                'ⅶ':'vii', 'ⅷ':'viii', 'ⅸ':'ix', 'ⅹ':'x', 'ⅺ':'xi', 'ⅻ':'xii',
                'ⅼ':'l', 'ⅽ':'c', 'ⅾ':'d', 'ⅿ':'m'
            }
            result[i] = roman_map.get(char, char)
        
        # Superscript and Subscript - ALL
        elif char in '⁰¹²³⁴⁵⁶⁷⁸⁹':
            super_map = {'⁰':'0','¹':'1','²':'2','³':'3','⁴':'4','⁵':'5','⁶':'6','⁷':'7','⁸':'8','⁹':'9'}
            result[i] = super_map.get(char, char)
        elif char in '₀₁₂₃₄₅₆₇₈₉':
            sub_map = {'₀':'0','₁':'1','₂':'2','₃':'3','₄':'4','₅':'5','₆':'6','₇':'7','₈':'8','₉':'9'}
            result[i] = sub_map.get(char, char)
        elif char in 'ᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖʳˢᵗᵘᵛʷˣʸᶻᴬᴮᴰᴱᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾᴿᵀᵁⱽᵂ':
            super_alpha_map = {
                'ᵃ':'a','ᵇ':'b','ᶜ':'c','ᵈ':'d','ᵉ':'e','ᶠ':'f','ᵍ':'g','ʰ':'h','ⁱ':'i','ʲ':'j',
                'ᵏ':'k','ˡ':'l','ᵐ':'m','ⁿ':'n','ᵒ':'o','ᵖ':'p','ʳ':'r','ˢ':'s','ᵗ':'t','ᵘ':'u',
                'ᵛ':'v','ʷ':'w','ˣ':'x','ʸ':'y','ᶻ':'z','ᴬ':'A','ᴮ':'B','ᴰ':'D','ᴱ':'E',
                'ᴳ':'G','ᴴ':'H','ᴵ':'I','ᴶ':'J','ᴷ':'K','ᴸ':'L','ᴹ':'M','ᴺ':'N','ᴼ':'O',
                'ᴾ':'P','ᴿ':'R','ᵀ':'T','ᵁ':'U','ⱽ':'V','ᵂ':'W'
            }
            result[i] = super_alpha_map.get(char, char)
        elif char in 'ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ':
            sub_alpha_map = {
                'ₐ':'a','ₑ':'e','ₕ':'h','ᵢ':'i','ⱼ':'j','ₖ':'k','ₗ':'l','ₘ':'m','ₙ':'n',
                'ₒ':'o','ₚ':'p','ᵣ':'r','ₛ':'s','ₜ':'t','ᵤ':'u','ᵥ':'v','ₓ':'x'
            }
            result[i] = sub_alpha_map.get(char, char)
    
    return ''.join(result)

def detect_flag_emojis(text):
    """Detect ALL flag emoji patterns"""
    if not text:
        return False, []
    
    violations = []
    
    # Check for regional indicator symbols (flag emojis)
    flag_pattern = re.compile(r'[\U0001F1E6-\U0001F1FF]')
    flag_matches = flag_pattern.findall(text)
    
    if len(flag_matches) >= 2:  # Any flag combination
        # Convert flag emojis to letters
        flag_letters = []
        for flag_char in flag_matches:
            letter = chr(ord('A') + (ord(flag_char) - 0x1F1E6))
            flag_letters.append(letter)
        
        flag_sequence = ''.join(flag_letters)
        violations.append(f"Flag emoji pattern detected: {flag_sequence}")
    
    # Also check for single flag usage if it's excessive
    if len(flag_matches) >= 3:  # 3 or more flag emojis
        violations.append("Excessive flag emoji usage detected")
    
    return len(violations) > 0, violations

def advanced_ascii_art_extraction(text):
    """Enhanced ASCII art extraction with multiple detection methods"""
    if not text or len(text) < 5:
        return []
    
    extracted_sequences = []
    lines = text.split('\n')
    
    # Method 1: Vertical reading (column-by-column) - ENHANCED
    if len(lines) >= 2:
        max_length = max(len(line) for line in lines) if lines else 0
        for col in range(min(200, max_length)):  # Increased range
            vertical_chars = []
            for line in lines:
                if col < len(line):
                    char = line[col]
                    # Convert Unicode to ASCII first
                    converted_char = comprehensive_unicode_to_ascii(char)
                    if converted_char.isalpha():
                        vertical_chars.append(converted_char.lower())
            if len(vertical_chars) >= 2:  # Lowered threshold
                vertical_word = ''.join(vertical_chars)
                if len(vertical_word) >= 2:
                    extracted_sequences.append(vertical_word)
    
    # Method 2: Diagonal reading
    for start_row in range(len(lines)):
        for start_col in range(len(lines[start_row]) if start_row < len(lines) else 0):
            # Diagonal down-right
            diagonal_chars = []
            row, col = start_row, start_col
            while row < len(lines) and col < len(lines[row]):
                char = lines[row][col]
                converted_char = comprehensive_unicode_to_ascii(char)
                if converted_char.isalpha():
                    diagonal_chars.append(converted_char.lower())
                row += 1
                col += 1
            if len(diagonal_chars) >= 3:
                diagonal_word = ''.join(diagonal_chars)
                extracted_sequences.append(diagonal_word)
            
            # Diagonal down-left
            diagonal_chars = []
            row, col = start_row, start_col
            while row < len(lines) and col >= 0 and col < len(lines[row]):
                char = lines[row][col]
                converted_char = comprehensive_unicode_to_ascii(char)
                if converted_char.isalpha():
                    diagonal_chars.append(converted_char.lower())
                row += 1
                col -= 1
            if len(diagonal_chars) >= 3:
                diagonal_word = ''.join(diagonal_chars)
                extracted_sequences.append(diagonal_word)
    
    # Method 3: Horizontal reading with enhanced cleaning
    for line in lines:
        # Convert Unicode first
        converted_line = comprehensive_unicode_to_ascii(line)
        # Remove ASCII art characters but keep letters
        cleaned = re.sub(r'[|/\\()[\]{}#@*=_\-+<>~^`.:;\'"!?$%&0-9]', ' ', converted_line)
        words = cleaned.split()
        for word in words:
            if len(word) >= 2 and word.isalpha():  # Lowered threshold
                extracted_sequences.append(word.lower())
    
    # Method 4: Pattern-based extraction (looking for repeated structures)
    full_text = ' '.join(lines)
    converted_full = comprehensive_unicode_to_ascii(full_text)
    
    # Extract sequences of letters separated by non-letters
    letter_sequences = re.findall(r'[a-zA-Z]{2,}', converted_full)
    for seq in letter_sequences:
        extracted_sequences.append(seq.lower())
    
    # Method 5: Dense character block detection with Unicode conversion
    letters_only = re.sub(r'[^a-zA-Z]', '', converted_full).lower()
    if letters_only:
        # Extract overlapping substrings
        for i in range(len(letters_only) - 1):
            for length in range(2, min(15, len(letters_only) - i + 1)):
                chunk = letters_only[i:i+length]
                if len(chunk) >= 2:
                    extracted_sequences.append(chunk)
    
    # Method 6: Reverse reading
    for line in lines:
        converted_line = comprehensive_unicode_to_ascii(line)
        reversed_line = converted_line[::-1]
        cleaned = re.sub(r'[^a-zA-Z]', '', reversed_line).lower()
        if len(cleaned) >= 2:
            extracted_sequences.append(cleaned)
    
    return list(set(extracted_sequences))  # Remove duplicates

def detect_multi_line_art(text):
    """Enhanced multi-line ASCII art detection"""
    if not text or len(text) < 10:
        return False
    
    lines = text.split('\n')
    
    # Check for multiple lines
    if len(lines) > 4:
        return True
    
    # Check for consistent structure
    if len(lines) >= 2:
        lengths = [len(line) for line in lines if line.strip()]
        if lengths:
            avg_length = sum(lengths) / len(lengths)
            # Lower threshold for detection
            if avg_length > 15 and len([l for l in lengths if abs(l - avg_length) < 15]) >= 2:
                return True
    
    # Check for high density of special characters or Unicode
    for line in lines:
        if len(line) > 10:
            # Count special ASCII art characters
            special_count = sum(1 for c in line if c in '|/\\()[]{}#@*=_-+<>~^`.:;')
            # Count Unicode characters that could be used for art
            unicode_count = sum(1 for c in line if ord(c) > 127)
            
            total_special = special_count + unicode_count
            if total_special > len(line) * 0.2:  # Lowered threshold
                return True
    
    # Check for mathematical Unicode characters (common in bypasses)
    unicode_math_pattern = re.compile(r'[\U0001D400-\U0001D7FF]')  # Mathematical Alphanumeric Symbols
    if unicode_math_pattern.search(text):
        return True
    
    # Check for flag emojis or regional indicators
    flag_pattern = re.compile(r'[\U0001F1E6-\U0001F1FF]')
    if flag_pattern.search(text):
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
    """Ultimate blocked word detection with enhanced Unicode handling"""
    if not text:
        return False, []
    
    violations = []
    
    # Convert Unicode to ASCII first
    converted = comprehensive_unicode_to_ascii(text)
    
    # Normalize text (remove special characters, keep letters and spaces)
    normalized = re.sub(r'[^a-z0-9\s]', '', converted.lower())
    words = normalized.split()
    
    # Check individual words
    for word in words:
        if len(word) < 2 or is_whitelisted_word(word):
            continue
        
        for blocked in BLOCKED_WORDS:
            blocked_clean = re.sub(r'[^a-z]', '', blocked.lower())
            if len(blocked_clean) >= 2:
                # Exact match
                if word == blocked_clean:
                    violations.append(f"Blocked word: '{blocked}'")
                # Partial match with obfuscation
                elif blocked_clean in word and len(word) <= len(blocked_clean) + 4:  # Allow slight variations
                    if not is_whitelisted_word(word):
                        violations.append(f"Blocked word (obfuscated): '{blocked}' in '{word}'")
    
    # Check full text for hidden words
    full_letters = re.sub(r'[^a-z]', '', converted.lower())
    for blocked in BLOCKED_WORDS:
        blocked_clean = re.sub(r'[^a-z]', '', blocked.lower())
        if len(blocked_clean) >= 2 and blocked_clean in full_letters:
            # Check if it's not part of a whitelisted word
            is_in_whitelist = False
            for word in words:
                if is_whitelisted_word(word) and blocked_clean in word.lower():
                    is_in_whitelist = True
                    break
            
            if not is_in_whitelist:
                violations.append(f"Blocked word (hidden): '{blocked}'")
    
    # Enhanced ASCII art extraction
    if '\n' in text or len(text) > 30:  # Lowered threshold
        extracted_words = advanced_ascii_art_extraction(text)
        for extracted in extracted_words:
            if len(extracted) < 2:
                continue
            for blocked in BLOCKED_WORDS:
                blocked_clean = re.sub(r'[^a-z]', '', blocked.lower())
                if len(blocked_clean) >= 2:
                    if blocked_clean in extracted and not is_whitelisted_word(extracted):
                        violations.append(f"Blocked word (ASCII art): '{blocked}' detected in art pattern")
    
    # Check for leetspeak and number substitutions
    leetspeak_map = {'3': 'e', '1': 'i', '0': 'o', '4': 'a', '5': 's', '7': 't', '8': 'b'}
    leet_converted = converted.lower()
    for num, letter in leetspeak_map.items():
        leet_converted = leet_converted.replace(num, letter)
    
    leet_normalized = re.sub(r'[^a-z]', '', leet_converted)
    for blocked in BLOCKED_WORDS:
        blocked_clean = re.sub(r'[^a-z]', '', blocked.lower())
        if len(blocked_clean) >= 2 and blocked_clean in leet_normalized:
            violations.append(f"Blocked word (leetspeak): '{blocked}' detected")
    
    return len(violations) > 0, list(set(violations))

def detect_non_english(text):
    """STRICT non-English language detection - ONLY ENGLISH ALLOWED"""
    if not text or len(text.strip()) < 2:
        return False
    
    # Clean the text - remove URLs, mentions, channels, emojis
    cleaned_text = re.sub(r'http[s]?://\S+', '', text)
    cleaned_text = re.sub(r'<@[!&]?\d+>', '', cleaned_text)
    cleaned_text = re.sub(r'<#\d+>', '', cleaned_text)
    cleaned_text = re.sub(r'<:\w+:\d+>', '', cleaned_text)
    
    # Remove emojis
    try:
        cleaned_text = emoji.demojize(cleaned_text)
        cleaned_text = re.sub(r':[a-z_]+:', '', cleaned_text)
    except:
        pass
    
    # Convert Unicode to ASCII first to handle fancy fonts
    cleaned_text = comprehensive_unicode_to_ascii(cleaned_text)
    
    # Remove numbers, punctuation, and special characters - keep only letters and spaces
    text_only = re.sub(r'[^a-zA-Z\s]', '', cleaned_text)
    text_only = text_only.strip()
    
    # If no letters remain after cleaning, allow it (could be just numbers/symbols)
    if len(text_only) < 2:
        return False
    
    # Check for non-English characters that survived the Unicode conversion
    # Chinese/Japanese/Korean characters
    if re.search(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]', text):
        return True
    
    # Arabic/Hebrew characters
    if re.search(r'[\u0600-\u06ff\u0590-\u05ff]', text):
        return True
    
    # Cyrillic characters (that weren't converted)
    if re.search(r'[\u0400-\u04ff]', text):
        return True
    
    # Thai, Hindi, and other Asian scripts
    if re.search(r'[\u0e00-\u0e7f\u0900-\u097f\u1000-\u109f]', text):
        return True
    
    # Check if the text contains mostly English letters
    total_chars = len(text_only.replace(' ', ''))
    if total_chars == 0:
        return False
    
    english_chars = len(re.findall(r'[a-zA-Z]', text_only))
    english_ratio = english_chars / total_chars
    
    # STRICT: If less than 90% English characters, consider it non-English
    if english_ratio < 0.9:
        return True
    
    # Additional check: Look for common non-English patterns
    # Check for sequences that look like other languages
    words = text_only.lower().split()
    suspicious_patterns = [
        # Common Chinese pinyin patterns
        r'^[bcdfghjklmnpqrstvwxyz]{3,}$',  # Too many consonants
        # Common patterns in other languages
        r'[qxz]{2,}',  # Repeated uncommon letters
        r'^[aeiou]{4,}$',  # Too many vowels in sequence
    ]
    
    for word in words:
        if len(word) > 2:
            for pattern in suspicious_patterns:
                if re.search(pattern, word):
                    # Only flag if it's a longer word and doesn't look like English
                    if len(word) > 4 and not any(common in word for common in ['the', 'and', 'you', 'that', 'was', 'for', 'are', 'with', 'his', 'they']):
                        return True
    
    return False

def analyze_message_content(content):
    """Enhanced message analysis with all detection methods"""
    if not content or len(content) < 1:
        return False, []
    
    violations = []
    
    # Check for multi-line ASCII art
    if detect_multi_line_art(content):
        violations.append("Multi-line ASCII art detected (likely bypass attempt)")
    
    # Check for ALL flag emojis
    has_flags, flag_violations = detect_flag_emojis(content)
    violations.extend(flag_violations)
    
    # Check for blocked words with enhanced detection
    has_blocked, blocked_violations = check_blocked_words_ultimate(content)
    violations.extend(blocked_violations)
    
    # Check for blocked messages
    converted = comprehensive_unicode_to_ascii(content).lower()
    for blocked_msg in BLOCKED_MESSAGES:
        if blocked_msg.lower() in converted:
            violations.append(f"Blocked content: '{blocked_msg}'")
    
    # Check for excessive formatting (potential bypass)
    markdown_chars = content.count('*') + content.count('_') + content.count('~') + content.count('|') + content.count('`')
    if len(content) > 5 and markdown_chars > len(content) * 0.4:  # Lowered threshold
        violations.append("Excessive formatting (possible bypass)")
    
    # Check for suspicious Unicode patterns - COMPLETE MATHEMATICAL SYMBOLS
    unicode_math_count = len(re.findall(r'[\U0001D400-\U0001D7FF]', content))
    if unicode_math_count > 2:
        violations.append("Mathematical Unicode symbols detected (bypass attempt)")
    
    # Check for mixed scripts (potential obfuscation)
    scripts = []
    if re.search(r'[a-zA-Z]', content): scripts.append('latin')
    if re.search(r'[\u0400-\u04FF]', content): scripts.append('cyrillic')
    if re.search(r'[\u0370-\u03FF]', content): scripts.append('greek')
    if re.search(r'[\U0001D400-\U0001D7FF]', content): scripts.append('math')
    if re.search(r'[\U0001F1E6-\U0001F1FF]', content): scripts.append('flags')
    
    if len(scripts) > 2:
        violations.append("Mixed scripts detected (potential obfuscation)")
    
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
    """Enhanced message processing - NO SPAM DETECTION"""
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
    
    # Check STRICT non-English - ONLY ENGLISH ALLOWED
    if detect_non_english(message.content):
        try:
            await message.delete()
        except discord.Forbidden:
            pass
        
        # Log non-English detection
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="🌐 Non-English Message Blocked",
                description=f"**User:** {guild_member.mention}\n**Channel:** {message.channel.mention}",
                color=0x3498db,
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            embed.add_field(name="Reason", value="Only English is allowed in this server", inline=False)
            embed.add_field(name="Original Message", value=f"```\n{message.content[:300]}\n```", inline=False)
            
            # Show Unicode conversion
            converted = comprehensive_unicode_to_ascii(message.content)
            if converted != message.content:
                embed.add_field(name="Unicode → ASCII", value=f"```\n{converted[:200]}\n```", inline=False)
            
            try:
                await log_channel.send(embed=embed)
            except:
                pass
        
        try:
            embed = discord.Embed(
                title="🌐 Language Notice",
                description="Please speak English only. All other languages are not allowed.",
                color=0x3498db
            )
            await message.channel.send(embed=embed, delete_after=10)
        except:
            pass
        return
    
    # Analyze content for violations
    is_violation, violation_reasons = analyze_message_content(message.content)
    
    if is_violation:
        try:
            await message.delete()
        except discord.Forbidden:
            pass
        
        # Log violation
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            violation_text = '\n'.join(f"• {reason}" for reason in violation_reasons[:8])  # Show more violations
            
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
            
            # Show Unicode conversion
            converted = comprehensive_unicode_to_ascii(message.content)
            if converted != message.content and len(converted) < 400:
                embed.add_field(name="Unicode → ASCII", value=f"```\n{converted[:300]}\n```", inline=False)
            
            # Show ASCII art extraction if detected
            if detect_multi_line_art(message.content):
                extracted = advanced_ascii_art_extraction(message.content)
                if extracted:
                    extracted_preview = ', '.join(extracted[:15])  # Show more extractions
                    if len(extracted_preview) > 200:
                        extracted_preview = extracted_preview[:197] + "..."
                    embed.add_field(name="Extracted from Art", value=f"`{extracted_preview}`", inline=False)
            
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
                value="• Use appropriate language\n• No unauthorized links\n• No filter bypass attempts\n• No ASCII art to hide words\n• English only - no other languages\n• Keep messages respectful",
                inline=False
            )
            await guild_member.send(embed=embed)
        except:
            pass
        
        return
    
    await bot.process_commands(message)

# === ENHANCED CHANNEL SCANNER ===

@tasks.loop(count=1)
async def scan_channels_on_startup():
    """Enhanced channel scan with better detection"""
    await bot.wait_until_ready()
    print("🔍 Starting COMPLETE channel scan for existing messages...")
    
    deleted_count = 0
    scanned_count = 0
    
    for channel_id in MONITORED_CHANNELS:
        try:
            channel = bot.get_channel(channel_id)
            if not channel:
                continue
            
            print(f"   Scanning #{channel.name}...")
            
            async for message in channel.history(limit=200):  # Increased scan limit
                scanned_count += 1
                if message.author.bot:
                    continue
                
                guild_member = message.guild.get_member(message.author.id)
                if not guild_member:
                    continue
                
                if any(role.id in BYPASS_ROLES for role in guild_member.roles):
                    continue
                
                # Check violations with enhanced detection
                is_violation, violation_reasons = analyze_message_content(message.content)
                is_non_english = detect_non_english(message.content)
                
                if is_violation or is_non_english:
                    try:
                        await message.delete()
                        deleted_count += 1
                        print(f"   ✓ Deleted message from {message.author.name}: {violation_reasons[:2] if is_violation else ['Non-English']}")
                        await asyncio.sleep(0.5)  # Rate limit protection
                    except:
                        pass
        except Exception as e:
            print(f"Error scanning channel {channel_id}: {e}")
    
    print(f"✅ COMPLETE scan finished! Scanned {scanned_count} messages, deleted {deleted_count} violations.")

# === HEALTH CHECK SERVER ===

async def health_check_server():
    """Enhanced health check server for Render"""
    async def health(request):
        return web.Response(text="✅ COMPLETE Discord Filter Bot is running!\n🛡️ ALL Mathematical Unicode A-Z Detection Active\n🚨 ALL Flag Emoji Detection Active\n🌐 STRICT English-Only Language Detection\n❌ Spam Detection REMOVED")
    
    async def stats(request):
        stats_text = f"""📊 COMPLETE Bot Statistics:
Monitored Channels: {len(MONITORED_CHANNELS)}
Blocked Words: {len(BLOCKED_WORDS)}
Auto-Reply Patterns: {len(AUTO_REPLY_PATTERNS)}
Servers: {len(bot.guilds) if bot.guilds else 0}
Status: 🟢 COMPLETE Active
Features: ALL A-Z Mathematical Unicode + ALL Flag Emojis + STRICT English-Only
Spam Detection: ❌ REMOVED"""
        return web.Response(text=stats_text)
    
    app = web.Application()
    app.router.add_get('/', health)
    app.router.add_get('/health', health)
    app.router.add_get('/stats', stats)
    
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv('PORT', 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 COMPLETE health server running on port {port}")

# === EVENTS ===

@bot.event
async def on_ready():
    print(f'✅ {bot.user} is online with COMPLETE detection!')
    print(f'📢 Monitoring channels: {MONITORED_CHANNELS}')
    print(f'🛡️ COMPLETE ASCII art detection: ENABLED')
    print(f'❌ Spam detection: REMOVED')
    print(f'🌐 STRICT English-only detection: ENABLED')
    print(f'🔍 Scanning for: {len(BLOCKED_WORDS)} blocked words')
    print(f'🤖 Auto-reply patterns: {len(AUTO_REPLY_PATTERNS)} active')
    print(f'🌍 COMPLETE Unicode support: ALL A-Z Mathematical symbols')
    print(f'🎯 ALL Flag emoji detection: ENABLED (🇦-🇿)')
    print(f'🔤 Mathematical symbols detection: ALL VARIANTS A-Z')
    print(f'📝 Example detection: 𝔸ℕ𝕋𝕀 𝕂𝔽ℂ 𝔻𝕆𝔾 → ANTI KFC DOG')
    print(f'🚫 Chinese/Non-English: STRICT BLOCKING')
    
    # Start health server
    bot.loop.create_task(health_check_server())
    
    # Start enhanced channel scanner
    scan_channels_on_startup.start()

@bot.event
async def on_message(message):
    await process_message(message, is_edit=False)

@bot.event
async def on_message_edit(before, after):
    await process_message(after, is_edit=True)

# === ENHANCED ADMIN COMMANDS ===

@bot.command(name="addchannel")
@commands.has_permissions(administrator=True)
async def add_channel(ctx, channel: discord.TextChannel):
    if channel.id in MONITORED_CHANNELS:
        await ctx.send(f"⚠️ {channel.mention} already monitored.", delete_after=10)
    else:
        MONITORED_CHANNELS.append(channel.id)
        await ctx.send(f"✅ Now monitoring {channel.mention} with COMPLETE detection", delete_after=10)

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
        await ctx.send(f"📢 **COMPLETE Monitored Channels:**\n" + "\n".join(channels), delete_after=30)
    else:
        await ctx.send("⚠️ No channels monitored.", delete_after=10)

@bot.command(name="rescan")
@commands.has_permissions(administrator=True)
async def rescan_channels(ctx):
    """Manually trigger a COMPLETE channel rescan"""
    await ctx.send("🔍 Starting COMPLETE channel rescan...", delete_after=5)
    
    deleted_count = 0
    scanned_count = 0
    
    for channel_id in MONITORED_CHANNELS:
        try:
            channel = bot.get_channel(channel_id)
            if not channel:
                continue
            
            async for message in channel.history(limit=200):
                scanned_count += 1
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
                        await asyncio.sleep(0.5)
                    except:
                        pass
        except:
            pass
    
    await ctx.send(f"✅ COMPLETE rescan finished! Scanned {scanned_count} messages, deleted {deleted_count}.", delete_after=15)

@bot.command(name="testmessage")
@commands.has_permissions(administrator=True)
async def test_message(ctx, *, text: str):
    """Test message with COMPLETE detection"""
    is_violation, violations = analyze_message_content(text)
    has_flags, flag_violations = detect_flag_emojis(text)
    is_non_english = detect_non_english(text)
    
    embed = discord.Embed(
        title="🔍 COMPLETE Scanner Test",
        color=0xff4444 if (is_violation or has_flags or is_non_english) else 0x44ff44
    )
    
    if is_violation or has_flags or is_non_english:
        embed.add_field(name="🚫 BLOCKED", value="Message would be deleted", inline=False)
        all_violations = violations + flag_violations
        if is_non_english:
            all_violations.append("Non-English language detected")
        embed.add_field(name="Violations", value='\n'.join(f"• {v}" for v in all_violations[:8]), inline=False)
    else:
        embed.add_field(name="✅ ALLOWED", value="Message would pass all COMPLETE checks", inline=False)
    
    embed.add_field(name="Original", value=f"```{text[:200]}```", inline=False)
    
    # Show Unicode conversion
    converted = comprehensive_unicode_to_ascii(text)
    if converted != text:
        embed.add_field(name="Unicode → ASCII (COMPLETE)", value=f"```{converted[:200]}```", inline=False)
    
    # Show ASCII art extraction
    if detect_multi_line_art(text):
        extracted = advanced_ascii_art_extraction(text)
        if extracted:
            embed.add_field(name="ASCII Art Extraction", value=f"`{', '.join(extracted[:10])}`", inline=False)
    
    # Show detection details
    details = []
    if re.search(r'[\U0001D400-\U0001D7FF]', text):
        details.append("Mathematical Unicode detected (ALL A-Z variants)")
    if re.search(r'[\U0001F1E6-\U0001F1FF]', text):
        details.append("Flag emojis detected (ALL country flags)")
    if is_non_english:
        details.append("Non-English language detected (STRICT)")
    
    if details:
        embed.add_field(name="COMPLETE Detection Details", value='\n'.join(f"• {d}" for d in details), inline=False)
    
    await ctx.send(embed=embed, delete_after=90)

@bot.command(name="filterhelp")
@commands.has_permissions(administrator=True)
async def filter_help(ctx):
    """Show all COMPLETE commands"""
    embed = discord.Embed(
        title="🛡️ COMPLETE Filter Bot Commands",
        description="Advanced bypass detection with COMPLETE A-Z Unicode + ALL flags + STRICT English-only",
        color=0x3498db
    )
    
    embed.add_field(
        name="📢 Channel Management",
        value="`$addchannel #channel` - Monitor channel\n"
              "`$removechannel #channel` - Stop monitoring\n"
              "`$listchannels` - Show monitored channels\n"
              "`$rescan` - COMPLETE scan for violations",
        inline=False
    )
    
    embed.add_field(
        name="🔍 Testing & Moderation",
        value="`$testmessage <text>` - Full COMPLETE test\n"
              "`$stats` - Show COMPLETE statistics",
        inline=False
    )
    
    embed.add_field(
        name="🎯 COMPLETE Features",
        value="✅ Auto-scans on startup (200 msgs/channel)\n"
              "❌ Spam detection REMOVED\n"
              "✅ ALL Mathematical Unicode A-Z detection\n"
              "✅ ALL Flag emoji detection (🇦-🇿)\n"
              "✅ STRICT English-only language detection\n"
              "✅ Enhanced ASCII art extraction\n"
              "✅ Diagonal & reverse reading\n"
              "✅ Mixed script detection\n"
              "✅ Leetspeak detection\n"
              "✅ Example: 𝔸ℕ𝕋𝕀 𝕂𝔽ℂ 𝔻𝕆𝔾 → DETECTED\n"
              "✅ Chinese/Non-English → BLOCKED",
        inline=False
    )
    
    await ctx.send(embed=embed, delete_after=120)

@bot.command(name="stats")
@commands.has_permissions(administrator=True)
async def show_stats(ctx):
    """Show COMPLETE bot statistics"""
    embed = discord.Embed(
        title="📊 COMPLETE Filter Bot Statistics",
        color=0x2ecc71
    )
    
    embed.add_field(name="Monitored Channels", value=str(len(MONITORED_CHANNELS)), inline=True)
    embed.add_field(name="Blocked Words", value=str(len(BLOCKED_WORDS)), inline=True)
    embed.add_field(name="Auto-Reply Patterns", value=str(len(AUTO_REPLY_PATTERNS)), inline=True)
    embed.add_field(name="Servers", value=str(len(bot.guilds)), inline=True)
    embed.add_field(name="Spam Detection", value="❌ REMOVED", inline=True)
    embed.add_field(name="Status", value="🟢 COMPLETE Active", inline=True)
    
    embed.add_field(
        name="COMPLETE Detection Capabilities",
        value="• ALL Mathematical Unicode A-Z mappings\n"
              "• ALL Flag emoji detection (🇦-🇿)\n"
              "• STRICT English-only language detection\n"
              "• Multi-directional ASCII art reading\n"
              "• Mixed script analysis\n"
              "• Leetspeak conversion\n"
              "• Example: 𝔸ℕ𝕋𝕀 𝕂𝔽ℂ 𝔻𝕆𝔾 → ANTI KFC DOG\n"
              "• Chinese text → BLOCKED IMMEDIATELY",
        inline=False
    )
    
    await ctx.send(embed=embed, delete_after=60)

# === ERROR HANDLING ===

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.", delete_after=10)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing required argument. Use `$filterhelp` for command list.", delete_after=10)
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid argument. Use `$filterhelp` for command list.", delete_after=10)
    else:
        print(f"Command error: {error}")

# === START BOT ===

if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN")
    
    if not token:
        print("❌ Bot token not found! Set DISCORD_TOKEN or TOKEN in your .env file.")
        exit(1)
    
    print("🚀 Starting COMPLETE Discord Filter Bot...")
    print("🛡️ COMPLETE Unicode Detection System Loading...")
    print("❌ Spam Detection System REMOVED...")
    print("🌐 STRICT English-Only Detection Loading...")
    print("🎯 ALL Flag Emoji Detection Loading...")
    print("🔤 ALL Mathematical A-Z Symbols Loading...")
    try:
        bot.run(token)
    except discord.LoginFailure:
        print("❌ Invalid bot token!")
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")




