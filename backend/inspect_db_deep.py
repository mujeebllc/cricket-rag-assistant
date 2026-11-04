import sys
sys.path.append('/home/inara/aiproject/backend')
from database.db import engine
from sqlalchemy import text

with engine.connect() as conn:
    def q(title, sql):
        print(f"\n==================== {title} ====================")
        print("SQL:", sql)
        try:
            res = conn.execute(text(sql))
            if res.returns_rows:
                rows = res.fetchall()
                print(f"Row count: {len(rows)}")
                for r in rows[:10]:
                    print("  ", r)
            else:
                print("No rows returned (non-SELECT)")
        except Exception as e:
            print("ERROR:", e)

    q("7. BEST BOWLING IN AN INNINGS - fow / bowling_detail / bowling_stats", "SELECT p.FullName, bd.Wickets, bd.Runs FROM bowling_detail bd JOIN player p ON bd.PlayerId = p.PlayerId ORDER BY bd.Wickets DESC, bd.Runs ASC LIMIT 5;")
    q("7. BEST BOWLING - check Asad Raza", "SELECT p.FullName, bd.Wickets, bd.Runs, bd.Overs FROM bowling_detail bd JOIN player p ON bd.PlayerId = p.PlayerId WHERE LOWER(p.FullName) LIKE '%asad raza%' ORDER BY bd.Wickets DESC LIMIT 5;")

    q("11. HIGHEST INNINGS TOTAL - batting_detail sum by match/innings", "SELECT MatchNo, Innings, SUM(Runs) AS InningsTotal FROM batting_detail GROUP BY MatchNo, Innings ORDER BY InningsTotal DESC LIMIT 5;")
    q("11. HIGHEST INNINGS TOTAL - innings table score", "SELECT * FROM innings ORDER BY Score DESC LIMIT 5;")
    
    q("14. RAWAL KINGS - team names", "SELECT TeamId, TeamName, ClubId FROM team WHERE LOWER(TeamName) LIKE '%rawal%' OR LOWER(TeamName) LIKE '%kings%';")
    q("14. RAWAL KINGS - matches win check by club 94", "SELECT COUNT(*) FROM matches WHERE Winner IN (SELECT TeamId FROM team WHERE ClubId = 94);")
    q("14. RAWAL KINGS - matches win check by team name", "SELECT COUNT(*) FROM matches WHERE WinnerName LIKE '%Rawal Kings%';")
