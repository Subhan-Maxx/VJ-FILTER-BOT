import re
from difflib import SequenceMatcher
from PTT import parse_title
from guessit import guessit

def clean_string_for_comparison(text):
    """Special characters, dots, aur spaces ko remove karke titles ko comparison ke liye normalize karta hai."""
    if not text:
        return ""
    return re.sub(r'[^a-z0-9]', '', str(text).lower())

def get_similarity_score(a, b):
    """Dono strings ke beech structural similarity ratio return karta hai."""
    return SequenceMatcher(None, a, b).ratio()

def generate_clean_video_title(raw_title):
    # 1. Parse title using PTT library
    parsed = parse_title(raw_title, translate_languages=True)
    ptt_title = parsed.get("title", "").strip()
    
    # 2. Parse title using GuessIt library
    guess_info = guessit(raw_title)
    guess_title = guess_info.get("title", "").strip()
    
    # 3. Base Verification (Agar dono me se ek bhi blank hai toh direct reject)
    if not ptt_title or not guess_title:
        return None

    # Normalize titles for matching
    clean_ptt = clean_string_for_comparison(ptt_title)
    clean_guess = clean_string_for_comparison(guess_title)
    
    # 4. Year-Based Validation (Strict Check for Sequels/Prequels like Extraction 1 vs 2)
    ptt_year = parsed.get("year")
    guess_year = guess_info.get("year")
    if ptt_year and guess_year and int(ptt_year) != int(guess_year):
        return None  # Year mismatch matlab different movies/shows hain

    # 5. Robust Similarity Engine (Exact -> Substring -> SequenceMatcher)
    similarity_score = get_similarity_score(clean_ptt, clean_guess)
    
    is_valid_title = (
        clean_ptt == clean_guess or 
        clean_ptt in clean_guess or 
        clean_guess in clean_ptt or 
        similarity_score >= 0.92
    )
    
    if not is_valid_title:
        return None

    # --- VALIDATION PASSED: CLEANING LOGIC START ---
    t = guess_title if len(guess_title.split()) >= len(ptt_title.split()) else ptt_title   
     
    year = f"({ptt_year})" if ptt_year else ""
    date = parsed.get("date", "")
    resolution = parsed.get("resolution", "")
    quality = parsed.get("quality", "")
    bit_depth = parsed.get("bit_depth", "")
    codec = parsed.get("codec", "").upper() if parsed.get("codec") else ""
    region = parsed.get("region", "")
    episode_code = parsed.get("episode_code", "")
    
    # Flags & Technical tags
    edition = parsed.get("edition", "")
    unrated = "UNRATED" if parsed.get("unrated") else ""
    extended = "EXTENDED" if parsed.get("extended") else ""
    remastered = "REMASTERED" if parsed.get("remastered") else ""
    proper = "PROPER" if parsed.get("proper") else ""
    repack = "REPACK" if parsed.get("repack") else ""
    retail = "RETAIL" if parsed.get("retail") else ""
    complete = "Complete" if parsed.get("complete") else ""
    dubbed = "Dubbed" if parsed.get("dubbed") else ""
    hardcoded = "HC" if parsed.get("hardcoded") else ""
    ppv = "PPV" if parsed.get("ppv") else ""
    convert = "CONVERT" if parsed.get("convert") else ""
    upscaled = "UPSCALED" if parsed.get("upscaled") else ""
    documentary = "DOCU" if parsed.get("documentary") else ""
    
    # HDR Handling
    hdr_list = parsed.get("hdr", [])
    hdr = " ".join(hdr_list) if hdr_list else ""
    
    # Audio formatting
    audio_list = parsed.get("audio", [])
    audio = " ".join(audio_list) if audio_list else ""
    
    if (
        "Dolby Digital Plus" in audio_list
        or "DDP" in raw_title.upper()
        or "DD+" in raw_title.upper()
    ):
        audio = "DDP"
    elif (
        "Dolby Digital" in audio_list
        or re.search(r"\bDD\b", raw_title, re.I)
    ):
        audio = "DD"        
    
    
    channels = " ".join(parsed.get("channels", []))
    
    ext = parsed.get("extension") or parsed.get("container") or "mkv"
    ext_str = f".{ext}"
    
    # Season & Episode Formatting
    seasons = parsed.get("seasons", [])
    episodes = parsed.get("episodes", [])
    volumes = parsed.get("volumes", [])
    
    se_str = ""
    if seasons: se_str += f"S{str(seasons[0]).zfill(2)}"
    if episodes:
        if len(episodes) > 1: 
            se_str += f"E{str(episodes[0]).zfill(2)}-{str(episodes[-1]).zfill(2)}"
        else: 
            se_str += f"E{str(episodes[0]).zfill(2)}"
    if volumes: se_str += f" Vol.{','.join(map(str, volumes))}"
    if episode_code: se_str += f" {episode_code}"

    # --- 100% STRICT RAW TEXT SCANNING ENGINE FOR LANGUAGES ---
    lang_items = []
    supported_langs = {
        "Hindi": [r"\bhin(?:di)?\b"],
        "English": [r"\beng(?:lish)?\b"],
        "Telugu": [r"\btel(?:ugu)?\b"],
        "Tamil": [r"\btam(?:il)?\b"],
        "Malayalam": [r"\bmal(?:ayalam)?\b"],
        "Korean": [r"\bkor(?:ean)?\b"],
        "Kannada": [r"\bkan(?:nada)?\b"],
        "Marathi": [r"\bmar(?:athi)?\b"],
        "Bengali": [r"\bben(?:gali)?\b", r"\bbangla\b"],
        "Punjabi": [r"\bpun(?:jabi)?\b"],
        "Gujarati": [r"\bguj(?:arati)?\b"],
        "Odia": [r"\bod(?:ia)?\b", r"\boriya\b"],
        "Assamese": [r"\bass(?:amese)?\b"],
        "Urdu": [r"\burd(?:u)?\b"],
        "Japanese": [r"\bjap(?:anese)?\b"],
        "Chinese": [r"\bchi(?:nese)?\b", r"\bmandarin\b"],
        "Thai": [r"\bthai\b"],
        "Indonesian": [r"\bind(?:onesian)?\b", r"\bbahasa\b"],
        "Vietnamese": [r"\bviet(?:namese)?\b"],
        "Spanish": [r"\bspa(?:nish)?\b"],
        "French": [r"\bfre(?:nch)?\b"],
        "German": [r"\bger(?:man)?\b"],
        "Italian": [r"\bita(?:lian)?\b"],
        "Russian": [r"\brus(?:sian)?\b"],
        "Arabic": [r"\bar(?:abic)?\b"],
        "Turkish": [r"\btur(?:kish)?\b"],
        "Portuguese": [r"\bpor(?:tuguese)?\b"],
    }
    
    raw_lower = raw_title.lower()
    
    for lang_name, regex_patterns in supported_langs.items():
        for pattern in regex_patterns:
            if re.search(pattern, raw_lower):
                if lang_name not in lang_items:
                    lang_items.append(lang_name)
                break

    brackets_content = re.findall(r'\[([^\]]+)\]', raw_title)
    if brackets_content:
        for block in brackets_content:
            block_lower = block.lower()
            if block_lower == "dual audio":
                continue
            if any(l in block_lower for l in [
                "hindi", "english", "tamil", "telugu",
                "malayalam", "kannada", "marathi",
                "bengali", "bangla", "punjabi",
                "gujarati", "odia", "oriya",
                "assamese", "urdu", "korean",
                "japanese", "portuguese", "chinese",
                "mandarin", "thai", "indonesian",
                "bahasa", "vietnamese", "spanish",
                "french", "german", "italian",
                "russian", "arabic", "turkish",
                "hin", "eng", "tam", "tel",
                "mal", "kan", "mar", "ben",
                "pun", "guj", "kor", "jap",
                "chi", "spa", "fre", "ger",
                "ita", "rus", "tur", "por"
            ]) and any(a in block_lower for a in ["dd", "ddp", "5.1", "aac", "audi"]):
    
                parts = re.split(r'\s*[\-+\|~]\s*|\bor\b', block, flags=re.IGNORECASE)
                temp_items = []
                for p in parts:
                    p_clean = p.strip()
                    p_clean = re.sub(r'\bHin(?:di)?\b', 'Hindi', p_clean, flags=re.IGNORECASE)
                    p_clean = re.sub(r'\bEng(?:lish)?\b', 'English', p_clean, flags=re.IGNORECASE)
                    p_clean = re.sub(r'\bTam(?:il)?\b', 'Tamil', p_clean, flags=re.IGNORECASE)
                    p_clean = re.sub(r'\bTel(?:ugu)?\b', 'Telugu', p_clean, flags=re.IGNORECASE)
                    p_clean = re.sub(r'\bMal(?:ayalam)?\b', 'Malayalam', p_clean, flags=re.IGNORECASE)
                    p_clean = re.sub(r'\bKan(?:nada)?\b', 'Kannada', p_clean, flags=re.IGNORECASE)
                    p_clean = re.sub(r'\bMar(?:athi)?\b', 'Marathi', p_clean, flags=re.IGNORECASE)
                    p_clean = re.sub(r'\bBen(?:gali)?\b|\bBangla\b', 'Bengali', p_clean, flags=re.IGNORECASE)
                    p_clean = re.sub(r'\bPun(?:jabi)?\b', 'Punjabi', p_clean, flags=re.IGNORECASE)
                    p_clean = re.sub(r'\bGuj(?:arati)?\b', 'Gujarati', p_clean, flags=re.IGNORECASE)
                    p_clean = re.sub(r'\bOd(?:ia)?\b|\bOriya\b', 'Odia', p_clean, flags=re.IGNORECASE)
                    p_clean = re.sub(r'\bAss(?:amese)?\b', 'Assamese', p_clean, flags=re.IGNORECASE)
                    p_clean = re.sub(r'\bUrd(?:u)?\b', 'Urdu', p_clean, flags=re.IGNORECASE)
                    p_clean = re.sub(r'\bKor(?:ean)?\b', 'Korean', p_clean, flags=re.IGNORECASE)
                    p_clean = re.sub(r'\bJap(?:anese)?\b', 'Japanese', p_clean, flags=re.IGNORECASE)
                    p_clean = re.sub(r'\bChi(?:nese)?\b|\bMandarin\b', 'Chinese', p_clean, flags=re.IGNORECASE)
                    p_clean = re.sub(r'\bThai\b', 'Thai', p_clean, flags=re.IGNORECASE)
                    p_clean = re.sub(r'\bInd(?:onesian)?\b|\bBahasa\b', 'Indonesian', p_clean, flags=re.IGNORECASE)
                    p_clean = re.sub(r'\bViet(?:namese)?\b', 'Vietnamese', p_clean, flags=re.IGNORECASE)
                    p_clean = re.sub(r'\bSpa(?:nish)?\b', 'Spanish', p_clean, flags=re.IGNORECASE)
                    p_clean = re.sub(r'\bFre(?:nch)?\b', 'French', p_clean, flags=re.IGNORECASE)
                    p_clean = re.sub(r'\bGer(?:man)?\b', 'German', p_clean, flags=re.IGNORECASE)
                    p_clean = re.sub(r'\bIta(?:lian)?\b', 'Italian', p_clean, flags=re.IGNORECASE)
                    p_clean = re.sub(r'\bRus(?:sian)?\b', 'Russian', p_clean, flags=re.IGNORECASE)
                    p_clean = re.sub(r'\bAr(?:abic)?\b', 'Arabic', p_clean, flags=re.IGNORECASE)
                    p_clean = re.sub(r'\bTur(?:kish)?\b', 'Turkish', p_clean, flags=re.IGNORECASE)
                    p_clean = re.sub(r'\bPor(?:tuguese)?\b', 'Portuguese', p_clean, flags=re.IGNORECASE)

                    if p_clean:
                        temp_items.append(p_clean)
                if temp_items:
                    lang_items = temp_items

    # --- Merge language with its own audio tag (Unlimited languages) ---
    lang_audio_pattern = re.compile(
        r'''(?ix)
        \b
        (Hindi|English|Tamil|Telugu|Malayalam|Kannada|Marathi|Bengali|Bangla|
         Punjabi|Gujarati|Odia|Oriya|Assamese|Urdu|Japanese|Chinese|Mandarin|
         Korean|Thai|Indonesian|Bahasa|Vietnamese|Spanish|French|German|
         Italian|Russian|Arabic|Turkish|Portuguese)
        \b
        (?:
            \s+
            (?:
                DDP?|\bDD\+?\b|
                Dolby\s+Digital(?:\s+Plus)?|
                AAC|AC3|EAC3|Atmos|TrueHD|
                DTS(?:-HD)?(?:\s+MA)?|
                FLAC|MP3|PCM
            )
            (?:\s*\d\.\d)?
        )?
        ''',
        re.I
    )
    matches = list(lang_audio_pattern.finditer(raw_title))

    if matches:
        new_lang_items = []

        for m in matches:
            text = m.group(0).strip()

            # Normalize language names
            text = re.sub(r'\bHin(?:di)?\b', 'Hindi', text, flags=re.I)
            text = re.sub(r'\bEng(?:lish)?\b', 'English', text, flags=re.I)
            text = re.sub(r'\bTam(?:il)?\b', 'Tamil', text, flags=re.I)
            text = re.sub(r'\bTel(?:ugu)?\b', 'Telugu', text, flags=re.I)
            text = re.sub(r'\bMal(?:ayalam)?\b', 'Malayalam', text, flags=re.I)
            text = re.sub(r'\bKan(?:nada)?\b', 'Kannada', text, flags=re.I)
            text = re.sub(r'\bMar(?:athi)?\b', 'Marathi', text, flags=re.I)
            text = re.sub(r'\bBen(?:gali)?\b|\bBangla\b', 'Bengali', text, flags=re.I)
            text = re.sub(r'\bPun(?:jabi)?\b', 'Punjabi', text, flags=re.I)
            text = re.sub(r'\bGuj(?:arati)?\b', 'Gujarati', text, flags=re.I)
            text = re.sub(r'\bOd(?:ia)?\b|\bOriya\b', 'Odia', text, flags=re.I)
            text = re.sub(r'\bAss(?:amese)?\b', 'Assamese', text, flags=re.I)
            text = re.sub(r'\bUrd(?:u)?\b', 'Urdu', text, flags=re.I)
            text = re.sub(r'\bKor(?:ean)?\b', 'Korean', text, flags=re.I)
            text = re.sub(r'\bJap(?:anese)?\b', 'Japanese', text, flags=re.I)
            text = re.sub(r'\bChi(?:nese)?\b|\bMandarin\b', 'Chinese', text, flags=re.I)
            text = re.sub(r'\bSpa(?:nish)?\b', 'Spanish', text, flags=re.I)
            text = re.sub(r'\bFre(?:nch)?\b', 'French', text, flags=re.I)
            text = re.sub(r'\bGer(?:man)?\b', 'German', text, flags=re.I)
            text = re.sub(r'\bIta(?:lian)?\b', 'Italian', text, flags=re.I)
            text = re.sub(r'\bRus(?:sian)?\b', 'Russian', text, flags=re.I)
            text = re.sub(r'\bAr(?:abic)?\b', 'Arabic', text, flags=re.I)
            text = re.sub(r'\bTur(?:kish)?\b', 'Turkish', text, flags=re.I)
            text = re.sub(r'\bPor(?:tuguese)?\b', 'Portuguese', text, flags=re.I)

            text = " ".join(text.split())

            if text not in new_lang_items:
                new_lang_items.append(text)

        if new_lang_items:
            lang_items = new_lang_items
        

    # Priority Sort: Move Hindi to index 0
    hindi_item = None
    for item in lang_items:
        if "Hindi" in item:
            hindi_item = item
            break
    if hindi_item:
        lang_items.remove(hindi_item)
        lang_items.insert(0, hindi_item)

    lang_str = ""
    if lang_items:
        connector = " or " if "or" in raw_title.lower() else " - "
        lang_str = f"[{connector.join(lang_items)}]"

    dual_audio_tag = "[Dual Audio]" if "dual audio" in raw_title.lower() or "dual" in raw_title.lower() else ""

    audio_details = ""
    audio_keywords = [
        "DD", "DDP", "AAC", "AC3", "EAC3",
        "DTS", "DTS-HD", "TRUEHD", "ATMOS",
        "FLAC", "PCM", "MP3",
        "2.0", "5.1", "7.1"
    ]
    if (audio or channels) and not any(
        any(k.upper() in item.upper() for k in audio_keywords)
        for item in lang_items
    ):
        audio_details = f"[{audio} {channels}]".strip().replace("  ", " ")
    
   # --- Language-specific subtitle detection (STRICT) ---
    subtitle_tag = ""
    subtitle_patterns = {
        "ESubs": [
            r"\besubs\b",
            r"\b(?:english|eng)[\s._-]{0,3}(?:subs?|subtitles?)\b",
        ],
        "HSubs": [
            r"\bhsubs\b",
            r"\b(?:hindi|hin)[\s._-]{0,3}(?:subs?|subtitles?)\b",
        ],
        "TSubs": [
            r"\btsubs\b",
            r"\b(?:tamil|tam)[\s._-]{0,3}(?:subs?|subtitles?)\b",
        ],
        "TelSubs": [
            r"\btelsubs\b",
            r"\b(?:telugu|tel)[\s._-]{0,3}(?:subs?|subtitles?)\b",
        ],
        "MLSubs": [
            r"\bmlsubs\b",
            r"\b(?:malayalam|mal)[\s._-]{0,3}(?:subs?|subtitles?)\b",
        ],
    }

    for tag, patterns in subtitle_patterns.items():
        if any(re.search(p, raw_lower, re.IGNORECASE) for p in patterns):
            subtitle_tag = tag
            break

    # Subtitle present but language unknown
    if not subtitle_tag and parsed.get("subbed"):
        subtitle_tag = "Subs"

  # --- STREAMING PLATFORM DETECTOR ENGINE (WEB RELEASES ONLY) ---

    platform_tag = ""

    # Sirf WEB releases me platform detect karo
    is_web_release = (
        "web" in raw_lower or
        "web-dl" in raw_lower or
        "webdl" in raw_lower or
        "webrip" in raw_lower or
        "web-rip" in raw_lower
    )

    if is_web_release:
        platform_mapping = {
            "NF": [r"\bnf\b", r"\bnetflix\b"],
            "AMZN": [r"\bamzn\b", r"\bamazon\s*prime\b", r"\bprime\s*video\b"],
            "DSNP": [r"\bdsnp\b", r"\bdisney\+\b", r"\bdisneyplus\b"],
            "HOTSTAR": [r"\bhotstar\b", r"\bdisney\+?\s*hotstar\b"],
            "ATVP": [r"\batvp\b", r"\bapple\s*tv\+\b", r"\bapple\s*tv\b"],
            "HULU": [r"\bhulu\b"],
            "MAX": [r"\bhbo\s*max\b", r"\bmax\b"],
            "HBO": [r"\bhbo\b"],
            "PCOK": [r"\bpcok\b", r"\bpeacock\b"],
            "PMTP": [r"\bpmtp\b", r"\bparamount\+\b", r"\bparamount\b"],
            "CR": [r"\bcr\b", r"\bcrunchyroll\b"],
            "FUNI": [r"\bfuni\b", r"\bfunimation\b"],
            "BBC": [r"\bbbc\s*iplayer\b", r"\biplayer\b"],
            "ITV": [r"\bitvx\b", r"\bitv\b"],
            "ALL4": [r"\ball4\b", r"\bchannel\s*4\b"],
            "MY5": [r"\bmy5\b"],
            "STAN": [r"\bstan\b"],
            "BINGE": [r"\bbinge\b"],
            "VIU": [r"\bviu\b"],
            "VIKI": [r"\bviki\b", r"\brakuten\s*viki\b"],
            "IQIYI": [r"\biqiyi\b"],
            "YOUKU": [r"\byouku\b"],
            "MGO": [r"\bmangotv\b", r"\bmgo\b"],
            "WETV": [r"\bwetv\b", r"\btencent\b"],
            "JIO": [r"\bjiocinema\b", r"\bjio\b"],
            "ZEE5": [r"\bzee5\b", r"\bz5\b"],
            "SONYLIV": [r"\bsonyliv\b", r"\bsony\s*liv\b"],
            "AHA": [r"\baha\b"],
            "SUNNXT": [r"\bsunnxt\b", r"\bsun\s*nxt\b"],
            "HOICHOI": [r"\bhoichoi\b"],
            "CHAUPAL": [r"\bchaupal\b"],
            "LIONSGATE": [r"\blionsgate\s*play\b", r"\blionsgate\b"],
            "DISCOVERY": [r"\bdiscovery\+\b", r"\bdiscoveryplus\b"],
            "TUBI": [r"\btubi\b"],
            "ROKU": [r"\broku\s*channel\b", r"\broku\b"],
            "PLEX": [r"\bplex\b"],
            "SHAHID": [r"\bshahid\b"],
            "TOD": [r"\btod\b"]
        }

        for tag, patterns in platform_mapping.items():
            if any(re.search(pattern, raw_lower, re.IGNORECASE) for pattern in patterns):
                platform_tag = tag
                break
            
    # Hierarchy arrangement mapping
    components = [
        t, year, date, se_str, complete, edition, unrated, extended, remastered, 
        proper, repack, retail, ppv, convert, upscaled, documentary, resolution, 
        bit_depth, codec, hdr, platform_tag, quality, region, dual_audio_tag, lang_str, dubbed, hardcoded, 
        audio_details, subtitle_tag
    ]
    
    clean_title = " ".join([str(c) for c in components if c])
    clean_title = " ".join(clean_title.split())
    
    if not clean_title.endswith(ext_str):
        clean_title += ext_str
        
    return clean_title
  