import re


GENERAL_KNOWLEDGE_PATTERNS = (
    r"\b(?:what is|what are|what does|explain|define)\b.*\b(?:lbw|leg before wicket|"
    r"no[- ]?ball|wide ball|maiden over|powerplay|yorker|bouncer|googly|doosra|boundary|"
    r"test cricket|one day international|odi|t20i?|innings|wicket|over|icc|umpire)\b",
    r"\bhow many runs (?:is|does) a (?:six|four) (?:worth|score)\b",
    r"\bhow many players (?:are )?(?:there )?(?:on the field|in|on) (?:a )?(?:cricket )?team\b",
    r"\bhow long (?:can|does) (?:a )?(?:test match|test cricket|odi|one day international|t20i?)\b",
    r"\bwhat (?:are|is) (?:the )?(?:main )?(?:formats?|rules?) of cricket\b",
    r"\bwho (?:governs|is the governing body for) (?:international )?cricket\b",
)

DATABASE_INTENT_PATTERNS = (
    r"\b(?:database|registered|scorecard|career stats?|statistics|records)\b",
    r"\b(?:who|which player|which team) (?:scored|has scored|won|has won|took|has taken)\b",
    r"\bhow many (?:runs|wickets|matches|wins|centuries|fifties) (?:did|has|have)\b",
)

CURRENT_MATCH_PATTERNS = (
    r"\b(?:today|yesterday|tonight|live|right now|latest)\b.*\b(?:score|match|game|result|winner)\b",
    r"\b(?:current|latest)\s+(?:score|match|result)\b",
)


def is_current_match_question(question: str) -> bool:
    normalized_question = question.lower().strip()
    return any(re.search(pattern, normalized_question) for pattern in CURRENT_MATCH_PATTERNS)


def is_general_knowledge_question(question: str) -> bool:
    normalized_question = question.lower().strip()
    if is_current_match_question(normalized_question):
        return False
    if any(re.search(pattern, normalized_question) for pattern in DATABASE_INTENT_PATTERNS):
        return False
    return any(re.search(pattern, normalized_question) for pattern in GENERAL_KNOWLEDGE_PATTERNS)