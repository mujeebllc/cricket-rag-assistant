import sys
sys.path.append('/home/inara/aiproject/backend')
from database.db import engine
from sqlalchemy import text

with engine.connect() as conn:
    print('1. TEAM', conn.execute(text('SELECT TeamName, COUNT(DISTINCT TournamentId) as cnt FROM team WHERE TournamentId IS NOT NULL AND TeamName IS NOT NULL AND TRIM(TeamName) != "" GROUP BY TeamName ORDER BY cnt DESC LIMIT 5')).fetchall())
    print('2. CLUB', conn.execute(text('SELECT c.ClubName, COUNT(DISTINCT tc.TournamentId) as cnt FROM tournament_club tc JOIN club c ON tc.ClubId = c.ClubId GROUP BY c.ClubName ORDER BY cnt DESC LIMIT 5')).fetchall())
    print('3. ROUND_TEAM', conn.execute(text('SELECT TeamName, COUNT(DISTINCT TournamentId) as cnt FROM round_team WHERE TeamName IS NOT NULL AND TRIM(TeamName) != "" GROUP BY TeamName ORDER BY cnt DESC LIMIT 5')).fetchall()
