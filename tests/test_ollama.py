import unittest

import httpx

from app.llm.ollama import (
    OllamaClient,
    OllamaInvalidResponseError,
    OllamaUnavailableError,
)


class OllamaClientTest(unittest.IsolatedAsyncioTestCase):
    def client_for(self, handler):
        return OllamaClient(
            "http://ollama.internal",
            1,
            transport=httpx.MockTransport(handler),
        )

    async def test_list_models_maps_ollama_tags_response(self):
        client = self.client_for(
            lambda request: httpx.Response(
                200,
                json={"models": [{"name": "llama3.2:3b", "size": 123}]},
            )
        )

        models = await client.list_models()

        self.assertEqual(models[0]["name"], "llama3.2:3b")

    async def test_chat_sends_non_streaming_request_and_returns_text(self):
        def handler(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.url.path, "/api/chat")
            self.assertIn(b'"stream":false', request.content)
            return httpx.Response(200, json={"message": {"content": "안녕하세요"}})

        response = await self.client_for(handler).chat(
            model="llama3.2:3b", message="hello"
        )

        self.assertEqual(response, "안녕하세요")

    async def test_unexpected_payload_raises_clear_error(self):
        client = self.client_for(lambda request: httpx.Response(200, json={}))

        with self.assertRaises(OllamaInvalidResponseError):
            await client.list_models()

    async def test_http_error_is_reported_as_unavailable(self):
        client = self.client_for(lambda request: httpx.Response(503))

        with self.assertRaises(OllamaUnavailableError):
            await client.list_models()
