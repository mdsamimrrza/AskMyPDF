"""QA engine with lazy model loading and configurable model choice.

Transforms heavy pipeline import into a lazy loader and uses an env var
`QA_MODEL` to select the model. Default uses a small/smaller model suitable
for CPU-limited environments. The pipeline is created on first use.
"""
import os
from typing import Optional


_qa_pipeline = None


def _get_pipeline():
    """Lazily load the transformers pipeline. The model can be overridden
    with the `QA_MODEL` environment variable.
    """
    global _qa_pipeline
    if _qa_pipeline is None:
        # default to a small/flan model that fits in limited RAM
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


def get_answer_from_context(question: str, context: str, max_context_chars: Optional[int] = 3000) -> str:
    """Generate an answer given a question and context. The pipeline is lazily
    loaded on first invocation.
    """
    if not context or len(context.strip()) == 0:
        return "No relevant content found in the PDF."

    prompt = (
        "Answer this question in detail using the given context.\n\n"
        f"Context:\n{context[:max_context_chars]}\n\n"
        f"Question: {question}\n\n"
        "Answer:"
    )

    pipeline = _get_pipeline()
    result = pipeline(prompt, max_length=250, do_sample=True, temperature=0.7)
    # pipeline text2text-generation returns generated_text for many models
    answer = result[0].get("generated_text") or result[0].get("text") or ""
    answer = answer.strip()

    if not answer:
        return "Sorry, I couldn’t find a clear answer from the PDF."

    return answer
