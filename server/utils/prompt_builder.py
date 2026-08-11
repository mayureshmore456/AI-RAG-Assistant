def build_prompt(question, search_results):
    """
    Build the RAG prompt using retrieved documents.
    """

    context_parts = []

    for result in search_results:

        document = result["document"]

        context_parts.append(
            document.text
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
You are an AI assistant that answers questions using the provided document context.

Use the context below to answer the user's question.

If the answer cannot be found in the provided context, clearly say that the information is not available in the uploaded documents.

Do not invent information.

-------------------------
DOCUMENT CONTEXT
-------------------------

{context}

-------------------------
USER QUESTION
-------------------------

{question}

-------------------------
ANSWER
-------------------------
"""

    return prompt