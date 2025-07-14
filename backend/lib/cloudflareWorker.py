# api call for cloudflare

import requests
import numpy as np

class CloudflareWorker:
    def __init__(self, cloudflare_api_key: str, api_base_url: str, llm_model_name: str, embedding_model_name:str):
        self.cloudflare_api_key = cloudflare_api_key
        self.api_base_url = api_base_url
        self.llm_model_name = llm_model_name
        self.embedding_model_name = embedding_model_name
        self.max_tokens = 4080

    async def _send_request(self, model_name: str, input_: dict):
        headers = {"Authorization": f"Bearer {self.cloudflare_api_key}"}

        try:
            response_raw = requests.post(
                f"{self.api_base_url}{model_name}",
                headers=headers,
                json=input_,
                timeout=30
            ).json()

            result = response_raw.get("result", {})

            if "response" in result:
                return result["response"]

            if "data" in result:  # Embedding case
                return np.array(result["data"])

            return "Error: No response from Cloudflare"

        except Exception as e:
            print(f"Cloudflare API Error: {e}")
            return f"Error: {e}"

    # function for asking questions
    async def query(self, prompt, system_prompt: str = '', **kwargs) -> str:

        # since no caching is used and we don't want to mess with everything lightrag, pop the kwarg it is
        kwargs.pop("hashing_kv", None)

        message = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        input_ = {
            "messages": message,
            "max_tokens": self.max_tokens,
        }

        result = await self._send_request(self.llm_model_name, input_)
        return result

    #function for embedding data
    async def embedding_chunk(self, texts: list[str]) -> np.ndarray:
        print(f'''
        TEXT inputted
        ~~~~~
        {texts}
        ''')

        input_ = {
            "text": texts,
            "max_tokens": self.max_tokens
        }

        return await self._send_request(
            self.embedding_model_name,
            input_,
        )