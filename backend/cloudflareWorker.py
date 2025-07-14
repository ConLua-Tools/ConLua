# api call for cloudflare

import requests

class CloudflareWorker:
    def __init__(self, cloudflare_api_key: str, api_base_url: str, llm_model_name: str):
        self.cloudflare_api_key = cloudflare_api_key
        self.api_base_url = api_base_url
        self.llm_model_name = llm_model_name
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

            return "Error: No response from Cloudflare"

        except Exception as e:
            print(f"Cloudflare API Error: {e}")
            return f"Error: {e}"

    async def query(self, prompt: str, system_prompt: str = '') -> str:
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
