"""QA engine with lazy model loading and configurable model choice.

Transforms heavy pipeline import into a lazy loader and uses an env var
`QA_MODEL` to select the model. Default uses a small/smaller model suitable
for CPU-limited environments. The pipeline is created on first use.
"""
import os
from typing import Optional

import os
from typing import Optional


_qa_pipeline = None


def _get_pipeline():
    """Lazily load the transformers pipeline. The model can be overridden
    with the `QA_MODEL` environment variable. This is only used when the
    QA_STRATEGY is set to 'model'."""
    global _qa_pipeline
    if _qa_pipeline is None:
        model_name = os.getenv("QA_MODEL", "google/flan-t5-small")
        try:
            from transformers import pipeline

            # force CPU device (device=-1) to avoid GPU assumptions
            _qa_pipeline = pipeline(
                "text2text-generation", model=model_name, device=-1
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load QA pipeline model {model_name}: {e}")
    return _qa_pipeline


def _extractive_answer(question: str, context: str, max_context_chars: int = 3000) -> str:
    """Lightweight extractive fallback that doesn't load big models.

    Strategy: try to find sentences in the context that contain tokens from the
    question. If none found, return the first useful chunk of context.
    """
    if not context or not context.strip():
        return "No relevant content found in the PDF."

    snippet = context[:max_context_chars]
    # split into sentences naively
    import re

    sentences = re.split(r"(?<=[.!?])\s+", snippet)
    # build a set of lowercase tokens from the question
    q_tokens = set(t.lower() for t in re.findall(r"\w+", question) if len(t) > 2)

    if q_tokens:
        # score sentences by how many tokens they contain
        scored = []
        for s in sentences:
            s_tokens = set(t.lower() for t in re.findall(r"\w+", s))
            score = len(q_tokens & s_tokens)
            if score > 0:
                scored.append((score, s))
        if scored:
            # choose the highest scoring sentence(s)
            scored.sort(key=lambda x: -x[0])
            top_sentences = " ".join(s for _, s in scored[:3])
            return top_sentences.strip()

    # fallback: return the beginning of the context as a helpful excerpt
    excerpt = snippet.strip()
    if len(excerpt) > 500:
        excerpt = excerpt[:500].rsplit(" ", 1)[0] + "..."
    return excerpt


def get_answer_from_context(question: str, context: str, max_context_chars: Optional[int] = 3000) -> str:
    """Public entry: chooses a strategy based on the QA_STRATEGY env var.

    - If QA_STRATEGY=model, lazily loads a transformers pipeline and runs it.
    - Otherwise (default 'extractive'), uses a small extractive heuristic.
    """
    strategy = os.getenv("QA_STRATEGY", "extractive").lower()
    if strategy != "model":
        # lightweight extractive answer — safe for low-memory hosts
        return _extractive_answer(question, context, max_context_chars or 3000)

    # strategy == 'model' -> use the (lazy) transformers pipeline
    pipeline = _get_pipeline()
    prompt = (
        "Answer this question in detail using the given context.\n\n"
        f"Context:\n{context[: (max_context_chars or 3000)]}\n\n"
        f"Question: {question}\n\n"
        "Answer:"
    )
    result = pipeline(prompt, max_length=250, do_sample=True, temperature=0.7)
    answer = result[0].get("generated_text") or result[0].get("text") or ""
    answer = answer.strip()
    if not answer:
        return "Sorry, I couldn’t find a clear answer from the PDF."
    return answer
