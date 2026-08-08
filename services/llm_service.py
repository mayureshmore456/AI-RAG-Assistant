from config import LLM_MODEL


class LLMService:
    """
    Handles communication with the Gemini language model.
    """

    def __init__(self, client):
        self.client = client

    def generate_answer(self, prompt):
        """
        Send a prompt to Gemini and return the generated answer.
        """

        response = self.client.models.generate_content(
            model=LLM_MODEL,
            contents=prompt
        )

        return response.text