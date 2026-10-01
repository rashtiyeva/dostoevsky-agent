# Dostoevsky Research Agent

**An agentic RAG research assistant for exploring Fyodor Dostoevsky's works and external literary research with grounded, source-backed answers.**

![Python](https://img.shields.io/badge/Python-3.12-5F7A68?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-API-5F7A68?style=flat-square&logo=fastapi&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--5.6-5F7A68?style=flat-square&logo=openai&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-5F7A68?style=flat-square)
![Docker](https://img.shields.io/badge/Docker-Compose-5F7A68?style=flat-square&logo=docker&logoColor=white)
![Tests](https://img.shields.io/badge/tests-passing-5F7A68?style=flat-square)

Dostoevsky Research Agent is a multilingual research system that combines a structured corpus of Dostoevsky's works with external web research.

The agent decides which sources are required for a question, retrieves relevant evidence through a hybrid search pipeline, reranks the results, and generates a grounded answer with inspectable sources.

The interface uses **Server-Sent Events (SSE)** to expose research progress and stream the generated answer as it is produced.

---

## Demo

<!-- Add demo video here -->

`demo.mp4`

The interface displays live research stages, streams the answer progressively, and keeps the final response separate from expandable corpus and external sources.

---

## How it works

```text
Research question
       │
       ▼
 Agent orchestration
       │
       ├───────────────┐
       ▼               ▼
 Corpus search      Web search
       │
       ▼
 Dense retrieval + BM25
       │
       ▼
 Reciprocal Rank Fusion
       │
       ▼
 Cross-encoder reranking
       │
       └───────────────┐
                       ▼
              Grounded generation
                       │
                       ▼
          SSE answer + sources
                       │
                       ▼
                 Browser UI
```

## Retrieval pipeline

The local corpus contains five Dostoevsky works:

- *Crime and Punishment*
- *The Brothers Karamazov*
- *Demons*
- *The Idiot*
- *Notes from Underground*

The books are parsed with structural metadata and split into token-aware chunks before indexing.

Retrieval uses:

```text
Query
  ↓
BGE-M3 dense retrieval ───┐
                          ├── Reciprocal Rank Fusion
BM25 sparse retrieval ────┘
                          ↓
                BGE reranker
                          ↓
                   Top sources
```

Dense retrieval captures semantic similarity, while BM25 provides lexical matching. Their results are combined with **Reciprocal Rank Fusion (RRF)** and passed through a **BGE cross-encoder reranker** before generation.

---

## Agent behavior

The agent has two research tools:

| Tool | Purpose |
| --- | --- |
| `corpus_search` | Searches Dostoevsky's literary works |
| `web_search` | Retrieves external scholarship, criticism, historical context, and current research |

Depending on the question, the agent can use the corpus, the web, or both.

Questions outside the Dostoevsky research scope are handled without invoking unrelated research tools.

---

## Grounded answers and sources

**Scope: The agent is intentionally limited to Dostoevsky-related research. Questions outside this scope are not answered.**

Generated answers are based on information returned by the research tools.

Corpus results preserve source metadata including the work, chapter, section, chunk position, and retrieved passage. The UI presents useful citation metadata separately from the answer and allows the original retrieved passages to be expanded.

External research results are presented separately as web sources.

This keeps the generated interpretation distinct from the evidence used to produce it.

---

## Tech stack

| Technology | Purpose |
| --- | --- |
| **Python 3.12** | Application runtime |
| **FastAPI** | API, SSE, and frontend serving |
| **OpenAI API** | Agent orchestration, generation, and web research |
| **BGE-M3** | Dense multilingual embeddings |
| **BGE Reranker v2 M3** | Cross-encoder reranking |
| **Qdrant** | Vector storage and dense search |
| **BM25** | Sparse lexical retrieval |
| **RRF** | Dense and sparse rank fusion |
| **pytest** | Automated testing |
| **HTML / CSS / JavaScript** | Same-origin research interface |
| **Docker / Docker Compose** | Reproducible application runtime |

---

## Project structure

```text
dostoevsky-agent/
├── agent/          # Agent orchestration and tool execution
├── app/            # FastAPI application and API schemas
├── embeddings/     # BGE-M3 embedding layer
├── evaluation/     # Retrieval and generation evaluation
├── frontend/       # Same-origin HTML/CSS/JavaScript UI
├── generation/     # Prompt and citation utilities
├── ingestion/      # Parsing and corpus preparation
├── retrieval/      # Dense, BM25, hybrid and reranked retrieval
├── tools/          # Corpus and web research tools
├── vector_store/   # Qdrant integration
└── tests/          # Automated tests
```

## Design decisions

### Why hybrid retrieval?

Semantic retrieval and lexical retrieval solve different failure modes. Combining BGE-M3 dense search with BM25 allows both semantic and exact textual signals to contribute before reranking.

### Why reranking?

Initial retrieval is optimized for candidate discovery. A cross-encoder can then evaluate the query and candidate passages together, improving the ordering of the final evidence supplied to generation.

### Why an agent?

Some questions can be answered from Dostoevsky's texts, while others require external scholarship or both. Tool selection allows the system to choose the appropriate research path instead of running every source for every request.

### Why SSE?

Retrieval, reranking, external research, and generation can introduce noticeable latency. SSE exposes those stages and streams generated text over the existing HTTP request without requiring a bidirectional WebSocket connection.

---

## 🚀 Quickstart

Set your OpenAI API key in `.env`:

```env
OPENAI_API_KEY=your_api_key
```

Start the application:

```bash
docker compose up -d --build
```

Open the UI: `http://localhost:8000/`
---

## Author

**Shafiga Rashtiyeva**

[LinkedIn](https://www.linkedin.com/in/shafiga-rashtiyeva-0aa427281)
