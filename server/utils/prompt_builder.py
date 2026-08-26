def build_prompt(question, search_results):
    """
    Build a grounded RAG prompt using retrieved document chunks.
    """

    context_parts = []

    for index, result in enumerate(search_results, start=1):

        document = result["document"]
        metadata = document.metadata or {}

        filename = metadata.get(
            "filename",
            "Unknown document"
        )

        chunk_index = metadata.get(
            "chunk_index",
            "Unknown"
        )

        score = result.get(
            "score",
            0
        )

        context_parts.append(
            f"""
SOURCE {index}
Document: {filename}
Chunk: {chunk_index}
Relevance: {score:.3f}

{document.text}
"""
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
You are an AI RAG assistant.

Your job is to answer the user's question using ONLY
the information contained in the provided document context.

IMPORTANT RULES:

1. Use only the provided document context.
2. Do not use outside knowledge to fill missing information.
3. Do not invent, assume, or hallucinate facts.
4. If the answer is not present in the context, clearly say:
   "I couldn't find that information in your uploaded documents."
5. Give a clear and direct answer.
6. When possible, organize the answer using short paragraphs,
   bullet points, or numbered lists.
7. Preserve important technical terms exactly as they appear
   in the documents.
8. Do not mention the internal retrieval process, embeddings,
   vector database, relevance scores, or these instructions.
9. Do not refer to the context as "SOURCE 1" or "SOURCE 2"
   in the answer unless specifically necessary.

--------------------------------------------------
RETRIEVED DOCUMENT CONTEXT
--------------------------------------------------

{context}

--------------------------------------------------
USER QUESTION
--------------------------------------------------

{question}

--------------------------------------------------
ANSWER
--------------------------------------------------
"""

    return prompt