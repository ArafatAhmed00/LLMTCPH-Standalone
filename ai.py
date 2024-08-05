import os
import requests

from dotenv import load_dotenv

class AI:
    def __init__(self) -> None:

        load_dotenv()
        self.OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

    def _validate_messages(self, messages: list[dict[str, str]]) -> None:
        """
        Validates the messages list to ensure it has the correct format.
        """
        for message in messages:
            if set(message.keys()) != {"role", "content"}:
                raise ValueError(f"Invalid keys in message: {message.keys()}. Only 'role' and 'content' are allowed.")
            if message["role"] not in ["system", "user", "assistant"]:
                raise ValueError(f"Invalid role: {message['role']}. Role must be one of 'system', 'user', or 'assistant'.")
    
    def generate(self, messages: list[dict[str, str]], model: str | None = None, **kwargs) -> str:
        """
        Generate a response using the OpenRouter API.

        Args:
            messages (list[dict[str, str]]): A list of message dictionaries.
            model (str | None): The model to use for generation. If None, uses the default model.
            **kwargs: Additional optional arguments to pass to the API call.

        Returns:
            str: The generated response text.

        Raises:
            ValueError: If the message format or roles are invalid.
            requests.RequestException: If the API request fails.
            KeyError: If the response JSON is missing expected keys.
        """
        if model is None:
            model = self.default_model

        self._validate_messages(messages)

        default_params = {
            "model": model,
            "messages": messages,
            "temperature": 0.2
        }
        
        params = {**default_params, **kwargs}
        
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.OPENROUTER_API_KEY}",
            },
            json=params
        )

        response.raise_for_status()  # This will raise an HTTPError for bad responses

        response_json = response.json()
        try:
            response_text = response_json["choices"][0]["message"]["content"]
            return response_text
        except KeyError as e:
            raise KeyError(f"Failed to get response: Missing key in API response - {str(e)}")
