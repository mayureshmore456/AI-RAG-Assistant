def build_prompt(question, search_results):
    """
    Build a prompt using the retrieved documents.

    Args:
        question (str): User question.
        search_results (list): Retrieved documents with similarity scores.

    Returns:
        str: Prompt for Gemini.
    """

    context = ""

    for index, result in enumerate(search_results, start=1):

        document = result["document"]

        context += (
            f"Document {index}\n"
            f"Source: {document.metadata['source']}\n\n"
            f"{document.text}\n\n"
        )

    prompt = f"""
You are an AI assistant.

Answer the user's question ONLY using the information provided in the context below.

If the answer cannot be found in the context, say:

"I couldn't find the answer in the provided documents."

------------------------
CONTEXT
------------------------

{context}

------------------------
QUESTION
------------------------

{question}

------------------------
ANSWER
------------------------
"""

    return prompt