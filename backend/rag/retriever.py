import re
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")
model = SentenceTransformer("BAAI/bge-m3")
print("Embedding model loaded!")

# ============================================================
# CONNECT TO QDRANT
# ============================================================

client = QdrantClient(host="localhost", port=6333)
COLLECTION_NAME = "cricket_schema"


def get_table_name(filename):
    name = filename.replace(".txt", "")
    name = re.sub(r"_\d+$", "", name)
    return name.lower()


def is_file_retrieved(retrieved_points, target_file):
    for point in retrieved_points:
        if point.payload.get("file") == target_file:
            return True
    return False


def find_schema_file(filename):
    try:
        offset = None
        while True:
            points, next_offset = client.scroll(
                collection_name=COLLECTION_NAME,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )
            for point in points:
                if point.payload.get("file") == filename:
                    return point
            if next_offset is None:
                break
            offset = next_offset
    except Exception as e:
        print(f"Warning: Could not find {filename}: {e}")
    return None


def detect_query_dependencies(question):
    """
    Generalized schema dependency detection supporting English, Urdu script, and Roman Urdu.
    Maps canonical intent and entity keywords to core required schema files.
    """
    q = question.lower().strip()
    required_files = []

    def add_dep(filename):
        if filename not in required_files:
            required_files.append(filename)

    # 1. Match / Wins / Victories (Requires matches.txt, team.txt)
    match_win_keywords = [
        "win", "wins", "won", "winning", "victory", "victories", "match", "matches", "game", "games",
        "jeeta", "jeete", "jita", "jeet", "jeeti", "muqabla", "sab se zyada", "sub se zyada",
        "جیت", "جیتے", "جیتا", "جیتیں", "میچ", "میچز", "مقابلہ"
    ]
    if any(kw in q for kw in match_win_keywords):
        add_dep("matches.txt")
        add_dep("team.txt")

    # 2. Batting / Runs / Scores (Requires batting_detail.txt, player.txt)
    batting_keywords = [
        "run", "runs", "score", "scored", "batsman", "batter", "batting", "century", "centuries",
        "fifty", "fifties", "banaye", "banai", "banaye hain",
        "رنز", "رن", "بنائے", "سکور", "بلے باز", "سنچری", "پچاس"
    ]
    if any(kw in q for kw in batting_keywords):
        add_dep("batting_detail.txt")
        add_dep("player.txt")

    # 3. Bowling / Wickets (Requires bowling_detail.txt, player.txt)
    bowling_keywords = [
        "wicket", "wickets", "bowler", "bowling", "taken", "conceded", "economy", "overs", "maidens",
        "wicketein", "li", "li hain",
        "وکٹ", "وکٹیں", "باؤلر", "بولنگ", "لی", "لی ہیں"
    ]
    if any(kw in q for kw in bowling_keywords):
        add_dep("bowling_detail.txt")
        add_dep("player.txt")

    # 4. Tournament Participation & Metadata (Requires tournament.txt, team.txt)
    tournament_keywords = [
        "tournament", "tournaments", "participated", "participation", "shamil", "shamil hui", "shamil huin", "began", "started",
        "ٹورنامنٹ", "ٹورنامنٹس", "شامل"
    ]
    if any(kw in q for kw in tournament_keywords):
        add_dep("tournament.txt")
        add_dep("team.txt")

    # 5. Players entity
    player_keywords = [
        "player", "players", "khiladi", "khilari", "کھلاڑی", "کھلاڑیوں"
    ]
    if any(kw in q for kw in player_keywords):
        add_dep("player.txt")

    # 6. Team entity
    team_keywords = [
        "team", "teams", "teamen", "teamein", "ٹیم", "ٹیمیں", "ٹیموں"
    ]
    if any(kw in q for kw in team_keywords):
        add_dep("team.txt")

    # 7. Club entity
    club_keywords = [
        "club", "clubs", "کلب", "کلبوں"
    ]
    if any(kw in q for kw in club_keywords):
        add_dep("club.txt")

    # 8. Live Match keywords
    live_keywords = [
        "live", "ongoing", "chalta", "jaari", "لائیو", "جاری", "current score"
    ]
    if any(kw in q for kw in live_keywords):
        add_dep("live_matches.txt")

    # 9. Point table keywords
    point_table_keywords = [
        "point table", "standings", "points", "پوائنٹس", "پوائنٹ"
    ]
    if any(kw in q for kw in point_table_keywords):
        add_dep("point_table.txt")

    return required_files


def retrieve_schema(question, top_k=5):
    print(f"Question received: '{question}'")
    query_vector = model.encode(question).tolist()

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k
    )

    retrieved_points = list(results.points)
    required_files = detect_query_dependencies(question)
    print("Required schema dependencies:", required_files)

    for required_file in required_files:
        if not is_file_retrieved(retrieved_points, required_file):
            print(f"Adding required schema: {required_file}")
            dependency_point = find_schema_file(required_file)
            if dependency_point is not None:
                retrieved_points.append(dependency_point)
            else:
                print(f"Warning: {required_file} was not found in Qdrant.")

    question_lower = question.lower()
    exact_table_matches = []

    for point in retrieved_points:
        filename = point.payload["file"]
        table_name = get_table_name(filename)
        clean_table_name = table_name.replace("_", " ")
        singular_name = clean_table_name.rstrip("s")
        plural_name = clean_table_name

        if (clean_table_name in question_lower or singular_name in question_lower or plural_name in question_lower):
            exact_table_matches.append(point)

    reordered_points = []
    for point in exact_table_matches:
        if point not in reordered_points:
            reordered_points.append(point)

    for required_file in required_files:
        for point in retrieved_points:
            if point.payload["file"] == required_file:
                if point not in reordered_points:
                    reordered_points.append(point)

    for point in retrieved_points:
        if point not in reordered_points:
            reordered_points.append(point)

    print("\n========== RETRIEVED FILES ==========\n")
    context = ""
    for point in reordered_points:
        filename = point.payload["file"]
        print(filename)
        context += point.payload["text"] + "\n\n"
    print("\n=====================================\n")

    return context
