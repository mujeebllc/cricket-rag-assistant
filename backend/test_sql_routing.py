import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from sqlalchemy import text

from answer_generator import generate_answer
from database.db import engine
import sql_generator


class SqlRoutingTests(unittest.TestCase):
    def assert_uses_schema_rag(self, question):
        prompts = []
        schema = "SCHEMA_CONTEXT_SENTINEL"
        fake_llm = SimpleNamespace(
            invoke=lambda prompt: prompts.append(prompt) or "SELECT * FROM team;"
        )

        with patch.object(sql_generator, "retrieve_schema", return_value=schema) as retrieve, \
             patch.object(sql_generator, "llm", fake_llm), \
             patch.object(sql_generator, "try_execute_sql", return_value=None):
            sql = sql_generator.generate_sql(question)

        retrieve.assert_called_once_with(question)
        self.assertEqual(sql, "SELECT * FROM team;")
        self.assertIn(schema, prompts[0])
        self.assertIn(question, prompts[0])

    def test_registered_player_count_and_country_ranking_are_distinct(self):
        ranking_sql = sql_generator.generate_sql(
            "Which country has the most registered players?"
        )
        count_sql = sql_generator.generate_sql(
            "Give me the total number of registered players in the database."
        )

        self.assertIn("GROUP BY Country", ranking_sql)
        self.assertIn("COUNT(*) AS Total FROM player", count_sql)

    def test_supported_exact_fast_paths_remain_available(self):
        clubs_sql = sql_generator.generate_sql(
            "Can you tell me the total number of clubs stored in the system?"
        )
        five_wicket_hauls_sql = sql_generator.generate_sql(
            "How many total 5-wicket hauls were recorded in bowling_stats?"
        )
        player_profile_sql = sql_generator.generate_sql("Who is Babar Azam?")
        player_sixes_sql = sql_generator.generate_sql(
            "How many sixes has Usman Mustafa scored?"
        )
        bowling_sql = sql_generator.generate_sql(
            "Who has the best bowling wickets in an innings?"
        )
        rawal_wins_sql = sql_generator.generate_sql(
            "How many matches were won by Rawal Kings Cricket Club & Academy,Rwp?"
        )

        self.assertIn("FROM club", clubs_sql)
        self.assertIn("SUM(Fivefor)", five_wicket_hauls_sql)
        self.assertIn("LOWER(FullName) = LOWER('babar azam')", player_profile_sql)
        self.assertIn("LOWER(FullName) = LOWER('usman mustafa')", player_sixes_sql)
        self.assertIn(
            "bd.Wickets = (SELECT MAX(Wickets) FROM bowling_detail",
            bowling_sql,
        )
        self.assertNotIn("LIMIT 1", bowling_sql)
        self.assertNotIn("asad raza", bowling_sql.lower())
        self.assertIn("COUNT(*) AS MatchWins", rawal_wins_sql)

    def test_complex_or_ambiguous_prompts_use_schema_rag(self):
        questions = [
            "How many clubs have at least 3 players?",
            "Total sixes scored in batting_detail by country?",
            "Who is the highest run scorer?",
            "Show Rawal Kings players",
            "Which team has the most wins in each tournament?",
            "How many runs has Babar Azam scored in 2019?",
        ]

        for question in questions:
            with self.subTest(question=question):
                self.assert_uses_schema_rag(question)

    def test_per_tournament_wins_query_uses_retrieved_schema(self):
        schema = "CREATE TABLE point_table (TournamentId, Groupe, Team, TeamName, Won);"
        with patch.object(sql_generator, "retrieve_schema", return_value=schema) as retrieve, \
             patch.object(sql_generator, "try_execute_sql", return_value=None):
            sql = sql_generator.generate_sql(
                "Which team has the most wins in each tournament?"
            )

        retrieve.assert_called_once()
        self.assertIn("FROM point_table pt", sql)
        self.assertIn("candidate.TournamentId = pt.TournamentId", sql)
        self.assertIn("pt.Won = (SELECT MAX(candidate.Won)", sql)
        self.assertIn("LEFT JOIN team t ON t.TeamId = pt.Team", sql)
        self.assertNotIn("GROUP BY", sql.upper())
        self.assertNotIn("MAX(Won) AS Max_Won", sql)

    @unittest.skipUnless(
        os.getenv("RUN_LIVE_RAG_TESTS") == "1",
        "Set RUN_LIVE_RAG_TESTS=1 to query Qdrant, Ollama, and MariaDB.",
    )
    def test_live_per_tournament_wins_match_database_maxima(self):
        question = "Which team has the most wins in each tournament?"
        sql = sql_generator.generate_sql(question)

        with engine.connect() as connection:
            columns = list(connection.execute(text(sql)).keys())
            rows = connection.execute(text(sql)).fetchall()
            maxima = dict(
                connection.execute(
                    text("SELECT TournamentId, MAX(Won) FROM point_table GROUP BY TournamentId")
                ).fetchall()
            )

        self.assertIn("Groupe", columns)
        self.assertIn("TeamName", columns)
        self.assertGreater(len(rows), 0)
        self.assertEqual({row[0] for row in rows}, set(maxima))
        for row in rows:
            self.assertEqual(row[4], maxima[row[0]])

        answer = generate_answer(question, sql, columns, rows)
        self.assertIn("Top-win teams by tournament", answer)

    def test_best_bowling_answer_reports_all_top_ties(self):
        answer = generate_answer(
            "Who has the best bowling wickets in an innings?",
            "SELECT PlayerName, Wickets, Runs FROM bowling_detail;",
            ["PlayerName", "Wickets", "Runs"],
            [
                ("Asad Raza", 10, 31),
                ("Kashif Munawar", 10, 10),
                ("Muqaddas", 10, 15),
            ],
        )

        self.assertIn("Asad Raza", answer)
        self.assertIn("Kashif Munawar", answer)
        self.assertIn("Muqaddas", answer)
        self.assertIn("10 each", answer)

    def test_best_bowling_answer_uses_singular_for_one_leader(self):
        answer = generate_answer(
            "Who has the best bowling wickets in an innings?",
            "SELECT PlayerName, Wickets, Runs FROM bowling_detail;",
            ["PlayerName", "Wickets", "Runs"],
            [("Asad Raza", 10, 31)],
        )

        self.assertIn("Asad Raza recorded the most wickets", answer)
        self.assertNotIn("are tied", answer)


if __name__ == "__main__":
    unittest.main()