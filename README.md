# AI Engineering Lab

A progressive learning repository covering core AI engineering concepts — from a basic chatbot to tool-augmented agents and retrieval-augmented generation.

## Roadmap

| Phase | Topic | Status |
|---|---|---|
| 01 | Chatbot with memory management strategies | In progress |
| 02 | Tool calling and MCP integration | Planned |
| 03 | RAG over documentation | Planned |

This progression follows the standard path in AI engineering: mastering context management before adding external capabilities, then grounding the model in private knowledge.

## Project Structure

```
src/
├── main.py                  # Chat loop with streaming support
├── config.py                # Config loading and OpenAI-compatible client
├── memory/
│   ├── memory_manager.py    # Abstract MemoryManager base class
│   └── token_counter.py     # Token counting via tiktoken
└── custom_types/
    └── enums.py             # Role enum (user / assistant / system)
```

## Memory Strategies

| Strategy | Description | Status |
|---|---|---|
| `SlidingWindowMem` | Keeps the last N user/assistant exchanges | Done |
| `TokenWindowMem` | Keeps messages within a token budget | Planned |
| `SummaryMem` | Summarizes older messages to free up context | Planned |
| `VectorMem` | Retrieves relevant messages by semantic similarity | Planned |

## Getting Started

**Prerequisite:** [uv](https://docs.astral.sh/uv/)

```bash
git clone https://github.com/<username>/ai-engineering-lab
cd ai-engineering-lab
uv sync
cp .env.example .env
```

Edit `.env` with your values:

```env
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=ollama
CHAT_MODEL=qwen3.5:4b
```

## Usage

```bash
uv run src/main.py
```

Type `quit`, `exit`, or `bye` to stop. `Ctrl+C` cancels the current generation.