from __future__ import annotations

from hollarek.devtools import Unittest
from tests.spoofs import MockEntity
from fastapi.testclient import TestClient

from engine.l5_singletons.io.engine_io import IO

# --------------------------------------------

class TestEngineIO(Unittest):
    def setUp(self):
        IO.reset_instance()
        self.entity = MockEntity()
        self.io = IO(handler=self.entity)
        self.client = TestClient(self.io.app)

    def test_initialization(self):
        self.assertIsNotNone(self.io)


    def test_process_endpoint(self):
        payload = {
            "user_id": "test_id",
            "bool_content": True,
            "msg": ["Hello, World!"],
            "img": None
        }
        response = self.client.post("/", json=payload)
        self.assertEqual(response.status_code, 200)

    def test_transcribe_endpoint(self):
        payload = {
            "audio_content": "base64_audio_string_here"
        }
        response = self.client.post("/transcribe", json=payload)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    TestEngineIO.execute_all()
