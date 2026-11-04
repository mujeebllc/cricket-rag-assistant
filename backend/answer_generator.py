import re
from datetime import datetime, date
from langchain_ollama import OllamaLLM
from prompts.answer_prompt import ANSWER_PROMPT

llm = OllamaLLM(model="qwen2.5:7b", temperature=0)

# Vocabulary dictionaries for Roman Urdu detection
STRONG_ROMAN_URDU_WORDS = {
    "kon", "kaun", "koun", "kitni", "kitne", "kitna", "khiladi", "khilari",
    "banaye", "banai", "diye", "diya", "sabse", "ziyada", "zyada", "teamen",
    "teamein", "batao", "konsa", "konsi", "konga", "kiske", "kisne", "kahan",
    "kyun", "huay", "karta", "karte", "karna", "gaya", "gayi"
}

# Weak Roman Urdu words - must be matched carefully to avoid English false positives
WEAK_ROMAN_URDU_WORDS = {
    "hai", "hain", "kya", "ka", "ki", "ke", "ne", "mein", "se",
    "ko", "par", "aur", "kis", "kab", "hua", "tha", "thi", "the", "sab",
    "kam", "bhi", "per", "ho"
}

ENGLISH_INDICATOR_PATTERNS = [
    r"\bhow many\b", r"\bwhat is\b", r"\bwho (?:is|scored|has|took)\b",
    r"\bwhich (?:player|team|country|bowler)\b", r"\bcan you tell me\b",
    r"\bgive me the\b", r"\bin the database\b", r"\bstart date\b", r"\bshort name\b",
    r"\btotal number of\b", r"\bregistered players\b"
]


def detect_language(text):
    """
    Detects whether the user question is written in English or Roman Urdu.
    Urdu script is unsupported and defaults to English/Roman Urdu.
    """
    if not text:
        return "english"

    text_lower = text.lower()

    # If sentence contains prominent English phrasing patterns, prioritize English
    english_matches = sum(1 for pat in ENGLISH_INDICATOR_PATTERNS if re.search(pat, text_lower))
    if english_matches >= 1:
        # Unless strong Roman Urdu words are also explicitly present
        words = set(re.findall(r'\b[a-zA-Z]+\b', text_lower))
        if len(words.intersection(STRONG_ROMAN_URDU_WORDS)) == 0:
            return "english"

    # Extract ASCII words
    words = set(re.findall(r'\b[a-zA-Z]+\b', text_lower))

    # 1. Check strong Roman Urdu indicators
    if len(words.intersection(STRONG_ROMAN_URDU_WORDS)) >= 1:
        return "roman_urdu"

    # 2. Check structural/weak Roman Urdu words (must have at least 2 distinct ones)
    if len(words.intersection(WEAK_ROMAN_URDU_WORDS)) >= 2:
        return "roman_urdu"

    return "english"


def clean_llm_answer(answer_text, lang):
    """
    Post-process LLM output to strip quotation marks, code fences, or Perso-Arabic characters.
    """
    if not answer_text:
        return ""
    text = answer_text.strip()
    text = re.sub(r'^["\']|["\']$', '', text).strip()

    # Strip any accidental Perso-Arabic / Urdu script characters
    text = re.sub(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]', '', text).strip()
    text = re.sub(r'\s+', ' ', text)

    return text


def format_cell_value(val):
    if isinstance(val, (datetime, date)):
        return val.strftime("%Y-%m-%d")
    return val


def generate_answer(question, sql, columns, rows):
    """
    Generate a natural language answer based on MariaDB SQL query results in English or Roman Urdu.
    """
    lang = detect_language(question)

    if not rows:
        if lang == "roman_urdu":
            return "Koi matching data ya record nahi mila."
        else:
            return "No matching records were found."

    # Format datetime objects across rows
    formatted_rows = []
    for r in rows:
        formatted_rows.append(tuple(format_cell_value(v) for v in r))
    rows = formatted_rows

    question_lower = question.lower()
    sql_lower = sql.lower()
    first_row = rows[0]

    # Deterministic Single-Value Attribute formatting (Preserves exact DB values for styles, names, roles, dates)
    if len(rows) == 1 and len(columns) == 1 and not re.search(r"\b(count|sum|avg|max|min)\b", sql_lower):
        val = first_row[0]
        if val is not None:
            val_str = str(val).strip()
            if "batting style" in question_lower:
                if lang == "roman_urdu":
                    return f"Unka batting style {val_str} hai."
                else:
                    return f"The batting style is {val_str}."
            if "bowling style" in question_lower:
                if lang == "roman_urdu":
                    return f"Unka bowling style {val_str} hai."
                else:
                    return f"The bowling style is {val_str}."
            if "playing role" in question_lower:
                if lang == "roman_urdu":
                    return f"Unka playing role {val_str} hai."
                else:
                    return f"The playing role is {val_str}."
            if "start date" in question_lower:
                if lang == "roman_urdu":
                    return f"Start date {val_str} hai."
                else:
                    return f"The start date is {val_str}."
            if "short name" in question_lower:
                if lang == "roman_urdu":
                    return f"Short name {val_str} hai."
                else:
                    return f"The short name is {val_str}."

    # Deterministic Count Formatting
    if ("count(" in sql_lower or "total" in sql_lower) and len(rows) == 1 and len(columns) == 1:
        value = first_row[0]
        if value is None:
            value = 0

        if "ground" in question_lower or "grounds" in question_lower:
            if lang == "roman_urdu":
                return f"Database mein total {value:,} grounds hain."
            else:
                return f"There are {value:,} grounds in the database."

        if "association" in question_lower:
            if lang == "roman_urdu":
                return f"Database mein total {value:,} cricket associations hain."
            else:
                return f"There are {value:,} cricket associations in the database."

        if "player" in question_lower or "khiladi" in question_lower:
            if lang == "roman_urdu":
                return f"Database mein total {value:,} khiladi hain."
            else:
                return f"There are {value:,} players in the database."

        if "team" in question_lower or "teams" in question_lower:
            if lang == "roman_urdu":
                return f"Database mein total {value:,} teams hain."
            else:
                return f"There are {value:,} teams in the database."

        if "tournament" in question_lower:
            if lang == "roman_urdu":
                return f"Database mein total {value:,} tournaments hain."
            else:
                return f"There are {value:,} tournaments in the database."

        if "match" in question_lower or "matches" in question_lower:
            if lang == "roman_urdu":
                return f"Database mein total {value:,} matches hain."
            else:
                return f"There are {value:,} matches in the database."

        if lang == "roman_urdu":
            return f"Total count {value:,} hai."
        else:
            return f"The total count is {value:,}."

    # Deterministic Sum Formatting
    if "sum(" in sql_lower and len(rows) == 1 and len(columns) == 1:
        value = first_row[0]
        if value is None:
            value = 0

        if "run" in question_lower or "runs" in question_lower:
            if lang == "roman_urdu":
                return f"Total runs {value:,} hain."
            else:
                return f"The total runs are {value:,}."

        if lang == "roman_urdu":
            return f"Total {value:,} hai."
        else:
            return f"The total is {value:,}."

    # LLM-based Natural Language Formatting for Complex / Profile / Ranking Queries
    if lang == "roman_urdu":
        target_lang_str = "Roman Urdu (STRICT REQUIREMENT: Write ONLY in detailed, natural Roman Urdu using Latin script. Do NOT output any Urdu script characters.)"
    else:
        target_lang_str = "English (STRICT REQUIREMENT: Write ONLY in clear English using Latin script.)"

    prompt = ANSWER_PROMPT.format(
        question=question,
        target_language=target_lang_str,
        sql=sql,
        columns=list(columns),
        rows=rows[:20]
    )

    response = llm.invoke(prompt)
    ans = clean_llm_answer(response, lang)

    # Fallback to rich factual summary if LLM output is empty or truncated
    if not ans or len(ans) < 5:
        if rows:
            r = rows[0]
            if len(columns) >= 3:
                row_dict = dict(zip(columns, r))
                name = row_dict.get("FullName") or row_dict.get("PlayerName") or row_dict.get("BatsmanName") or str(r[0])
                role = row_dict.get("PlayingRole") or row_dict.get("BattingStyle") or ""
                country = row_dict.get("Country") or "Pakistan"
                if lang == "roman_urdu":
                    ans = f"{name} database ke mutabiq {country} ke player hain."
                    if role:
                        ans += f" Unka playing role/style {role} hai."
                else:
                    ans = f"{name} is listed in the database as a player from {country}."
                    if role:
                        ans += f" Their playing role/style is {role}."
            else:
                ans = str(r[0])
        else:
            ans = "No matching records were found."

    return ans

