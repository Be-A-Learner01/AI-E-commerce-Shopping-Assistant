# ProA — AI E-commerce Shopping Assistant

> An AI-powered e-commerce shopping assistant built with **LangGraph, DeepSeek, Hybrid RAG, PostgreSQL + pgvector, ReAct-style Agent Architecture, HITL, FastAPI and Docker**.

ProA is an AI shopping assistant designed to understand user requirements, retrieve relevant long-term memories, search products through a hybrid retrieval pipeline, use tools through an agent loop, and involve the user in the decision process through Human-in-the-Loop (HITL).

---

## ✨ Features

* 🤖 **LLM-powered Shopping Assistant**

  * DeepSeek LLM
  * Structured requirement extraction
  * Tool calling

* 🧠 **Long-term Memory**

  * PostgreSQL
  * pgvector
  * Semantic memory retrieval
  * Memory extraction
  * Deduplication
  * Conflict detection and update

* 🔍 **Hybrid Product RAG**

  * Vector Semantic Search
  * BM25 Keyword Search
  * Reciprocal Rank Fusion (RRF)
  * BGE-M3 Embedding
  * BGE-Reranker-v2-M3
  * RAG fallback strategy

* 🔄 **ReAct-style Agent Architecture**

  * Reason
  * Act / Tool Calling
  * Observation
  * Re-evaluation
  * Iterative agent-tool loop

* 🙋 **Human-in-the-Loop (HITL)**

  * Product confirmation
  * LangGraph `interrupt()`
  * Persistent checkpoint
  * Resume execution with `Command`

* 🛠️ **Agent Tools**

  * Product Search
  * Product Detail
  * Product Comparison

* 🛡️ **Reliability**

  * Retry
  * Timeout
  * Exception handling
  * RAG fallback

* 📊 **Evaluation**

  * Memory Retrieval Evaluation
  * Requirement Extraction Evaluation
  * Product Relevance Evaluation
  * RAG Fallback Evaluation
  * End-to-End Evaluation
  * HITL Evaluation

* 🔭 **Observability**

  * Structured logging
  * Latency tracking
  * LangSmith tracing
  * LLM token / cost monitoring

* 🌐 **FastAPI**

  * REST API
  * Swagger UI
  * HITL conversation resume

* 🐳 **Docker**

  * Containerized FastAPI application
  * PostgreSQL + pgvector
  * Docker Compose

---

# 🏗️ AI System Architecture

```text
                         User
                           │
                           ▼
                        FastAPI
                           │
                           ▼
                    ┌──────────────┐
                    │  LangGraph   │
                    │    Agent     │
                    └──────┬───────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │ Memory Retrieval │
                  └────────┬─────────┘
                           │
                           ▼
                 ┌─────────────────────┐
                 │     Requirement     │
                 │     Extraction      │
                 └──────────┬──────────┘
                            │
                            ▼
                    ┌─────────────┐
                    │   Reason    │
                    └──────┬──────┘
                           │
                      Need Tool?
                       /       \
                     Yes        No
                      │          │
                      ▼          ▼
              ┌────────────┐   Answer
              │ Tool Call  │
              │    Act     │
              └─────┬──────┘
                    │
                    ▼
              ┌────────────┐
              │  ToolNode  │
              └─────┬──────┘
                    │
                    ▼
              ┌────────────┐
              │ Observation│
              │ Tool Result│
              └─────┬──────┘
                    │
                    └──────────────┐
                                   │
                                   ▼
                                Reason
                                   │
                                   ▼
                          Human Confirmation
                                (HITL)
                                   │
                                Resume
                                   │
                                   ▼
                            Memory Write
                                   │
                                   ▼
                                  END
```

---

# 🔄 ReAct-style Agent Architecture

ProA does not use a separate "ReAct Agent" implementation.

Instead, the ReAct concept is implemented through the LangGraph agent loop:

```text
Reason
   ↓
Act
   ↓
Tool Execution
   ↓
Observation
   ↓
Reason Again
   ↓
Act Again ...
```

In ProA:

| ReAct Concept    | ProA Implementation    |
| ---------------- | ---------------------- |
| Reason           | `agent_node`           |
| Act              | LLM Tool Calling       |
| Action Execution | `ToolNode`             |
| Observation      | `ToolMessage`          |
| Re-evaluation    | Return to `agent_node` |

This allows the agent to dynamically decide whether it needs additional product information or tools before generating the final response.

---

# 🔁 Agent Workflow

The main LangGraph workflow is:

```text
START
  │
  ▼
Memory Retrieval
  │
  ▼
Requirement Extraction
  │
  ▼
Agent
  │
  ├─────────────── No Tool ──────────────► Memory Write
  │
  ▼
ToolNode
  │
  ▼
Agent
  │
  ├─────────────── Need More Tools ─────► ToolNode
  │
  ▼
Human Confirmation
  │
  ▼
User Resume
  │
  ▼
Memory Write
  │
  ▼
END
```

The agent can therefore combine:

* User requirements
* Long-term memory
* Product retrieval
* Tool results
* Human confirmation

before completing the conversation.

---

# 🧠 Long-term Memory

ProA uses **PostgreSQL + pgvector** for persistent user memory.

## Memory Pipeline

```text
User Message
     │
     ▼
Memory Extraction
     │
     ▼
Embedding
     │
     ▼
PostgreSQL + pgvector
     │
     ├── Deduplication
     │
     └── Conflict Detection / Update
     │
     ▼
Long-term Memory
```

## Memory Retrieval

When a new user request arrives:

```text
User Query
    │
    ▼
BGE-M3 Embedding
    │
    ▼
pgvector
    │
    ▼
Cosine Similarity
    │
    ▼
Top-K Memories
    │
    ▼
Requirement Extraction
```

The retrieved memories are provided to the requirement extraction stage so that previous user preferences can influence the current request.

Example:

```text
Previous:
"我比较喜欢三星手机"

Current:
"那你推荐一台手机给我"

        ↓

Memory Retrieval

        ↓

Requirement

brand = Samsung
category = 手机
```

---

# 🔍 Hybrid Product RAG

Product retrieval combines semantic and keyword search.

```text
                    User Requirements
                           │
                 ┌─────────┴─────────┐
                 ▼                   ▼
          Semantic Search        BM25 Search
            BGE-M3                jieba
                 │                   │
                 └─────────┬─────────┘
                           ▼
                         RRF
                Reciprocal Rank Fusion
                           │
                           ▼
                       Reranker
                BGE-Reranker-v2-M3
                           │
                           ▼
                    Product Results
```

## Retrieval Pipeline

### 1. Semantic Search

Uses:

```text
BAAI/bge-m3
```

to convert queries and products into embeddings.

### 2. BM25

Provides keyword-based retrieval and improves matching for explicit product terms.

### 3. RRF

Reciprocal Rank Fusion combines semantic and BM25 rankings.

```text
Semantic Ranking
       +
BM25 Ranking
       ↓
      RRF
       ↓
Combined Ranking
```

### 4. Reranking

The combined results are reranked using:

```text
BAAI/bge-reranker-v2-m3
```

### 5. Fallback

If strict product filtering produces no suitable result, ProA relaxes selected constraints and performs another retrieval attempt.

```text
Strict Search
     │
     ├── Results found ──► Return
     │
     └── No results
             │
             ▼
       Relax constraints
             │
             ▼
        Search Again
```

---

# 🛠️ Agent Tools

ProA currently provides three tools:

```text
search_products
get_product_detail
compare_products
```

The agent decides whether and when to call these tools.

Example:

```text
User
 ↓
"帮我找一台5000元左右的手机"
 ↓
Agent Reasoning
 ↓
search_products
 ↓
Product Results
 ↓
Agent Observation
 ↓
Human Confirmation
 ↓
Final Answer
```

---

# 🙋 Human-in-the-Loop

ProA integrates LangGraph HITL to allow the user to confirm a product before the workflow continues.

```text
Product Search
      │
      ▼
Candidate Products
      │
      ▼
interrupt()
      │
      ▼
Waiting for User
      │
      ▼
Command(resume=...)
      │
      ▼
Continue Graph
```

The API exposes the HITL state:

```json
{
  "status": "waiting",
  "thread_id": "...",
  "interrupt": {
    "type": "product_confirmation",
    "message": "请选择你想继续了解的商品",
    "products": []
  }
}
```

After the user responds:

```text
waiting
   ↓
resume
   ↓
completed
```

LangGraph checkpointing allows the conversation to continue using the same `thread_id`.

---

# 🛡️ Reliability

ProA includes several reliability mechanisms.

## Retry

Retryable failures include:

* LLM timeout
* Connection errors
* Database operational errors
* Temporary LLM failures

The retry strategy uses exponential backoff.

```text
Request
  │
  ▼
Failure
  │
  ▼
Retry
  │
  ▼
Failure
  │
  ▼
Retry
  │
  ▼
Final Failure
```

LLM calls are protected by an async timeout using `asyncio.wait_for()`.

## Error Handling

Custom project exceptions separate different failure categories:

```text
BaseError
├── LLMError
├── ProductSearchError
└── MemoryError
```

---

# 📊 Evaluation

ProA includes evaluation at multiple levels.

## Memory Retrieval

Current evaluation:

```text
Precision@5 = 0.78
Recall@5    = 1.00
```

## RAG Fallback

Fallback evaluation:

```text
Passed: 2 / 2
```

## End-to-End Evaluation

The evaluation pipeline checks:

* Requirement Accuracy
* Product Relevance
* End-to-End Success

Product relevance is evaluated against the current product dataset.

## HITL Evaluation

Current HITL test cases:

```text
hitl_001  Phone Recommendation
hitl_002  Running Shoes Recommendation
hitl_003  Normal Greeting
```

Result:

```text
HITL Evaluation: 3/3
```

The evaluation verifies:

```text
Should Interrupt
       ↓
Actual Interrupt
       ↓
Resume
       ↓
Completed
```

---

# 🔭 Observability

ProA uses structured logging and LangSmith for observability.

Tracked information includes:

* Node execution
* LLM latency
* Retrieval latency
* Product search latency
* Tool execution
* LLM token usage
* LLM cost
* Errors

Example workflow:

```text
LangGraph
   │
   ├── Memory Retrieval
   ├── Requirement Extraction
   ├── Agent
   ├── Tool
   ├── Product Retrieval
   └── Memory Write
          │
          ▼
      LangSmith
```

This makes it possible to analyze both **latency** and **LLM cost** across the complete agent workflow.

---

# 🌐 FastAPI

ProA exposes the agent through FastAPI.

## Request

```json
{
  "user_id": "test001",
  "query": "帮我推荐一台5000元左右的手机"
}
```

For HITL continuation:

```json
{
  "user_id": "test001",
  "query": "",
  "thread_id": "existing-thread-id",
  "resume": "1"
}
```

## Response

The API can return:

```json
{
  "status": "waiting",
  "thread_id": "...",
  "answer": null,
  "requirements": {},
  "products": [],
  "interrupt": {}
}
```

After resuming:

```json
{
  "status": "completed",
  "thread_id": "...",
  "answer": "...",
  "requirements": {},
  "products": [],
  "interrupt": null
}
```

Swagger UI can be used to test the API interactively.

---

# 📁 Project Structure

```text
E-commerce-asist/
│
├── app/
│   ├── agent/
│   │   ├── graph.py
│   │   ├── state.py
│   │   ├── nodes.py
│   │   └── prompts.py
│   │
│   ├── tools/
│   │   ├── product_search.py
│   │   ├── product_detail.py
│   │   └── product_compare.py
│   │
│   ├── retrieval/
│   │   ├── vector_search.py
│   │   ├── bm25_search.py
│   │   ├── hybrid_search.py
│   │   └── reranker.py
│   │
│   ├── memory/
│   │   └── long_term/
│   │
│   ├── models/
│   │   └── llm.py
│   │
│   ├── eval/
│   │   ├── hitl_eval.py
│   │   ├── requirements_eval.py
│   │   ├── product_relevance_eval.py
│   │   └── e2e_eval.py
│   │
│   ├── data/
│   │
│   ├── schemas/
│   │
│   ├── utils/
│   │
│   └── main.py
│
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
├── .env.example
└── README.md
```

---

# 🧰 Tech Stack

| Category              | Technology              |
| --------------------- | ----------------------- |
| Language              | Python                  |
| Agent Framework       | LangGraph               |
| LLM                   | DeepSeek                |
| API                   | FastAPI                 |
| Embedding             | BAAI/bge-m3             |
| Reranker              | BAAI/bge-reranker-v2-m3 |
| Vector Database       | PostgreSQL + pgvector   |
| Keyword Retrieval     | BM25                    |
| Fusion                | RRF                     |
| Agent Pattern         | ReAct-style             |
| Human Interaction     | LangGraph HITL          |
| Observability         | LangSmith               |
| Database ORM          | SQLAlchemy              |
| Async Database        | aiosqlite / PostgreSQL  |
| Dependency Management | uv                      |
| Containerization      | Docker / Docker Compose |

---

# 🚀 Running Locally

## 1. Install dependencies

```bash
uv sync
```

## 2. Configure environment variables

Create `.env`:

```env
DATABASE_URL=postgresql://postgres:123456@localhost:5432/proa
```

Configure the required LLM and LangSmith environment variables according to your local setup.

## 3. Start the application

```bash
uv run uvicorn app.main:app --reload
```

Then open the FastAPI Swagger UI.

---

# 🐳 Docker

ProA can also run through Docker Compose.

```bash
docker compose build
docker compose up
```

The Docker architecture is:

```text
              Docker Compose
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
      proa-app            proa-postgres
      FastAPI              PostgreSQL
      LangGraph             + pgvector
          │                   │
          └─────────┬─────────┘
                    │
                  Network
```

The application connects to PostgreSQL through the Docker service name rather than `localhost`.

---

# 🎯 Project Goals

ProA focuses on demonstrating a complete AI application architecture rather than only implementing a simple chatbot.

The project combines:

```text
LLM
 +
Agent
 +
ReAct-style Tool Calling
 +
RAG
 +
Long-term Memory
 +
HITL
 +
Evaluation
 +
Observability
 +
API
 +
Docker
```

The goal is to demonstrate how these components can work together in a complete AI-powered e-commerce assistant.

---

# 🔮 Future Improvements

Potential future improvements include:

* More comprehensive product evaluation datasets
* Better product relevance evaluation
* More advanced memory management
* Streaming responses
* More sophisticated HITL interaction
* Production-grade PostgreSQL deployment
* Authentication and user management
* More advanced retrieval optimization
* Cost and latency optimization

---

# 👤 Author

**LJR**

AI / Backend Engineering Project
