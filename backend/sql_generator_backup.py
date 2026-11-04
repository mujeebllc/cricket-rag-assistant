import re
import time

from sqlalchemy import text

from langchain_ollama import OllamaLLM

from rag.retriever import retrieve_schema
from prompts.system_prompt import SYSTEM_PROMPT
from database.db import engine


# ============================================================
# LOAD LLM
# ============================================================

llm = OllamaLLM(
    model="qwen2.5:7b",
    temperature=0
)


# ============================================================
# KNOWN DATABASE TABLES
# ============================================================

KNOWN_TABLES = {
    "RECOVER_YOUR_DATA",
    "article",
    "article_group",
    "article_tags",
    "association",
    "ball_by_ball",
    "batting_detail",
    "batting_stats",
    "bowling_detail",
    "bowling_stats",
    "budget",
    "category",
    "city",
    "city_cricket_association",
    "club",
    "comment",
    "country",
    "cricket_association",
    "current_day",
    "department",
    "edition",
    "event",
    "fantasy_prediction",
    "fantasy_result",
    "fantasy_user",
    "feedback",
    "fow",
    "gallery",
    "ground",
    "group",
    "group_screen",
    "innings",
    "inreport",
    "live_ball_by_ball",
    "live_batting_detail",
    "live_bowling_detail",
    "live_fow",
    "live_innings",
    "live_match_over",
    "live_match_squad",
    "live_matches",
    "livescore",
    "match_comments",
    "match_over",
    "match_squad",
    "matches",
    "media_item",
    "news",
    "object_pics",
    "offer",
    "official",
    "outreport",
    "outreport_data",
    "photo",
    "player",
    "player_follower",
    "point_table",
    "points",
    "posts",
    "province",
    "region",
    "round_team",
    "scorer",
    "scorer_setup_sync_event",
    "scorer_tournament",
    "screen",
    "season",
    "section",
    "section_head",
    "squad",
    "sw_user",
    "tags",
    "team",
    "temp",
    "test_table",
    "tournament",
    "tournament_club",
    "tournament_round",
    "user_group",
    "users",
}


# ============================================================
# DIRECT PLAYER BATTING STATISTICS
#
# Handles:
# - How many runs has Babar Azam scored?
# - How many fours has Babar Azam hit?
# - How many sixes has Babar Azam hit?
# - How many balls has Babar Azam faced?
#
# These bypass RAG + LLM for speed and reliability.
# ============================================================

def generate_direct_player_stat_sql(question):

    question_lower = question.lower().strip()

    patterns = [

        # RUNS
        (r"how many runs has (.+?) scored\??$", "Runs", "Runs"),
        (r"how many runs did (.+?) score\??$", "Runs", "Runs"),
        (r"total runs (?:of|for) (.+?)\??$", "Runs", "Runs"),

        # FOURS
        (r"how many fours has (.+?) hit\??$", "Fours", "Fours"),
        (r"how many fours did (.+?) hit\??$", "Fours", "Fours"),
        (r"total fours (?:of|for) (.+?)\??$", "Fours", "Fours"),

        # SIXES
        (r"how many sixes has (.+?) hit\??$", "Sixes", "Sixes"),
        (r"how many sixes did (.+?) hit\??$", "Sixes", "Sixes"),
        (r"total sixes (?:of|for) (.+?)\??$", "Sixes", "Sixes"),

        # BALLS FACED
        (r"how many balls has (.+?) faced\??$", "BallsFaced", "BallsFaced"),
        (r"how many balls did (.+?) face\??$", "BallsFaced", "BallsFaced"),
        (r"total balls (?:faced|of|for) (.+?)\??$", "BallsFaced", "BallsFaced"),
    ]

    for pattern, column, alias in patterns:

        match = re.match(pattern, question_lower, re.IGNORECASE)

        if match:

            player_name = match.group(1).strip()
            player_name = player_name.rstrip("?.!")
            player_name_sql = player_name.replace("'", "''")

            # ========================================================
            # GENERIC DUPLICATE-NAME SOLUTION
            #
            # Every PlayerId is kept separate.
            # Different players with the same FullName are NOT merged.
            # ========================================================

            sql = (
                "SELECT "
                "p.PlayerId, "
                "p.FullName, "
                "p.PlayingRole, "
                "c.ClubName, "
                f"COALESCE(SUM(bs.{column}), 0) AS {alias} "
                "FROM player p "
                "LEFT JOIN club c "
                "ON p.ClubId = c.ClubId "
                "LEFT JOIN batting_stats bs "
                "ON bs.PlayerId = p.PlayerId "
                f"WHERE LOWER(p.FullName) = LOWER('{player_name_sql}') "
                "GROUP BY "
                "p.PlayerId, "
                "p.FullName, "
                "p.PlayingRole, "
                "c.ClubName "
                "ORDER BY p.PlayerId;"
            )

            print("\n========== DIRECT PLAYER STAT RULE ==========\n")
            print(f"Detected player: {player_name}")
            print(f"Requested field: {column}")
            print("Duplicate names will be kept as separate players.")
            print("Generated SQL:")
            print(sql)
            print("\n=============================================\n")

            return sql

    return None




# ============================================================
# DIRECT PLAYER BOWLING STATISTICS
#
# Handles:
# - How many wickets has Shaheen Afridi taken?
# - How many wickets did Shaheen Afridi take?
# - How many overs has X bowled?
# - How many maidens has X bowled?
# - What is X's economy rate?
# - How many runs has X conceded?
#
# Uses bowling_stats (season-wise aggregated), same pattern as the
# batting stat rule above, joined by PlayerId (not name text).
# ============================================================

def generate_direct_player_bowling_stat_sql(question):

    question_lower = question.lower().strip()

    patterns = [

        # WICKETS
        (r"how many wickets has (.+?) taken\??$", "Wickets", "Wickets"),
        (r"how many wickets did (.+?) take\??$", "Wickets", "Wickets"),
        (r"total wickets (?:of|for|taken by) (.+?)\??$", "Wickets", "Wickets"),

        # OVERS BOWLED (bowling_stats stores Balls, not Overs)
        (r"how many balls has (.+?) bowled\??$", "Balls", "Balls"),
        (r"how many balls did (.+?) bowl\??$", "Balls", "Balls"),

        # MAIDENS
        (r"how many maidens has (.+?) bowled\??$", "Fourfor", "Fourfor"),

        # RUNS CONCEDED
        (r"how many runs has (.+?) conceded\??$", "Runs", "RunsConceded"),
        (r"how many runs did (.+?) concede\??$", "Runs", "RunsConceded"),
        (r"total runs conceded by (.+?)\??$", "Runs", "RunsConceded"),

        # ECONOMY RATE
        (r"what is (.+?)'?s economy rate\??$", "Economy", "Economy"),
        (r"(.+?)'?s economy rate\??$", "Economy", "Economy"),

        # BOWLING AVERAGE
        (r"what is (.+?)'?s bowling average\??$", "Average", "BowlingAverage"),
    ]

    for pattern, column, alias in patterns:

        match = re.match(pattern, question_lower, re.IGNORECASE)

        if match:

            player_name = match.group(1).strip()
            player_name = player_name.rstrip("?.!")
            player_name_sql = player_name.replace("'", "''")

            # For rate-style columns (Economy, Average) summing across
            # seasons doesn't make sense - use a weighted aggregate
            # via SUM(Runs)/ (SUM(Balls)/6) instead of averaging the
            # per-season rate column directly.

            if column == "Economy":
                sql = (
                    "SELECT "
                    "p.PlayerId, "
                    "p.FullName, "
                    "c.ClubName, "
                    "ROUND(COALESCE(SUM(bs.Runs), 0) / "
                    "NULLIF(COALESCE(SUM(bs.Balls), 0) / 6, 0), 2) "
                    "AS Economy "
                    "FROM player p "
                    "LEFT JOIN club c "
                    "ON p.ClubId = c.ClubId "
                    "LEFT JOIN bowling_stats bs "
                    "ON bs.PlayerId = p.PlayerId "
                    f"WHERE LOWER(p.FullName) = LOWER('{player_name_sql}') "
                    "GROUP BY p.PlayerId, p.FullName, c.ClubName "
                    "ORDER BY p.PlayerId;"
                )

            elif column == "Average":
                sql = (
                    "SELECT "
                    "p.PlayerId, "
                    "p.FullName, "
                    "c.ClubName, "
                    "ROUND(COALESCE(SUM(bs.Runs), 0) / "
                    "NULLIF(COALESCE(SUM(bs.Wickets), 0), 0), 2) "
                    "AS BowlingAverage "
                    "FROM player p "
                    "LEFT JOIN club c "
                    "ON p.ClubId = c.ClubId "
                    "LEFT JOIN bowling_stats bs "
                    "ON bs.PlayerId = p.PlayerId "
                    f"WHERE LOWER(p.FullName) = LOWER('{player_name_sql}') "
                    "GROUP BY p.PlayerId, p.FullName, c.ClubName "
                    "ORDER BY p.PlayerId;"
                )

            else:
                sql = (
                    "SELECT "
                    "p.PlayerId, "
                    "p.FullName, "
                    "p.PlayingRole, "
                    "c.ClubName, "
                    f"COALESCE(SUM(bs.{column}), 0) AS {alias} "
                    "FROM player p "
                    "LEFT JOIN club c "
                    "ON p.ClubId = c.ClubId "
                    "LEFT JOIN bowling_stats bs "
                    "ON bs.PlayerId = p.PlayerId "
                    f"WHERE LOWER(p.FullName) = LOWER('{player_name_sql}') "
                    "GROUP BY "
                    "p.PlayerId, "
                    "p.FullName, "
                    "p.PlayingRole, "
                    "c.ClubName "
                    "ORDER BY p.PlayerId;"
                )

            print("\n========== DIRECT PLAYER BOWLING STAT RULE ==========\n")
            print(f"Detected player: {player_name}")
            print(f"Requested field: {column}")
            print("Duplicate names will be kept as separate players.")
            print("Generated SQL:")
            print(sql)
            print("\n======================================================\n")

            return sql

    return None


# ============================================================
# DIRECT PLAYER LIST BY COUNTRY
# ============================================================

def generate_direct_player_list_sql(question):

    question_lower = question.lower().strip()

    patterns = [
        r"list players from (.+?)\??$",
        r"show players from (.+?)\??$",
        r"which players are from (.+?)\??$",
        r"show me players from (.+?)\??$",
    ]

    for pattern in patterns:

        match = re.match(pattern, question_lower, re.IGNORECASE)

        if match:

            country_name = match.group(1).strip()
            country_name = country_name.rstrip("?.!")
            country_name_sql = country_name.replace("'", "''")

            sql = (
                "SELECT DISTINCT FullName "
                "FROM player "
                f"WHERE LOWER(Country) = LOWER('{country_name_sql}') "
                "AND FullName IS NOT NULL "
                "AND TRIM(FullName) <> '' "
                "ORDER BY FullName;"
            )

            print("\n========== DIRECT PLAYER LIST RULE ==========\n")
            print(f"Detected country: {country_name}")
            print(f"Generated SQL: {sql}")
            print("\n=============================================\n")

            return sql

    return None


# ============================================================
# DIRECT PLAYER COUNT BY COUNTRY
# ============================================================

def generate_direct_player_country_count_sql(question):

    question_lower = question.lower().strip()

    patterns = [
        r"how many players are from (.+?)\??$",
        r"how many players from (.+?)\??$",
        r"count players from (.+?)\??$",
    ]

    for pattern in patterns:

        match = re.match(pattern, question_lower, re.IGNORECASE)

        if match:

            country_name = match.group(1).strip()
            country_name = country_name.rstrip("?.!")
            country_name_sql = country_name.replace("'", "''")

            sql = (
                "SELECT COUNT(DISTINCT PlayerId) AS PlayerCount "
                "FROM player "
                f"WHERE LOWER(Country) = LOWER('{country_name_sql}') "
                "AND FullName IS NOT NULL "
                "AND TRIM(FullName) <> '';"
            )

            print("\n========== DIRECT PLAYER COUNTRY COUNT RULE ==========\n")
            print(f"Detected country: {country_name}")
            print(f"Generated SQL: {sql}")
            print("\n=======================================================\n")

            return sql

    return None


# ============================================================
# DIRECT PLAYER PROFILE
# ============================================================

def generate_direct_player_profile_sql(question):

    question_lower = question.lower().strip()

    patterns = [
    (r"what is (.+?)'?s batting style\??$", "BattingStyle"),
    (r"what is (.+?)'?s bowling style\??$", "BowlingStyle"),
    (r"what is (.+?)'?s playing role\??$", "PlayingRole"),
    (r"which country is (.+?) from\??$", "Country"),
    (r"what country is (.+?) from\??$", "Country"),
    (r"which city is (.+?) from\??$", "City"),
    (r"what city is (.+?) from\??$", "City"),
    (r"who is (.+?)\??$", "*"),
    (r"tell me about (.+?)\??$", "*"),
    (r"player profile of (.+?)\??$", "*"),
]

    for pattern, column in patterns:

        match = re.match(pattern, question_lower, re.IGNORECASE)

        if match:

            player_name = match.group(1).strip()
            player_name = player_name.rstrip("?.!")
            player_name_sql = player_name.replace("'", "''")

            if column == "*":

                sql = (
                    "SELECT * "
                    "FROM player "
                    f"WHERE LOWER(FullName) = LOWER('{player_name_sql}') "
                    "LIMIT 1;"
                )

            else:

                sql = (
                    f"SELECT {column} "
                    "FROM player "
                    f"WHERE LOWER(FullName) = LOWER('{player_name_sql}') "
                    "LIMIT 1;"
                )

            print("\n========== DIRECT PLAYER PROFILE RULE ==========\n")
            print(f"Detected player: {player_name}")
            print(f"Requested field: {column}")
            print(f"Generated SQL: {sql}")
            print("\n================================================\n")

            return sql

    return None


# ============================================================
# DIRECT PLAYER STATISTICS
# ============================================================

def generate_direct_player_seasons_sql(question):

    question_lower = question.lower().strip()

    patterns = [
        r"what batting seasons are available for (.+?)\??$",
        r"what are (.+?)'?s batting seasons\??$",
        r"show batting seasons of (.+?)\??$",
        r"list batting seasons of (.+?)\??$",
        r"batting seasons of (.+?)\??$",
    ]

    for pattern in patterns:

        match = re.match(pattern, question_lower, re.IGNORECASE)

        if match:

            player_name = match.group(1).strip()
            player_name = player_name.rstrip("?.!")
            player_name_sql = player_name.replace("'", "''")

            sql = (
                "SELECT DISTINCT bs.Season "
                "FROM batting_stats bs "
                "JOIN player p "
                "ON bs.PlayerId = p.PlayerId "
                f"WHERE LOWER(p.FullName) = LOWER('{player_name_sql}') "
                "ORDER BY bs.Season;"
            )

            print("\n========== DIRECT PLAYER SEASONS RULE ==========\n")
            print(f"Detected player: {player_name}")
            print(f"Generated SQL: {sql}")
            print("\n===============================================\n")

            return sql

    return None


# ============================================================
# DIRECT MOST RUNS
#
# FIX: Previously grouped by BatsmanName (a free-text column),
# which splits the same real player's runs across multiple rows
# whenever the name was entered with a different spelling,
# spacing, or capitalization in different matches. This produced
# incorrect / inconsistent totals compared to manually checking
# the database.
#
# Now we group by PlayerId (a stable numeric identifier) and only
# use the name for display purposes.
# ============================================================

def generate_direct_most_runs_sql(question):

    question_lower = question.lower().strip()

    patterns = [
        r"who scored the most runs\??$",
        r"which player scored the most runs\??$",
        r"who has scored the most runs\??$",
        r"who has the most runs\??$",
        r"which player has the most runs\??$",
        # Roman Urdu & Urdu script
        r".*(?:sabse|sub se|sab se|سب سے) (?:zyada|ziada|زیادہ) (?:runs|رنز).*",
        r".*(?:runs|رنز) (?:sabse|sub se|sab se|سب سے) (?:zyada|ziada|زیادہ).*",
    ]

    for pattern in patterns:

        if re.match(pattern, question_lower, re.IGNORECASE):

            sql = (
                "SELECT "
                "bd.PlayerId, "
                "COALESCE(p.FullName, MAX(bd.BatsmanName)) AS PlayerName, "
                "SUM(bd.Runs) AS TotalRuns "
                "FROM batting_detail bd "
                "LEFT JOIN player p "
                "ON bd.PlayerId = p.PlayerId "
                "WHERE bd.PlayerId IS NOT NULL "
                "GROUP BY bd.PlayerId, p.FullName "
                "ORDER BY TotalRuns DESC "
                "LIMIT 1;"
            )

            print("\n========== DIRECT MOST RUNS RULE ==========\n")
            print("Grouping by PlayerId (not BatsmanName) to avoid")
            print("splitting one player's runs across name variants.")
            print(f"Generated SQL: {sql}")
            print("\n============================================\n")

            return sql

    return None


# ============================================================
# DIRECT MOST MATCH WINS
#
# FIX: Previously grouped by WinnerName (a free-text column),
# which splits the same real team's wins across multiple rows
# whenever the team name was entered with a different spelling,
# spacing, or capitalization in different matches. This produced
# incorrect / inconsistent totals compared to manually checking
# the database.
#
# Now we group by the Winner column (the team's numeric ID) and
# only use the name for display purposes.
# ============================================================

def generate_direct_most_wins_sql(question):

    question_lower = question.lower().strip()

    patterns = [
        r"which team won the most matches\??$",
        r"which team has won the most matches\??$",
        r"who won the most matches\??$",
        r"which team has the most wins\??$",
        r"who has the most wins\??$",
        r".*(?:sabse|sub se|sab se|سب سے) (?:zyada|ziada|زیادہ) (?:matches|wins|میچز).*",
        r".*matches (?:sabse|sub se|sab se|سب سے) (?:zyada|ziada|زیادہ).*",
    ]

    for pattern in patterns:

        if re.match(pattern, question_lower, re.IGNORECASE):

            sql = (
                "SELECT "
                "m.Winner AS TeamId, "
                "COALESCE(t.TeamName, MAX(m.WinnerName)) AS TeamName, "
                "COUNT(*) AS MatchWins "
                "FROM matches m "
                "LEFT JOIN team t "
                "ON m.Winner = t.TeamId "
                "WHERE m.Winner IS NOT NULL "
                "GROUP BY m.Winner, t.TeamName "
                "ORDER BY MatchWins DESC "
                "LIMIT 1;"
            )

            print("\n========== DIRECT MOST WINS RULE ==========\n")
            print("Grouping by Winner TeamId (not WinnerName) to avoid")
            print("splitting one team's wins across name variants.")
            print(f"Generated SQL: {sql}")
            print("\n============================================\n")

            return sql

    return None


# ============================================================
# DIRECT MOST WICKETS
#
# Same fix pattern as "most runs" / "most wins": group by PlayerId
# (a stable numeric identifier) instead of BowlerName (free text),
# to avoid splitting one player's wickets across name variants.
# ============================================================

def generate_direct_most_wickets_sql(question):

    question_lower = question.lower().strip()

    patterns = [
        r"who has taken the most wickets\??$",
        r"which player has taken the most wickets\??$",
        r"who took the most wickets\??$",
        r"which player has the most wickets\??$",
        r"who has the most wickets\??$",
        r".*(?:sabse|sub se|sab se|سب سے) (?:zyada|ziada|زیادہ) (?:wickets|wicketein|وکٹیں|وکٹ).*",
        r".*(?:wickets|wicketein|وکٹیں) (?:sabse|sub se|sab se|سب سے) (?:zyada|ziada|زیادہ).*",
    ]

    for pattern in patterns:

        if re.match(pattern, question_lower, re.IGNORECASE):

            sql = (
                "SELECT "
                "bd.PlayerId, "
                "COALESCE(p.FullName, MAX(bd.BowlerName)) AS PlayerName, "
                "SUM(bd.Wickets) AS TotalWickets "
                "FROM bowling_detail bd "
                "LEFT JOIN player p "
                "ON bd.PlayerId = p.PlayerId "
                "WHERE bd.PlayerId IS NOT NULL "
                "GROUP BY bd.PlayerId, p.FullName "
                "ORDER BY TotalWickets DESC "
                "LIMIT 1;"
            )

            print("\n========== DIRECT MOST WICKETS RULE ==========\n")
            print("Grouping by PlayerId (not BowlerName) to avoid")
            print("splitting one player's wickets across name variants.")
            print(f"Generated SQL: {sql}")
            print("\n===============================================\n")

            return sql

    return None


# ============================================================
# DIRECT BEST BOWLING FIGURES
#
# Handles:
# - Who has the best bowling figures?
# - What is the best bowling figure in a single innings?
#
# "Best" bowling = most wickets first, then fewest runs conceded
# as the tiebreaker (standard cricket convention).
# ============================================================

def generate_direct_best_bowling_figures_sql(question):

    question_lower = question.lower().strip()

    patterns = [
        r"who has the best bowling figures\??$",
        r"what is the best bowling figure(?:s)? (?:in a single innings)?\??$",
        r"which player has the best bowling figures\??$",
        r"who took the best bowling figures\??$",
    ]

    for pattern in patterns:

        if re.match(pattern, question_lower, re.IGNORECASE):

            sql = (
                "SELECT "
                "bd.PlayerId, "
                "COALESCE(p.FullName, bd.BowlerName) AS PlayerName, "
                "bd.MatchNo, "
                "bd.Innings, "
                "bd.Wickets, "
                "bd.Runs AS RunsConceded "
                "FROM bowling_detail bd "
                "LEFT JOIN player p "
                "ON bd.PlayerId = p.PlayerId "
                "WHERE bd.Wickets IS NOT NULL "
                "ORDER BY bd.Wickets DESC, bd.Runs ASC "
                "LIMIT 1;"
            )

            print("\n========== DIRECT BEST BOWLING FIGURES RULE ==========\n")
            print("Generated SQL:")
            print(sql)
            print("\n=======================================================\n")

            return sql

    return None


# ============================================================
# DIRECT TOURNAMENT START DATE
#
# Handles:
# - Which tournament started on 2016-02-04?
# - What tournament started on 2016-02-04?
# - Which tournament began on 2016-02-04?
# - What tournament began on 2016-02-04?
# ============================================================

def generate_direct_tournament_start_sql(question):

    question_lower = question.lower().strip()

    patterns = [
        r"which tournament started on (\d{4}-\d{2}-\d{2})\??$",
        r"what tournament started on (\d{4}-\d{2}-\d{2})\??$",
        r"which tournament began on (\d{4}-\d{2}-\d{2})\??$",
        r"what tournament began on (\d{4}-\d{2}-\d{2})\??$",
    ]

    for pattern in patterns:

        match = re.match(pattern, question_lower, re.IGNORECASE)

        if match:

            start_date = match.group(1)

            sql = (
                "SELECT Name "
                "FROM tournament "
                f"WHERE DATE(StartDate) = '{start_date}' "
                "ORDER BY Name;"
            )

            print("\n========== DIRECT TOURNAMENT START DATE RULE ==========\n")
            print(f"Detected start date: {start_date}")
            print(f"Generated SQL: {sql}")
            print("\n========================================================\n")

            return sql

    return None


# ============================================================
# DIRECT HIGHEST INDIVIDUAL SCORE
#
# Handles:
# - Who scored the highest individual score?
# - Which player scored the highest individual score?
# - What is the highest individual score?
#
# Uses batting_detail because Runs represents
# the player's score in a single innings.
# ============================================================

def generate_direct_highest_individual_score_sql(question):

    question_lower = question.lower().strip()

    patterns = [
        r"who scored the highest individual score\??$",
        r"which player scored the highest individual score\??$",
        r"who has the highest individual score\??$",
        r"what is the highest individual score\??$",
        r"which player has the highest individual score\??$",
    ]

    for pattern in patterns:

        if re.match(pattern, question_lower, re.IGNORECASE):

            sql = (
                "SELECT "
                "bd.PlayerId, "
                "COALESCE(p.FullName, bd.BatsmanName) AS PlayerName, "
                "bd.MatchNo, "
                "bd.Innings, "
                "bd.Runs AS IndividualScore "
                "FROM batting_detail bd "
                "LEFT JOIN player p "
                "ON bd.PlayerId = p.PlayerId "
                "WHERE bd.Runs IS NOT NULL "
                "ORDER BY bd.Runs DESC "
                "LIMIT 1;"
            )

            print("\n========== DIRECT HIGHEST INDIVIDUAL SCORE RULE ==========\n")
            print("Generated SQL:")
            print(sql)
            print("\n===========================================================\n")

            return sql

    return None


# ============================================================
# DIRECT SIMPLE ENTITY COUNT / LIST
#
# NEW: Handles simple "how many X are there" / "show/list all X"
# questions for base entities (teams, tournaments, clubs).
#
# WHY THIS WAS ADDED:
# Without this deterministic rule, these simple questions were
# going through the RAG + LLM path, where the LLM would sometimes
# pick the wrong table (e.g. round_team or tournament_club instead
# of team/tournament), producing an incorrect total that did not
# match a manual check in MariaDB.
#
# This only handles the SIMPLE case (no filters). Anything more
# complex (e.g. "how many teams are in the Rawalpindi region")
# still falls through to the LLM/RAG path below.
# ============================================================

ENTITY_TABLE_CONFIG = {
    "team": {
        "table": "team",
        "trigger_words": ["team", "teams", "teamen", "teamein", "ٹیم", "ٹیمیں", "ٹیموں"],
    },
    "tournament": {
        "table": "tournament",
        "trigger_words": ["tournament", "tournaments", "ٹورنامنٹ", "ٹورنامنٹس"],
    },
    "club": {
        "table": "club",
        "trigger_words": ["club", "clubs", "کلب", "کلبوں"],
    },
    "player": {
        "table": "player",
        "trigger_words": ["player", "players", "khiladi", "khilari", "کھلاڑی", "کھلاڑیوں"],
    },
}

# Words that indicate the question is NOT a simple count/list and
# needs real filtering/joining logic, so we should NOT short-circuit.
# NOTE: "player"/"players" are intentionally NOT here anymore -
# this rule only fires when the question ends in "... are there?"
# (see is_count_question below), so plain "How many players are
# there?" is safe, while player-specific questions like "how many
# players scored 50 or more" or "how many players are from
# Pakistan" never match that strict ending and fall through to
# their own dedicated rules instead.
DISQUALIFYING_WORDS = [
    "region", "province", "district", "department", "season",
    "format", "level", "stage", "won", "win", "wins", "lost",
    "match", "matches", "from", "in ",
    "with", "where", "captain", "coach",
]


def generate_direct_entity_count_or_list_sql(question):

    question_lower = question.lower().strip()

    # Only handle very simple phrasing - if the question has extra
    # filtering words, let the LLM handle it instead.
    if any(word in question_lower for word in DISQUALIFYING_WORDS):
        return None

    is_count_question = bool(
        re.search(r"how many .*\bare there\??$", question_lower)
        or re.search(r"^count\b", question_lower)
        or re.search(r"\b(kitni|kitne|kitna)\b", question_lower)
        or re.search(r"(کتنی|کتنے|تعداد)", question_lower)
    )

    is_list_question = bool(
        re.search(r"^(show|list)\b", question_lower)
        or re.search(r"^(بتاو|دکھاؤ)\b", question_lower)
    )

    if not (is_count_question or is_list_question):
        return None

    for entity_key, config in ENTITY_TABLE_CONFIG.items():

        table = config["table"]

        if any(
            re.search(rf"\b{re.escape(word)}\b", question_lower)
            for word in config["trigger_words"]
        ):

            if is_count_question:
                sql = f"SELECT COUNT(*) AS Total FROM {table};"
            else:
                sql = f"SELECT * FROM {table};"

            print("\n========== DIRECT ENTITY COUNT/LIST RULE ==========\n")
            print(f"Detected entity: {entity_key} -> table: {table}")
            print(f"Generated SQL: {sql}")
            print("\n====================================================\n")

            return sql

    return None


# ============================================================
# DIRECT CENTURY / FIFTY / RUNS-THRESHOLD QUESTIONS
#
# All of these are based on a single innings' Runs value in
# batting_detail (the per-match batting record), NOT batting_stats
# (which is season-aggregated and not suitable for "in one innings"
# questions).
#
# Handles:
# - How many players have scored at least one century?
# - How many centuries were scored in total?
# - How many fifties were scored in total?
# - Which player scored the most centuries?
# - How many players scored 200 or more?   (any threshold number)
# - How many players scored 50 or more?
# ============================================================

def generate_direct_century_fifty_sql(question):

    q = question.lower().strip()

    # ---- How many players have scored at least one century? ----
    if re.match(
        r"how many players have scored at least one century\??$", q
    ):
        sql = (
            "SELECT COUNT(DISTINCT PlayerId) AS PlayerCount "
            "FROM batting_detail "
            "WHERE Runs >= 100;"
        )
        print("\n========== DIRECT CENTURY PLAYER COUNT RULE ==========\n")
        print(f"Generated SQL: {sql}")
        print("\n=======================================================\n")
        return sql

    # ---- How many players scored <N> or more? (generic threshold) ----
    match = re.match(
        r"how many players (?:have )?scored (\d+) or more\??$", q
    )
    if match:
        threshold = int(match.group(1))
        sql = (
            "SELECT COUNT(DISTINCT PlayerId) AS PlayerCount "
            "FROM batting_detail "
            f"WHERE Runs >= {threshold};"
        )
        print("\n========== DIRECT RUNS-THRESHOLD PLAYER COUNT RULE ==========\n")
        print(f"Detected threshold: {threshold}")
        print(f"Generated SQL: {sql}")
        print("\n===============================================================\n")
        return sql

    # ---- How many centuries were scored in total? ----
    if re.match(
        r"how many centuries were scored(?: in total)?\??$", q
    ):
        sql = (
            "SELECT COUNT(*) AS CenturyCount "
            "FROM batting_detail "
            "WHERE Runs >= 100;"
        )
        print("\n========== DIRECT TOTAL CENTURIES RULE ==========\n")
        print(f"Generated SQL: {sql}")
        print("\n===================================================\n")
        return sql

    # ---- How many fifties were scored in total? ----
    # (A "fifty" conventionally means 50-99 runs; 100+ counts as a
    # century instead, so it is excluded here to avoid double
    # counting the same innings in both totals.)
    if re.match(
        r"how many fifties were scored(?: in total)?\??$", q
    ):
        sql = (
            "SELECT COUNT(*) AS FiftyCount "
            "FROM batting_detail "
            "WHERE Runs >= 50 AND Runs < 100;"
        )
        print("\n========== DIRECT TOTAL FIFTIES RULE ==========\n")
        print(f"Generated SQL: {sql}")
        print("\n=================================================\n")
        return sql

    # ---- Which player scored the most centuries? ----
    if re.match(
        r"(which player|who) scored the most centuries\??$", q
    ):
        sql = (
            "SELECT "
            "bd.PlayerId, "
            "COALESCE(p.FullName, MAX(bd.BatsmanName)) AS PlayerName, "
            "COUNT(*) AS Centuries "
            "FROM batting_detail bd "
            "LEFT JOIN player p "
            "ON bd.PlayerId = p.PlayerId "
            "WHERE bd.Runs >= 100 "
            "GROUP BY bd.PlayerId, p.FullName "
            "ORDER BY Centuries DESC "
            "LIMIT 1;"
        )
        print("\n========== DIRECT MOST CENTURIES RULE ==========\n")
        print(f"Generated SQL: {sql}")
        print("\n==================================================\n")
        return sql

    return None

def clean_sql_output(sql):

    if not sql:
        return ""

    sql = sql.strip()

    # Remove markdown code fences
    sql = re.sub(r"```sql", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"```", "", sql)
    sql = sql.strip()

    # If LLM added explanation before SQL,
    # keep only from SELECT or WITH onward.
    select_match = re.search(r"\b(SELECT|WITH)\b", sql, re.IGNORECASE)

    if select_match:
        sql = sql[select_match.start():]

    # Keep only first SQL statement
    if ";" in sql:
        sql = sql.split(";")[0] + ";"

    # Ensure semicolon
    if not sql.endswith(";"):
        sql += ";"

    return sql.strip()


def normalize_table_names(sql):
    for known_table in KNOWN_TABLES:
        pattern = rf"\b{re.escape(known_table)}\b"
        sql = re.sub(
            pattern,
            known_table,
            sql,
            flags=re.IGNORECASE
        )

    return sql

# ============================================================
# VALIDATE TABLES IN GENERATED SQL
# ============================================================

def validate_sql_tables(sql):

    table_matches = re.findall(
        r"\b(?:FROM|JOIN)\s+[`]?([A-Za-z0-9_]+)[`]?",
        sql,
        re.IGNORECASE
    )

    for table in table_matches:

        valid = any(
            table.lower() == known.lower()
            for known in KNOWN_TABLES
        )

        if not valid:
            print(
                f"WARNING: Generated SQL contains unknown table: {table}"
            )
            return False

    return True


# ============================================================
# MAIN SQL GENERATOR
# ============================================================

def generate_sql(question):

    print("Question received:", repr(question))

    # ========================================================
    # STEP 1: DIRECT PLAYER STATISTICS
    # ========================================================

    direct_sql = generate_direct_player_stat_sql(question)

    if direct_sql:
        print("Using deterministic player-stat SQL.")
        return direct_sql

    # ========================================================
    # STEP 1B: DIRECT PLAYER BOWLING STATISTICS
    # ========================================================

    direct_bowling_sql = generate_direct_player_bowling_stat_sql(question)

    if direct_bowling_sql:
        print("Using deterministic player-bowling-stat SQL.")
        return direct_bowling_sql

    # ========================================================
    # STEP 2: DIRECT PLAYER LIST
    # ========================================================

    direct_player_list_sql = generate_direct_player_list_sql(question)

    if direct_player_list_sql:
        print("Using deterministic player-list SQL.")
        return direct_player_list_sql

    # ========================================================
    # STEP 3: DIRECT PLAYER COUNT BY COUNTRY
    # ========================================================

    direct_country_count_sql = generate_direct_player_country_count_sql(
        question
    )

    if direct_country_count_sql:
        print("Using deterministic player-country-count SQL.")
        return direct_country_count_sql

    # ========================================================
    # STEP 4: DIRECT PLAYER PROFILE
    # ========================================================

    direct_player_profile_sql = generate_direct_player_profile_sql(question)

    if direct_player_profile_sql:
        print("Using deterministic player-profile SQL.")
        return direct_player_profile_sql


   # ========================================================
   # STEP 5: DIRECT PLAYER SEASONS
   # ========================================================

    direct_player_seasons_sql = generate_direct_player_seasons_sql(question)

    if direct_player_seasons_sql:
        print("Using deterministic player-seasons SQL.")
        return direct_player_seasons_sql



    # ========================================================
    # STEP 5: DIRECT HIGHEST INDIVIDUAL SCORE
    # ========================================================
    direct_highest_score_sql = generate_direct_highest_individual_score_sql(question)

    if direct_highest_score_sql:
        print("Using deterministic highest-individual-score SQL.")
        return direct_highest_score_sql

    # ========================================================
    # STEP 6: DIRECT MOST RUNS
    # ========================================================

    direct_most_runs_sql = generate_direct_most_runs_sql(question)

    if direct_most_runs_sql:
        print("Using deterministic most-runs SQL.")
        return direct_most_runs_sql

    # ========================================================
    # STEP 7: DIRECT MOST MATCH WINS
    # ========================================================

    direct_most_wins_sql = generate_direct_most_wins_sql(question)

    if direct_most_wins_sql:
        print("Using deterministic most-wins SQL.")
        return direct_most_wins_sql

    # ========================================================
    # STEP 7B: DIRECT MOST WICKETS
    # ========================================================

    direct_most_wickets_sql = generate_direct_most_wickets_sql(question)

    if direct_most_wickets_sql:
        print("Using deterministic most-wickets SQL.")
        return direct_most_wickets_sql

    # ========================================================
    # STEP 7C: DIRECT BEST BOWLING FIGURES
    # ========================================================

    direct_best_bowling_sql = generate_direct_best_bowling_figures_sql(question)

    if direct_best_bowling_sql:
        print("Using deterministic best-bowling-figures SQL.")
        return direct_best_bowling_sql

    # ========================================================
    # STEP 7D: DIRECT CENTURY / FIFTY / RUNS-THRESHOLD RULE
    # ========================================================

    direct_century_fifty_sql = generate_direct_century_fifty_sql(question)

    if direct_century_fifty_sql:
        print("Using deterministic century/fifty/threshold SQL.")
        return direct_century_fifty_sql

    # ========================================================
    # STEP 8: DIRECT TOURNAMENT START DATE
    # ========================================================

    direct_tournament_start_sql = generate_direct_tournament_start_sql(
        question
    )

    if direct_tournament_start_sql:
        print("Using deterministic tournament-start-date SQL.")
        return direct_tournament_start_sql

    # ========================================================
    # STEP 8.5: DIRECT SIMPLE ENTITY COUNT / LIST
    # (team / tournament / club - no filters)
    # ========================================================

    direct_entity_sql = generate_direct_entity_count_or_list_sql(question)

    if direct_entity_sql:
        print("Using deterministic entity count/list SQL.")
        return direct_entity_sql

    # ========================================================
    # STEP 9: RAG RETRIEVAL
    # ========================================================

    print("1. Retrieving schema...")

    start_time = time.time()
    schema = retrieve_schema(question)
    retrieval_time = time.time() - start_time

    print(f"RAG retrieval time: {retrieval_time:.2f} seconds")
    print(f"Schema length: {len(schema)}")

    # ========================================================
    # STEP 10: SHOW SCHEMA PREVIEW
    # ========================================================

    print("\n========== FIRST 1000 CHARACTERS OF SCHEMA ==========\n")
    print(schema[:1000])
    print("\n=====================================================\n")

    # ========================================================
    # STEP 11: BUILD PROMPT (with grounded few-shot examples)
    # ========================================================

    prompt = f"""
{SYSTEM_PROMPT}

DATABASE SCHEMA (only these tables/columns exist - do not use anything else):
{schema}

QUESTION:
{question}

Generate exactly ONE valid MariaDB SQL query that answers the question.
Return ONLY the SQL query. No explanation, no markdown, no code fences.
The query must end with a semicolon.
"""

    print("3. Prompt ready")
    print(f"Prompt length: {len(prompt)}")

    # ========================================================
    # STEP 12-14: SELF-CORRECTING GENERATE -> VALIDATE -> EXECUTE
    #             LOOP
    #
    # Instead of hoping the LLM gets it right on the first try (and
    # hoping we thought to write a rule for every possible phrasing),
    # we actually TEST the generated SQL against the real database.
    # If it fails (unknown column, unknown table, syntax error,
    # ambiguous join, etc.) we feed the REAL database error message
    # back to the LLM and ask it to fix its own mistake. This makes
    # the fallback path self-healing and works for ANY question
    # phrasing, not just ones we anticipated.
    # ========================================================

    MAX_ATTEMPTS = 3
    sql = None
    last_error = None
    current_prompt = prompt

    for attempt in range(1, MAX_ATTEMPTS + 1):

        print(f"\n--- LLM SQL generation attempt {attempt}/{MAX_ATTEMPTS} ---")

        start_time = time.time()
        response = llm.invoke(current_prompt)
        llm_time = time.time() - start_time

        print(f"LLM generation time: {llm_time:.2f} seconds")

        sql = clean_sql_output(response)
        sql = normalize_table_names(sql)

        # ---- Check 1: does it only reference known tables? ----
        if not validate_sql_tables(sql):

            last_error = (
                "The SQL uses a table name that does not exist in "
                "this database. Only use tables from the schema "
                "provided."
            )

            print(f"WARNING: {last_error}")
            print(f"Rejected SQL: {sql}")

            current_prompt = build_retry_prompt(
                question, schema, sql, last_error
            )
            continue

        # ---- Check 2: does it actually execute against the real DB? ----
        db_error = try_execute_sql(sql)

        if db_error is None:
            print("SQL executed successfully against the database.")
            return sql

        last_error = db_error
        print(f"WARNING: SQL failed against the real database: {db_error}")
        print(f"Rejected SQL: {sql}")

        current_prompt = build_retry_prompt(
            question, schema, sql, last_error
        )

    # ========================================================
    # STEP 15: RETURN SQL
    #
    # If we ran out of attempts, return the last attempt anyway
    # (graph_chatbot.py's execute_node will surface the real error
    # to the user rather than silently failing here), but at least
    # we tried multiple self-corrections first.
    # ========================================================

    print(
        f"WARNING: Reached max attempts ({MAX_ATTEMPTS}) without a "
        f"validated query. Returning last attempt. Last error: "
        f"{last_error}"
    )

    return sql


def build_retry_prompt(question, schema, previous_sql, error_message):
    """
    Build a retry prompt that includes the REAL error MariaDB gave us,
    so the LLM can see exactly what went wrong and fix it - this is
    what makes the fallback generic instead of needing a hand-written
    rule for every possible question.
    """

    return f"""
{SYSTEM_PROMPT}

DATABASE SCHEMA (only these tables/columns exist - do not use anything else):
{schema}

QUESTION:
{question}

Your previous SQL was:
{previous_sql}

That SQL FAILED with this real database error:
{error_message}

Look carefully at the schema above and the error message. Common causes:
- A column name that does not exist in that table (check the schema
  for the correct column, it may be in a DIFFERENT table than you
  used - e.g. per-match stats live in batting_detail/bowling_detail,
  not in matches or innings).
- A table name that does not exist.
- A JOIN condition using the wrong column.

Generate a CORRECTED, complete MariaDB SQL query that fixes this
specific error. Return ONLY the SQL query. No explanation, no
markdown, no code fences. The query must end with a semicolon.
"""


def build_validation_sql(sql):
    """
    Build a cheap, safe version of the query purely to test whether
    it executes without error. We cap it at 1 row so validating a
    query that would otherwise scan/return thousands of rows is fast.
    We don't care about the actual data here, only whether MariaDB
    accepts the query.
    """

    stripped = sql.rstrip(";").strip()

    if re.search(r"\blimit\b", stripped, re.IGNORECASE):
        return stripped + ";"

    return stripped + " LIMIT 1;"


def try_execute_sql(sql):
    """
    Actually run the SQL against the real database to check it is
    valid. Returns None if it succeeded, or the error message
    (string) if it failed. This is what lets the system catch
    mistakes like 'Unknown column Runs in innings' automatically,
    for ANY question, without us having to anticipate it.
    """

    validation_sql = build_validation_sql(sql)

    try:
        with engine.connect() as conn:
            conn.execute(text(validation_sql))
        return None

    except Exception as e:
        return str(e)
