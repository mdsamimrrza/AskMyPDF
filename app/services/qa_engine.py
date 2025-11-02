from transformers import pipeline

# Load a generative model for better explanations
model_name = "google/flan-t5-large"
qa_pipeline = pipeline("text2text-generation", model=model_name)


def get_answer_from_context(question: str, context: str) -> str:
    """
    Generates a paragraph-style answer using context from the PDF.
    """
    if not context or len(context.strip()) == 0:
        return "No relevant content found in the PDF."

    # Combine question and context into a single prompt
    prompt = (
        f"Answer this question in detail using the given context.\n\n"
        # limit context length for performance
        f"Context:\n{context[:3000]}\n\n"
        f"Question: {question}\n\n"
        f"Answer:"
    )

    result = qa_pipeline(prompt, max_length=250,
                         do_sample=True, temperature=0.7)
    answer = result[0]['generated_text'].strip()

    if not answer:
        return "Sorry, I couldn’t find a clear answer from the PDF."

    return answer
