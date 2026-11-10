import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import answer_generator
import main
from rag.knowledge import knowledge_retriever
from question_router import is_current_match_question, is_general_knowledge_question


class ChatApiTests(unittest.TestCase):
    def test_general_cricket_question_uses_knowledge_route_and_returns_source(self):
        question = "How many runs is a six worth?"
        with patch.object(
            main,
            "retrieve_knowledge",
            return_value=("A six is worth six runs.", ["Cricket Knowledge #1"]),
        ), patch.object(
            main,
            "generate_knowledge_answer",
            return_value="A six is worth six runs.",
        ), patch.object(main, "generate_sql") as generate_sql:
            response = main.chat_endpoint(main.ChatRequest(question=question))

        self.assertEqual(response.route, "knowledge")
        self.assertEqual(response.sources, ["Cricket Knowledge #1"])
        self.assertEqual(response.sql, "")
        self.assertEqual(response.columns, [])
        self.assertIn("six runs", response.answer)
        generate_sql.assert_not_called()

    def test_empty_knowledge_retrieval_abstains_without_calling_llm(self):
        fake_llm = SimpleNamespace(invoke=Mock())
        with patch.object(main, "retrieve_knowledge", return_value=("", [])), patch.object(
            answer_generator, "llm", fake_llm
        ):
            response = main.chat_endpoint(
                main.ChatRequest(question="What does LBW mean?")
            )

        self.assertEqual(response.route, "knowledge")
        self.assertEqual(response.sources, [])
        self.assertIn("do not provide enough information", response.answer)
        fake_llm.invoke.assert_not_called()

    def test_database_statistics_remain_on_sql_route(self):
        with patch.object(main, "generate_sql", return_value="SELECT 1;"), patch.object(
            main,
            "execute_sql",
            return_value=(["Total"], [(1,)], [[1]]),
        ), patch.object(main, "generate_answer", return_value="One."):
            response = main.chat_endpoint(
                main.ChatRequest(question="How many matches are in the database?")
            )

        self.assertEqual(response.route, "database")
        self.assertEqual(response.sources, [])
        self.assertEqual(response.sql, "SELECT 1;")

    def test_knowledge_retriever_uses_scores_and_source_metadata(self):
        point = SimpleNamespace(
            score=0.8,
            payload={"title": "Cricket Rules #1", "text": "An over has six legal balls."},
        )
        model = SimpleNamespace(
            encode=lambda question: SimpleNamespace(tolist=lambda: [0.1, 0.2])
        )
        client = SimpleNamespace(
            query_points=lambda **kwargs: SimpleNamespace(points=[point])
        )
        with patch.object(knowledge_retriever, "_get_model", return_value=model), patch.object(
            knowledge_retriever, "_get_client", return_value=client
        ):
            context, sources = knowledge_retriever.retrieve_knowledge("What is an over?")

        self.assertIn("six legal balls", context)
        self.assertEqual(sources, ["Cricket Rules #1"])

    def test_knowledge_retriever_discards_low_relevance_passages(self):
        point = SimpleNamespace(
            score=knowledge_retriever.MIN_RELEVANCE_SCORE - 0.01,
            payload={"title": "Unrelated passage", "text": "Cricket is a bat-and-ball sport."},
        )
        model = SimpleNamespace(
            encode=lambda question: SimpleNamespace(tolist=lambda: [0.1, 0.2])
        )
        client = SimpleNamespace(
            query_points=lambda **kwargs: SimpleNamespace(points=[point])
        )
        with patch.object(knowledge_retriever, "_get_model", return_value=model), patch.object(
            knowledge_retriever, "_get_client", return_value=client
        ):
            context, sources = knowledge_retriever.retrieve_knowledge("Who won today?")

        self.assertEqual(context, "")
        self.assertEqual(sources, [])

    def test_general_knowledge_classifier_does_not_capture_database_stats(self):
        self.assertTrue(is_general_knowledge_question("What does LBW mean?"))
        self.assertTrue(
            is_general_knowledge_question("How many players are in a cricket team?")
        )
        self.assertFalse(
            is_general_knowledge_question("Which country has the most registered players?")
        )
        self.assertFalse(is_general_knowledge_question("How many sixes did Babar score?"))

    def test_current_match_questions_are_not_sent_to_static_rag_or_sql(self):
        question = "What was the score in today's cricket match?"
        with patch.object(main, "retrieve_knowledge") as retrieve, patch.object(
            main, "generate_sql"
        ) as generate_sql:
            response = main.chat_endpoint(main.ChatRequest(question=question))

        self.assertTrue(is_current_match_question(question))
        self.assertEqual(response.route, "unsupported")
        self.assertIn("not connected", response.answer)
        retrieve.assert_not_called()
        generate_sql.assert_not_called()


if __name__ == "__main__":
    unittest.main()