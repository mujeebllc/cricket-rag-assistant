import re
import time

from langchain_ollama import OllamaLLM

from rag.retriever import retrieve_schema
from prompts.system_prompt import SYSTEM_PROMPT
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


from sql_generator import generate_sql

