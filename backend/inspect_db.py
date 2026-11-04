import sys
sys.path.append("/home/inara/aiproject/backend")
from database.db import engine
from sqlalchemy import text

with engine.connect() as conn:
    print("--- 1. TEAM Table Grouped by TeamName ---")
    res1 = conn.execute(text("SELECT TeamName, COUNT(DISTINCT TournamentId) as cnt FROM team WHERE TournamentId IS NOT NULL AND TeamName IS NOT NULL AND TRIM(TeamName) != '' GROUP BY TeamName ORDER BY cnt DESC LIMIT 10")).fetchall()
    for r in res1:
        print(r)

    print("\n--- 2. TOURNAMENT_CLUB Table ---")
    res2 = conn.execute(text("SELECT c.ClubName, COUNT(DISTINCT tc.TournamentId) as cnt FROM tournament_club tc JOIN club c ON tc.ClubId = c.ClubId GROUP BY c.ClubName ORDER BY cnt DESC LIMIT 10")).fetchall()
    for r in res2:
        print(r)

    print("\n--- 3. ROUND_TEAM Table ---")
    res3 = conn.execute(text("SELECT TeamName, COUNT(DISTINCT TournamentId) as cnt FROM round_team WHERE TeamName IS NOT NULL AND TRIM(TeamName) != '' GROUP BY TeamName ORDER BY cnt DESC LIMIT 10")).fetchall()
    for r in res3:
        print(r)

    print("\n--- 4. CHECK RELATIONSHIP BETWEEN TEAM AND CLUB ---")
    res4 = conn.execute(text("SHOW COLUMNS FROM team")).fetchall()
    print("team columns:", [r[0] for r in res4])
