"""
Jenkins AI Chatbot — Context Builder

Builds a structured prompt context from retrieved documents
for the LLM to generate informed answers.

Usage:
    from rag.context_builder import build_context
    prompt = build_context(query, retrieved_docs)
"""


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are a Jenkins assistant that helps users configure pipelines, "
    "install plugins, and troubleshoot errors. "
    "Answer the user's question based on the provided Jenkins knowledge. "
    "If the knowledge does not contain enough information, say so honestly. "
    "Be concise, accurate, and provide step-by-step instructions when appropriate."
)

CONTEXT_TEMPLATE = """Relevant Jenkins Knowledge:

{documents}

---

User Question: {question}

Please provide a helpful and accurate answer based on the knowledge above."""


# ---------------------------------------------------------------------------
# Context formatting
# ---------------------------------------------------------------------------


def format_documents(results: list[dict]) -> str:
    """
    Format retrieved document results into a numbered context block.

    Args:
        results: List of dicts from the retriever, each with
                 'text', 'source', 'category', 'score'.

    Returns:
        Formatted string like:
            Document 1 (Source: ..., Category: ...):
            <text>

            Document 2 ...
    """
    parts: list[str] = []
    for i, doc in enumerate(results, 1):
        source = doc.get("source", "unknown")
        category = doc.get("category", "unknown")
        text = doc.get("text", "")
        score = doc.get("score", 0.0)

        header = f"Document {i} (Source: {source}, Category: {category}, Relevance: {score:.2f}):"
        parts.append(f"{header}\n{text}")

    return "\n\n".join(parts)


def build_context(
    query: str,
    results: list[dict],
) -> str:
    """
    Build the full prompt context by combining retrieved documents
    with the user's question.

    Args:
        query:   The user's (normalized) question.
        results: Retrieved document list from the retriever.

    Returns:
        A complete context string ready to be appended to the system prompt
        and sent to the LLM.
    """
    documents_text = format_documents(results)
    return CONTEXT_TEMPLATE.format(documents=documents_text, question=query)


def build_prompt(
    query: str,
    results: list[dict],
) -> list[dict]:
    """
    Build a chat-style prompt (list of message dicts) for the LLM.

    Returns:
        [
            {"role": "system", "content": <system prompt>},
            {"role": "user",   "content": <context + question>},
        ]
    """
    context = build_context(query, results)
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": context},
    ]


# ---------------------------------------------------------------------------
# CLI demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    from rag.retriever import retrieve

    parser = argparse.ArgumentParser(description="Build LLM prompt context")
    parser.add_argument("query", type=str, help="User query")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    results = retrieve(args.query, top_k=args.top_k)
    prompt = build_prompt(args.query, results)

    print("=== SYSTEM ===")
    print(prompt[0]["content"])
    print("\n=== USER ===")
    print(prompt[1]["content"])
