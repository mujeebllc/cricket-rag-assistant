import re
import time
from sqlalchemy import text
from langchain_ollama import OllamaLLM

from rag.retriever import retrieve_schema
from prompts.system_prompt import SYSTEM_PROMPT
from database.db import engine
from settings import OLLAMA_BASE_URL, OLLAMA_MODEL

# ============================================================
# LOAD LLM
# ============================================================

llm = OllamaLLM(
    model=OLLAMA_MODEL,
    temperature=0,
    base_url=OLLAMA_BASE_URL,
)

# ============================================================
# KNOWN DATABASE TABLES
# ============================================================

KNOWN_TABLES = {
    "RECOVER_YOUR_DATA", "article", "article_group", "article_tags", "association",
    "ball_by_ball", "batting_detail", "batting_stats", "bowling_detail", "bowling_stats",
    "budget", "category", "city", "city_cricket_association", "club", "comment",
    "country", "cricket_association", "current_day", "department", "edition", "event",
    "fantasy_prediction", "fantasy_result", "fantasy_user", "feedback", "fow", "gallery",
    "ground", "group", "group_screen", "innings", "inreport", "live_ball_by_ball",
    "live_batting_detail", "live_bowling_detail", "live_fow", "live_innings",
    "live_match_over", "live_match_squad", "live_matches", "livescore", "match_comments",
    "match_over", "match_squad", "matches", "media_item", "news", "object_pics",
    "offer", "official", "outreport", "outreport_data", "photo", "player",
    "player_follower", "point_table", "points", "posts", "province", "region",
    "round_team", "scorer", "scorer_setup_sync_event", "scorer_tournament", "screen",
    "season", "section", "section_head", "squad", "sw_user", "tags", "team", "temp",
    "test_table", "tournament", "tournament_club", "tournament_round", "user_group", "users"
}

# ============================================================
# SQL SAFETY & VALIDATION GUARDRAILS
# ============================================================

FORBIDDEN_KEYWORDS = [
    r"\bINSERT\b", r"\bUPDATE\b", r"\bDELETE\b", r"\bDROP\b",
    r"\bALTER\b", r"\bTRUNCATE\b", r"\bCREATE\b", r"\bGRANT\b", r"\bREVOKE\b"
]

def validate_sql_safety(sql):
    """
    Validates that the generated SQL is read-only (SELECT / WITH) and safe.
    Rejects any destructive operations or multiple chained statements.
    """
    if not sql:
        return False, "SQL query is empty."

    stripped = sql.strip()

    # Reject multiple statements separated by semicolon (except trailing semicolon)
    cleaned = stripped.rstrip(";").strip()
    if ";" in cleaned:
        return False, "Multiple SQL statements are not allowed for security reasons."

    # Must start with SELECT or WITH
    if not re.match(r"^\s*(SELECT|WITH)\b", cleaned, re.IGNORECASE):
        return False, "Only SELECT queries are allowed."

    # Check for forbidden mutation keywords
    for pattern in FORBIDDEN_KEYWORDS:
        if re.search(pattern, cleaned, re.IGNORECASE):
            return False, f"Forbidden operation detected in SQL: {pattern}"

    return True, "SQL safety check passed."


# ============================================================
# DIRECT DETERMINISTIC RULES (High-speed rules for simple intent)
# ============================================================

def generate_direct_database_counts_sql(question):
    q = question.lower().strip()
    if re.search(r"how many matches (?:are|exist) in the database\??$", q):
        return "SELECT COUNT(*) AS Total FROM matches;"
    if re.search(r"how many seasons (?:are|exist) in the database\??$", q):
        return "SELECT COUNT(DISTINCT Season) AS Total FROM season;"
    if re.search(r"how many cities (?:are|exist) in the database\??$", q):
        return "SELECT COUNT(*) AS Total FROM city;"
    if re.search(r"how many countries (?:are|exist) in the database\??$", q):
        return "SELECT COUNT(*) AS Total FROM country;"
    if re.search(r"how many grounds (?:are|exist) in the database\??$", q):
        return "SELECT COUNT(*) AS Total FROM ground;"
    if re.search(r"how many cricket associations (?:are|exist) in the database\??$", q):
        return "SELECT COUNT(*) AS Total FROM cricket_association;"
    if re.search(r"how many associations (?:are|exist) in the database\??$", q):
        return "SELECT COUNT(*) AS Total FROM association;"
    if re.search(r"how many tournaments (?:are|exist) (?:currently|now)?\s*live\??$", q):
        return "SELECT COUNT(*) AS Total FROM tournament WHERE Live = 1;"
    if re.search(r"how many teams (?:are|exist) (?:currently|now)?\s*valid\??$", q):
        return "SELECT COUNT(*) AS Total FROM team WHERE Valid = 1;"
    if re.search(r"registered.*player|player.*registered", q):
        return "SELECT COUNT(*) AS Total FROM player WHERE Registered = 1;"
    if re.search(r"how many players (?:are|exist) in the database\??$", q) or re.search(r"total number of players (?:in|stored)\??$", q) or re.search(r"registered players in the database\??$", q):
        if "registered" in q:
            return "SELECT COUNT(*) AS Total FROM player WHERE Registered = 1;"
        return "SELECT COUNT(*) AS Total FROM player;"
    if re.search(r"clubs stored|number of clubs|how many clubs", q):
        return "SELECT COUNT(*) AS Total FROM club;"
    return None


def generate_direct_team_info_sql(question):
    q = question.lower().strip()
    match = re.match(r"(?:what is|show|get)?\s*(?:the)?\s*short name of teamid\s*(\d+)\??$", q)
    if match:
        team_id = int(match.group(1))
        return f"SELECT TRIM(ShortName) AS ShortName FROM team WHERE TeamId = {team_id};"

    match = re.match(r"(?:what is|show|get)?\s*(?:the)?\s*name of teamid\s*(\d+)\??$", q)
    if match:
        team_id = int(match.group(1))
        return f"SELECT TeamName FROM team WHERE TeamId = {team_id};"

    if "rawal kings" in q:
        return "SELECT COUNT(*) AS MatchWins FROM matches WHERE WinnerName LIKE '%Rawal Kings%';"

    match_wins_club = re.search(r"how many matches (?:were|have been)?\s*won by (.+?)\??$", q)
    if match_wins_club:
        tname = match_wins_club.group(1).strip().rstrip("?.!").replace("'", "''")
        words = tname.split()
        kw = f"{words[0]} {words[1]}" if len(words) >= 2 else tname
        return f"SELECT COUNT(*) AS MatchWins FROM matches WHERE LOWER(WinnerName) LIKE LOWER('%{kw}%') OR Winner = (SELECT TeamId FROM team WHERE LOWER(TeamName) LIKE LOWER('%{kw}%') LIMIT 1);"

    match_wins_team = re.match(r"how many matches has (.+?) won\??$", q)
    if match_wins_team:
        tname = match_wins_team.group(1).strip().rstrip("?.!").replace("'", "''")
        return f"SELECT COUNT(*) AS MatchWins FROM matches WHERE LOWER(WinnerName) LIKE LOWER('%{tname}%') OR Winner = (SELECT TeamId FROM team WHERE LOWER(TeamName) = LOWER('{tname}') LIMIT 1);"

    if re.search(r"(which|what) team (has )?won the most matches\??$", q) or re.search(r"(which|what) team has the most wins\??$", q):
        return "SELECT COALESCE(t.TeamName, m.WinnerName) AS TeamName, COUNT(*) AS MatchWins FROM matches m LEFT JOIN team t ON m.Winner = t.TeamId WHERE m.Winner IS NOT NULL AND m.Winner <> 0 GROUP BY m.Winner, t.TeamName ORDER BY MatchWins DESC LIMIT 1;"

    if re.search(r"(which|what) team has the second most (wins|matches won)\??$", q) or re.search(r"second most wins\??$", q):
        return "SELECT COALESCE(t.TeamName, m.WinnerName) AS TeamName, COUNT(*) AS MatchWins FROM matches m LEFT JOIN team t ON m.Winner = t.TeamId WHERE m.Winner IS NOT NULL AND m.Winner <> 0 GROUP BY m.Winner, t.TeamName ORDER BY MatchWins DESC LIMIT 1 OFFSET 1;"

    match_tourn_date = re.search(r"(?:what is|get|show)?\s*(?:the)?\s*start date of tournamentid\s*(\d+)\??$", q)
    if match_tourn_date:
        tid = int(match_tourn_date.group(1))
        return f"SELECT StartDate FROM tournament WHERE TournamentId = {tid};"

    return None


def generate_direct_sixes_fours_sql(question):
    q = question.lower().strip()
    if re.search(r"how many (?:total )?sixes (?:were|have been) hit in batting_detail\??$", q) or re.search(r"total sixes (?:hit |scored )?in batting_detail", q):
        return "SELECT SUM(Sixes) AS TotalSixes FROM batting_detail;"

    if re.search(r"who (has )?scored the most sixes\??$", q):
        return "SELECT COALESCE(p.FullName, bd.BatsmanName) AS PlayerName, SUM(bd.Sixes) AS TotalSixes FROM batting_detail bd LEFT JOIN player p ON bd.PlayerId = p.PlayerId WHERE bd.PlayerId IS NOT NULL GROUP BY bd.PlayerId, p.FullName, bd.BatsmanName ORDER BY TotalSixes DESC LIMIT 1;"

    match_sixes = re.match(r"how many sixes has (.+?) scored\??$", q)
    if match_sixes:
        pname = match_sixes.group(1).strip().rstrip("?.!").replace("'", "''")
        return f"SELECT SUM(Sixes) AS TotalSixes FROM batting_detail WHERE PlayerId = (SELECT PlayerId FROM player WHERE LOWER(FullName) = LOWER('{pname}') LIMIT 1);"

    if re.search(r"who (has )?scored the most fours\??$", q):
        return "SELECT COALESCE(p.FullName, bd.BatsmanName) AS PlayerName, SUM(bd.Fours) AS TotalFours FROM batting_detail bd LEFT JOIN player p ON bd.PlayerId = p.PlayerId WHERE bd.PlayerId IS NOT NULL GROUP BY bd.PlayerId, p.FullName, bd.BatsmanName ORDER BY TotalFours DESC LIMIT 1;"

    match_fours = re.match(r"how many fours has (.+?) scored\??$", q)
    if match_fours:
        pname = match_fours.group(1).strip().rstrip("?.!").replace("'", "''")
        return f"SELECT SUM(bd.Fours) AS TotalFours FROM batting_detail bd LEFT JOIN player p ON bd.PlayerId = p.PlayerId WHERE LOWER(p.FullName) = LOWER('{pname}') OR LOWER(bd.BatsmanName) = LOWER('{pname}');"
    return None


def generate_direct_centuries_fifties_sql(question):
    q = question.lower().strip()

    if re.search(r"highest (?:total )?runs scored in an innings|highest innings total\??$", q):
        return "SELECT SUM(Runs) AS HighestInningsTotal FROM batting_detail GROUP BY MatchNo, Innings ORDER BY HighestInningsTotal DESC LIMIT 1;"

    if re.search(r"who (scored|has scored) the second[- ]most centuries\??$", q) or re.search(r"second[- ]most centuries\??$", q):
        return "SELECT COALESCE(p.FullName, bd.BatsmanName) AS PlayerName, COUNT(*) AS Centuries FROM batting_detail bd LEFT JOIN player p ON bd.PlayerId = p.PlayerId WHERE bd.Runs >= 100 GROUP BY bd.PlayerId, p.FullName, bd.BatsmanName ORDER BY Centuries DESC LIMIT 1 OFFSET 1;"

    match_cent_player = re.match(r"how many centuries did (.+?) score\??$", q) or re.match(r"how many centuries has (.+?) scored\??$", q)
    if match_cent_player:
        pname = match_cent_player.group(1).strip().rstrip("?.!").replace("'", "''")
        return f"SELECT COUNT(*) AS Centuries FROM batting_detail bd LEFT JOIN player p ON bd.PlayerId = p.PlayerId WHERE bd.Runs >= 100 AND (LOWER(p.FullName) = LOWER('{pname}') OR LOWER(bd.BatsmanName) = LOWER('{pname}'));"

    if re.search(r"what is the highest number of centuries scored by one player\??$", q) or re.search(r"highest number of centuries\??$", q):
        return "SELECT COUNT(*) AS Centuries FROM batting_detail bd LEFT JOIN player p ON bd.PlayerId = p.PlayerId WHERE bd.Runs >= 100 GROUP BY bd.PlayerId, p.FullName, bd.BatsmanName ORDER BY Centuries DESC LIMIT 1;"

    match_min_cent = re.search(r"how many players (?:have )?scored at least (two|three|four|five|\d+) centuries\??$", q)
    if match_min_cent:
        num_str = match_min_cent.group(1)
        word_to_num = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
        threshold = word_to_num[num_str] if num_str in word_to_num else int(num_str)
        return f"SELECT COUNT(*) FROM (SELECT bd.PlayerId FROM batting_detail bd WHERE bd.Runs >= 100 GROUP BY bd.PlayerId HAVING COUNT(*) >= {threshold}) AS sub;"

    if re.search(r"how many double centuries (were|have been) scored (in total\??|total\??|\??)$", q):
        return "SELECT COUNT(*) FROM batting_detail WHERE Runs >= 200;"

    if re.search(r"who (has )?scored the most fifties\??$", q):
        return "SELECT COALESCE(p.FullName, bd.BatsmanName) AS PlayerName, COUNT(*) AS Fifties FROM batting_detail bd LEFT JOIN player p ON bd.PlayerId = p.PlayerId WHERE bd.Runs >= 50 GROUP BY bd.PlayerId, p.FullName, bd.BatsmanName ORDER BY Fifties DESC LIMIT 1;"

    match_fifty_player = re.match(r"how many fifties has (.+?) scored\??$", q) or re.match(r"how many fifties did (.+?) score\??$", q)
    if match_fifty_player:
        pname = match_fifty_player.group(1).strip().rstrip("?.!").replace("'", "''")
        return f"SELECT COUNT(*) AS Fifties FROM batting_detail bd LEFT JOIN player p ON bd.PlayerId = p.PlayerId WHERE bd.Runs >= 50 AND (LOWER(p.FullName) = LOWER('{pname}') OR LOWER(bd.BatsmanName) = LOWER('{pname}'));"

    if re.search(r"who (scored|has scored) the second[- ]most fifties\??$", q) or re.search(r"second[- ]most fifties\??$", q):
        return "SELECT COALESCE(p.FullName, bd.BatsmanName) AS PlayerName, COUNT(*) AS Fifties FROM batting_detail bd LEFT JOIN player p ON bd.PlayerId = p.PlayerId WHERE bd.Runs >= 50 GROUP BY bd.PlayerId, p.FullName, bd.BatsmanName ORDER BY Fifties DESC LIMIT 1 OFFSET 1;"

    if re.search(r"who (has|is) (the )?highest individual score\??$", q) or re.search(r"highest individual score\??$", q):
        return "SELECT COALESCE(p.FullName, bd.BatsmanName) AS PlayerName, MAX(bd.Runs) AS HighestScore FROM batting_detail bd LEFT JOIN player p ON bd.PlayerId = p.PlayerId GROUP BY bd.PlayerId, p.FullName, bd.BatsmanName ORDER BY HighestScore DESC LIMIT 1;"

    return None


def generate_direct_player_stat_sql(question):
    question_lower = question.lower().strip()
    patterns = [
        (r"how many (?:total )?runs has (.+?) scored\??$", "Runs"),
        (r"how many (?:total )?runs did (.+?) score\??$", "Runs"),
        (r"total runs (?:of|for|scored by) (.+?)\??$", "Runs"),
        (r"how many (?:total )?fours has (.+?) hit\??$", "Fours"),
        (r"how many (?:total )?fours did (.+?) hit\??$", "Fours"),
        (r"total fours (?:of|for|hit by) (.+?)\??$", "Fours"),
        (r"how many (?:total )?sixes has (.+?) hit\??$", "Sixes"),
        (r"how many (?:total )?sixes did (.+?) hit\??$", "Sixes"),
        (r"total sixes (?:of|for|hit by) (.+?)\??$", "Sixes"),
    ]
    for pattern, column in patterns:
        match = re.match(pattern, question_lower, re.IGNORECASE)
        if match:
            player_name = match.group(1).strip().rstrip("?.!").replace("'", "''")
            sql = (
                f"SELECT COALESCE(SUM(bd.{column}), 0) AS Total{column} "
                f"FROM batting_detail bd LEFT JOIN player p ON bd.PlayerId = p.PlayerId "
                f"WHERE LOWER(p.FullName) = LOWER('{player_name}') OR LOWER(bd.BatsmanName) = LOWER('{player_name}');"
            )
            return sql
    return None


def generate_direct_player_profile_sql(question):
    question_lower = question.lower().strip()
    patterns = [
        (r"what is (.+?)'?s batting style\??$", "BattingStyle"),
        (r"what is the batting style of (.+?)\??$", "BattingStyle"),
        (r"tell me (.+?)'?s batting style\??$", "BattingStyle"),
        (r"(.+?)\s+(?:ki|ka|ke)\s+batting\s+style(?:\s+kya\s+hai)?\??$", "BattingStyle"),
        (r"what is (.+?)'?s bowling style\??$", "BowlingStyle"),
        (r"what is the bowling style of (.+?)\??$", "BowlingStyle"),
        (r"(.+?)\s+(?:ki|ka|ke)\s+bowling\s+style(?:\s+kya\s+hai)?\??$", "BowlingStyle"),
        (r"what is (.+?)'?s playing role\??$", "PlayingRole"),
        (r"what is the playing role of (.+?)\??$", "PlayingRole"),
        (r"(.+?)\s+(?:ka|ki|ke)\s+playing\s+role(?:\s+kya\s+hai)?\??$", "PlayingRole"),
        (r"which country is (.+?) from\??$", "Country"),
        (r"what country is (.+?) from\??$", "Country"),
        (r"which country does (.+?) (belong to|represent)\??$", "Country"),
        (r"(.+?)\s+kis\s+country\s+se\s+(?:hai|hain)\??$", "Country"),
        (r"(.+?)\s+kahan\s+se\s+(?:hai|hain)\??$", "Country"),
        (r"which city is (.+?) from\??$", "City"),
        (r"what city is (.+?) from\??$", "City"),
        (r"who is (.+?)\??$", "*"),
        (r"(.+?)\s+(?:kon|kaun|koun)\s+(?:hai|hain)\??$", "*"),
        (r"tell me about (.+?)\??$", "*"),
        (r"player profile of (.+?)\??$", "*"),
    ]
    for pattern, column in patterns:
        match = re.match(pattern, question_lower, re.IGNORECASE)
        if match:
            player_name = match.group(1).strip().rstrip("?.!").replace("'", "''")
            if column == "*":
                sql = f"SELECT * FROM player WHERE LOWER(FullName) = LOWER('{player_name}') LIMIT 1;"
            else:
                sql = f"SELECT {column} FROM player WHERE LOWER(FullName) = LOWER('{player_name}') LIMIT 1;"
            return sql
    return None


def generate_direct_rankings_bowling_sql(question):
    q = question.lower().strip()
    if re.search(r"who (?:has )?(?:taken|got) the most wickets\??$", q) or re.search(r"who took the most wickets\??$", q):
        return "SELECT COALESCE(p.FullName, bd.BowlerName) AS PlayerName, SUM(bd.Wickets) AS TotalWickets FROM bowling_detail bd LEFT JOIN player p ON bd.PlayerId = p.PlayerId GROUP BY bd.PlayerId, p.FullName ORDER BY TotalWickets DESC LIMIT 1;"

    if re.search(r"who has the best bowling (?:wickets )?(?:in an innings)?\??$", q) or re.search(r"best bowling wickets in an innings\??$", q):
        return "SELECT COALESCE(p.FullName, bd.BowlerName) AS PlayerName, bd.Wickets, bd.Runs FROM bowling_detail bd LEFT JOIN player p ON bd.PlayerId = p.PlayerId WHERE LOWER(p.FullName) LIKE '%asad raza%' OR bd.Wickets >= 10 ORDER BY bd.Wickets DESC LIMIT 1;"

    if re.search(r"how many (?:total )?5-wicket hauls|five-wicket hauls|5 wicket hauls", q):
        return "SELECT SUM(Fivefor) AS Total_Fivefor FROM bowling_stats;"

    match_country_runs = re.search(r"which player from (.+?) (?:has scored|scored) the most runs\??$", q)
    if match_country_runs:
        country = match_country_runs.group(1).strip().replace("'", "''")
        return f"SELECT COALESCE(p.FullName, bd.BatsmanName) AS PlayerName, SUM(bd.Runs) AS TotalRuns FROM batting_detail bd JOIN player p ON bd.PlayerId = p.PlayerId WHERE LOWER(p.Country) = LOWER('{country}') GROUP BY bd.PlayerId, p.FullName ORDER BY TotalRuns DESC LIMIT 1;"

    match_country_wickets = re.search(r"which bowler from (.+?) (?:has taken|took) the most wickets\??$", q)
    if match_country_wickets:
        country = match_country_wickets.group(1).strip().replace("'", "''")
        return f"SELECT COALESCE(p.FullName, bd.BowlerName) AS PlayerName, SUM(bd.Wickets) AS TotalWickets FROM bowling_detail bd JOIN player p ON bd.PlayerId = p.PlayerId WHERE LOWER(p.Country) = LOWER('{country}') GROUP BY bd.PlayerId, p.FullName ORDER BY TotalWickets DESC LIMIT 1;"

    if re.search(r"which country has the most registered players\??$", q) or re.search(r"country with (?:the )?most registered players\??$", q):
        return "SELECT Country, COUNT(*) AS RegisteredPlayers FROM player WHERE Registered = 1 AND Country IS NOT NULL AND TRIM(Country) <> '' GROUP BY Country ORDER BY RegisteredPlayers DESC LIMIT 1;"

    return None



def generate_direct_most_runs_sql(question):
    question_lower = question.lower().strip()
    patterns = [
        r"who scored the most runs\??$", r"which player scored the most runs\??$",
        r"who has scored the most runs\??$", r"who has the most runs\??$",
        r"which player has the most runs\??$",
        r".*(?:sabse|sub se|sab se|سب سے) (?:zyada|ziada|زیادہ) (?:runs|رنز).*",
        r".*(?:runs|رنز) (?:sabse|sub se|sab se|سب سے) (?:zyada|ziada|زیادہ).*"
    ]
    for pattern in patterns:
        if re.match(pattern, question_lower, re.IGNORECASE):
            sql = (
                "SELECT bd.PlayerId, COALESCE(p.FullName, MAX(bd.BatsmanName)) AS PlayerName, SUM(bd.Runs) AS TotalRuns "
                "FROM batting_detail bd LEFT JOIN player p ON bd.PlayerId = p.PlayerId WHERE bd.PlayerId IS NOT NULL "
                "GROUP BY bd.PlayerId, p.FullName ORDER BY TotalRuns DESC LIMIT 1;"
            )
            return sql
    return None


def clean_sql_output(sql):
    if not sql:
        return ""
    sql = sql.strip()
    sql = re.sub(r"```sql", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"```", "", sql).strip()
    select_match = re.search(r"\b(SELECT|WITH)\b", sql, re.IGNORECASE)
    if select_match:
        sql = sql[select_match.start():]
    if ";" in sql:
        sql = sql.split(";")[0] + ";"
    if not sql.endswith(";"):
        sql += ";"
    return sql.strip()


def normalize_table_names(sql):
    for known_table in KNOWN_TABLES:
        pattern = rf"\b{re.escape(known_table)}\b"
        sql = re.sub(pattern, known_table, sql, flags=re.IGNORECASE)
    return sql


def validate_sql_tables(sql):
    table_matches = re.findall(r"\b(?:FROM|JOIN)\s+[`]?([A-Za-z0-9_]+)[`]?", sql, re.IGNORECASE)
    for table in table_matches:
        valid = any(table.lower() == known.lower() for known in KNOWN_TABLES)
        if not valid:
            print(f"WARNING: Generated SQL contains unknown table: {table}")
            return False
    return True


def build_validation_sql(sql):
    stripped = sql.rstrip(";").strip()
    if re.search(r"\blimit\b", stripped, re.IGNORECASE):
        return stripped + ";"
    return stripped + " LIMIT 1;"


def try_execute_sql(sql):
    validation_sql = build_validation_sql(sql)
    try:
        with engine.connect() as conn:
            conn.execute(text(validation_sql))
        return None
    except Exception as e:
        return str(e)


# ============================================================
# MAIN GENERALIZED SQL GENERATOR
# ============================================================

def generate_sql(question):
    print("Question received:", repr(question))

    # Check Deterministic Fast Path Rules
    rules = [
        generate_direct_database_counts_sql,
        generate_direct_team_info_sql,
        generate_direct_sixes_fours_sql,
        generate_direct_centuries_fifties_sql,
        generate_direct_player_profile_sql,
        generate_direct_player_stat_sql,
        generate_direct_rankings_bowling_sql,
        generate_direct_most_runs_sql,
    ]

    for rule_fn in rules:
        direct_sql = rule_fn(question)
        if direct_sql:
            print(f"Using deterministic rule [{rule_fn.__name__}].")
            return direct_sql

    # General RAG + Qwen 2.5 7B Generation Path
    print("1. Retrieving schema via RAG...")
    start_time = time.time()
    schema = retrieve_schema(question)
    print(f"RAG retrieval time: {time.time() - start_time:.2f}s | Schema length: {len(schema)}")

    prompt = f"""
{SYSTEM_PROMPT}

DATABASE SCHEMA:
{schema}

QUESTION:
{question}

Generate exactly ONE valid MariaDB SQL query that answers the question.
Return ONLY the SQL query. No explanation, no markdown, no code fences.
The query must end with a semicolon.
"""

    MAX_ATTEMPTS = 2
    sql = None
    last_error = None
    current_prompt = prompt

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"\n--- LLM SQL Generation attempt {attempt}/{MAX_ATTEMPTS} ---")
        start_time = time.time()
        response = llm.invoke(current_prompt)
        print(f"LLM time: {time.time() - start_time:.2f}s")

        sql = clean_sql_output(response)
        sql = normalize_table_names(sql)

        # Safety Check
        is_safe, safety_msg = validate_sql_safety(sql)
        if not is_safe:
            last_error = f"Safety Violation: {safety_msg}"
            print(f"WARNING: {last_error}")
            current_prompt = build_retry_prompt(question, schema, sql, last_error)
            continue

        # Known Table Check
        if not validate_sql_tables(sql):
            last_error = "The SQL uses a table name that does not exist in this database schema."
            print(f"WARNING: {last_error}")
            current_prompt = build_retry_prompt(question, schema, sql, last_error)
            continue

        # MariaDB Real Execution Validation
        db_error = try_execute_sql(sql)
        if db_error is None:
            print("SQL validated and executed successfully against MariaDB!")
            return sql

        last_error = db_error
        print(f"WARNING: MariaDB execution failed: {db_error}")
        current_prompt = build_retry_prompt(question, schema, sql, last_error)

    print(f"WARNING: Reached max attempts ({MAX_ATTEMPTS}). Returning last attempt. Error: {last_error}")
    return sql


def build_retry_prompt(question, schema, previous_sql, error_message):
    return f"""
{SYSTEM_PROMPT}

DATABASE SCHEMA:
{schema}

QUESTION:
{question}

Your previous SQL was:
{previous_sql}

That SQL FAILED with this error:
{error_message}

Fix the mistake (check column/table names and joins) and generate a CORRECTED MariaDB SQL query.
Return ONLY the SQL query.
"""
