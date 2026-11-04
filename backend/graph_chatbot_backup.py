print("1. Starting chatbot...")


# ============================================================
# IMPORT DATABASE
# ============================================================

from database.db import engine

print("2. Database imported")


# ============================================================
# IMPORT SQL GENERATOR
#
# This keeps:
# - Direct deterministic rules
# - RAG schema retrieval
# - LLM SQL generation
#
# Nothing is removed from sql_generator.py.
# ============================================================

from sql_generator import generate_sql

print("3. SQL generator imported")


# ============================================================
# IMPORT FAST ANSWER GENERATOR
#
# No second LLM call.
# Answers are generated directly from SQL results.
# ============================================================

from answer_generator import generate_answer

print("4. Answer generator imported")


# ============================================================
# LANGGRAPH
# ============================================================

from langgraph.graph import StateGraph, START, END

print("5. LangGraph imported")


# ============================================================
# OTHER IMPORTS
# ============================================================

from typing import TypedDict

from sqlalchemy import text


# ============================================================
# GRAPH STATE
# ============================================================

class ChatState(TypedDict):

    question: str

    sql: str

    columns: list

    rows: list

    answer: str

    route: str


# ============================================================
# ROUTER NODE
#
# This is the first LangGraph routing layer.
#
# IMPORTANT:
# The router does NOT generate SQL.
#
# SQL generation is still handled by your existing
# sql_generator.py.
#
# Current routes:
#
# 1. database
#    - Direct deterministic rules
#    - OR RAG + LLM
#
# 2. live_score
#    - Reserved for future Live Cricket API
#
# For now, all questions go to database.
#
# This keeps the current working system safe.
# ============================================================

def router_node(state: ChatState):

    question = state["question"].lower().strip()


    # --------------------------------------------------------
    # FUTURE LIVE SCORE ROUTE
    #
    # We are NOT connecting the API yet.
    # This route is reserved for the next phase.
    # --------------------------------------------------------

    live_keywords = [

        "live score",

        "live scores",

        "live match",

        "live matches",

        "current score",

        "current scores",

        "score right now",

        "match right now",

    ]


    for keyword in live_keywords:

        if keyword in question:

            # For now, keep database route.
            #
            # Later this will become:
            #
            # router
            #    ↓
            # live_score_node
            #    ↓
            # API
            #
            # We do NOT activate it yet because
            # the live API integration is not implemented.

            print(
                "\n[Router] Live-score question detected."
            )

            print(
                "[Router] Live API route is reserved for next phase."
            )

            print(
                "[Router] Using database route for now.\n"
            )

            state["route"] = "database"

            return state


    # --------------------------------------------------------
    # DEFAULT DATABASE ROUTE
    #
    # This includes:
    #
    # - Direct player statistics
    # - Player country list
    # - Player country count
    # - Most runs
    # - Most wins
    # - RAG-based schema retrieval
    # - LLM SQL generation
    # --------------------------------------------------------

    print(
        "\n[Router] Database question detected."
    )

    state["route"] = "database"

    return state


# ============================================================
# SQL GENERATION NODE
#
# Existing sql_generator.py handles:
#
# Direct rules:
# - Babar runs
# - Babar fours
# - Babar sixes
# - Babar balls faced
# - Players from Pakistan
# - Number of players from Pakistan
# - Most runs
# - Most match wins
#
# Other questions:
# - RAG retrieval
# - LLM SQL generation
#
# NOTHING IS REMOVED.
# ============================================================

def sql_node(state: ChatState):

    question = state["question"]


    print(
        "\n[LangGraph] Running SQL generation node..."
    )


    sql = generate_sql(question)


    state["sql"] = sql


    return state


# ============================================================
# SQL EXECUTION NODE
# ============================================================

def execute_node(state: ChatState):

    print(
        "\n[LangGraph] Running SQL execution node..."
    )


    try:

        with engine.connect() as conn:

            result = conn.execute(
                text(state["sql"])
            )


            # ------------------------------------------------
            # Save column names
            # ------------------------------------------------

            state["columns"] = list(
                result.keys()
            )


            # ------------------------------------------------
            # Save database rows
            # ------------------------------------------------

            state["rows"] = result.fetchall()


            # ------------------------------------------------
            # Clear previous answer
            # ------------------------------------------------

            state["answer"] = ""


    except Exception as e:

        state["columns"] = []

        state["rows"] = []


        state["answer"] = (
            f"SQL Error:\n{e}"
        )


    return state


# ============================================================
# ANSWER GENERATION NODE
#
# Uses answer_generator.py.
#
# No second LLM call.
# This keeps answers fast.
# ============================================================

def answer_node(state: ChatState):


    # --------------------------------------------------------
    # If SQL execution already produced an error,
    # do not generate another answer.
    # --------------------------------------------------------

    if state.get("answer"):

        return state


    print(
        "\n[LangGraph] Running answer generation node..."
    )


    answer = generate_answer(

        state["question"],

        state["sql"],

        state["columns"],

        state["rows"],

    )


    state["answer"] = answer


    return state


# ============================================================
# BUILD LANGGRAPH
# ============================================================

graph = StateGraph(ChatState)


# ------------------------------------------------------------
# ADD NODES
# ------------------------------------------------------------

graph.add_node(
    "router",
    router_node
)


graph.add_node(
    "generate_sql",
    sql_node
)


graph.add_node(
    "execute_sql",
    execute_node
)


graph.add_node(
    "generate_answer",
    answer_node
)


# ============================================================
# GRAPH FLOW
#
# START
#   ↓
# ROUTER
#   ↓
# SQL GENERATION
#   ↓
# SQL EXECUTION
#   ↓
# FAST ANSWER
#   ↓
# END
#
# The router is now ready for future API integration.
# ============================================================

graph.add_edge(
    START,
    "router"
)


graph.add_edge(
    "router",
    "generate_sql"
)


graph.add_edge(
    "generate_sql",
    "execute_sql"
)


graph.add_edge(
    "execute_sql",
    "generate_answer"
)


graph.add_edge(
    "generate_answer",
    END
)


# ============================================================
# COMPILE GRAPH
# ============================================================

app = graph.compile()


# ============================================================
# MAIN CHATBOT LOOP
# ============================================================

if __name__ == "__main__":


    print(
        "\n=============================================="
    )

    print(
        "   AI-POWERED CRICKET CHATBOT"
    )

    print(
        "   LangGraph + RAG + MariaDB"
    )

    print(
        "=============================================="
    )


    while True:


        question = input(
            "\nAsk Question (exit): "
        )


        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

        if question.lower().strip() == "exit":

            print(
                "\nChatbot stopped."
            )

            break


        # ----------------------------------------------------
        # IGNORE EMPTY QUESTION
        # ----------------------------------------------------

        if not question.strip():

            print(
                "\nPlease enter a question."
            )

            continue


        # ----------------------------------------------------
        # INITIAL GRAPH STATE
        # ----------------------------------------------------

        initial_state = {

            "question": question,

            "sql": "",

            "columns": [],

            "rows": [],

            "answer": "",

            "route": "",

        }


        # ----------------------------------------------------
        # RUN LANGGRAPH
        # ----------------------------------------------------

        result = app.invoke(
            initial_state
        )


        # ----------------------------------------------------
        # SHOW ROUTE
        # ----------------------------------------------------

        print(
            "\n========== LANGGRAPH ROUTE =========="
        )

        print(
            result["route"]
        )

        print(
            "====================================="
        )


        # ----------------------------------------------------
        # SHOW GENERATED SQL
        # ----------------------------------------------------

        print(
            "\nGenerated SQL:\n"
        )

        print(
            result["sql"]
        )


        # ----------------------------------------------------
        # SHOW FINAL ANSWER
        # ----------------------------------------------------

        print(
            "\nAnswer:\n"
        )

        print(
            result["answer"]
        )
