import unittest
import tempfile
from types import SimpleNamespace
from unittest.mock import Mock, patch
from pathlib import Path

import answer_generator
import main
from fastapi.testclient import TestClient
from rag.knowledge import knowledge_retriever
from question_router import is_current_match_question, is_general_knowledge_question


class ChatApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.store_path_patch = patch.object(
            main.conversation_store,
            "DB_PATH",
            Path(self.temp_dir.name) / "chat_history.sqlite3",
        )
        self.store_path_patch.start()

    def tearDown(self):
        self.store_path_patch.stop()
        self.temp_dir.cleanup()

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

    def test_chat_persists_turns_and_resolves_followup_before_sql(self):
        conversation_id = main.conversation_store.create_conversation()
        main.conversation_store.append_turn(
            conversation_id,
            "Who scored the most runs?",
            "Aman scored the most runs.",
            {"sql": "SELECT large_result", "rows": [["excluded from context"]]},
        )
        request = main.ChatRequest(
            question="Which team did he play for?",
            conversation_id=conversation_id,
        )
        with patch.object(
            main,
            "resolve_followup_question",
            return_value="Which team did Aman play for?",
        ) as resolve, patch.object(
            main, "generate_sql", return_value="SELECT 'Aman';"
        ) as generate_sql, patch.object(
            main,
            "execute_sql",
            return_value=(["Team"], [("Pakistan",)], [["Pakistan"]]),
        ), patch.object(main, "generate_answer", return_value="Pakistan.") as answer:
            response = main.chat_endpoint(request)

        self.assertEqual(response.question, "Which team did he play for?")
        self.assertEqual(response.resolved_question, "Which team did Aman play for?")
        self.assertEqual(response.conversation_id, conversation_id)
        resolve.assert_called_once()
        context = resolve.call_args.args[1]
        self.assertIn("Who scored the most runs?", context)
        self.assertIn("Aman scored the most runs.", context)
        self.assertNotIn("excluded from context", context)
        generate_sql.assert_called_once_with("Which team did Aman play for?")
        answer.assert_called_once()
        messages = main.conversation_store.get_messages(conversation_id)
        self.assertEqual([message["role"] for message in messages], [
            "user", "assistant", "user", "assistant"
        ])
        self.assertEqual(
            messages[-1]["metadata"]["resolved_question"],
            "Which team did Aman play for?",
        )

    def test_context_budget_keeps_only_recent_text_not_response_metadata(self):
        conversation_id = main.conversation_store.create_conversation()
        main.conversation_store.append_turn(
            conversation_id,
            "Old question",
            "Old answer",
            {"rows": [["large result"]]},
        )
        main.conversation_store.append_turn(
            conversation_id,
            "Recent question",
            "Recent answer",
        )

        context = main.conversation_store.get_recent_context(conversation_id, 30)

        self.assertEqual(context, [
            {"role": "user", "content": "Recent question"},
            {"role": "assistant", "content": "Recent answer"},
        ])
        self.assertLessEqual(sum(len(message["content"]) for message in context), 30)

    def test_context_budget_preserves_previous_question_with_large_assistant_answer(self):
        conversation_id = main.conversation_store.create_conversation()
        main.conversation_store.append_turn(
            conversation_id,
            "Who scored the most runs?",
            "A" * 100,
        )

        context = main.conversation_store.get_recent_context(conversation_id, 40)

        self.assertEqual(context[0]["role"], "user")
        self.assertEqual(context[0]["content"], "Who scored the most runs?")
        self.assertLessEqual(sum(len(message["content"]) for message in context), 40)

    def test_conversation_context_is_isolated(self):
        first_id = main.conversation_store.create_conversation()
        second_id = main.conversation_store.create_conversation()
        main.conversation_store.append_turn(first_id, "First chat question", "First chat answer")

        self.assertEqual(
            main.conversation_store.get_recent_context(second_id, 100),
            [],
        )

    def test_conversation_http_endpoints_create_load_chat_and_delete(self):
        client = TestClient(main.app)
        created = client.post("/api/conversations")
        self.assertEqual(created.status_code, 200)
        conversation_id = created.json()["id"]

        with patch.object(main, "resolve_followup_question", side_effect=lambda q, _: q), patch.object(
            main, "generate_sql", return_value="SELECT 1;"
        ), patch.object(
            main, "execute_sql", return_value=(["Total"], [(1,)], [[1]])
        ), patch.object(main, "generate_answer", return_value="One."):
            chat = client.post(
                "/api/chat",
                json={"question": "How many matches?", "conversation_id": conversation_id},
            )

        self.assertEqual(chat.status_code, 200)
        self.assertEqual(chat.json()["conversation_id"], conversation_id)
        loaded = client.get(f"/api/conversations/{conversation_id}")
        self.assertEqual(loaded.status_code, 200)
        self.assertEqual(
            [message["role"] for message in loaded.json()["messages"]],
            ["user", "assistant"],
        )
        self.assertEqual(client.get("/api/conversations").json()[0]["id"], conversation_id)
        self.assertEqual(client.delete(f"/api/conversations/{conversation_id}").status_code, 200)
        self.assertEqual(client.get(f"/api/conversations/{conversation_id}").status_code, 404)

    def test_conversation_delete_removes_messages_and_unknown_ids_return_404(self):
        conversation_id = main.conversation_store.create_conversation()
        main.conversation_store.append_turn(conversation_id, "Question", "Answer")

        self.assertTrue(main.conversation_store.delete_conversation(conversation_id))
        self.assertFalse(main.conversation_store.conversation_exists(conversation_id))
        with self.assertRaises(main.HTTPException) as error:
            main.get_conversation_endpoint(conversation_id)
        self.assertEqual(error.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()