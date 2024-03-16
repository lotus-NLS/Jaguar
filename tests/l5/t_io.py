from __future__ import annotations

import time

import requests

from api import LotusRequest
from tests.spoofs import MockEntity
from hollarek.devtools import Unittest

from engine.l5_singletons.io.engine_io import IO
import threading
# --------------------------------------------

class TestEngineIO(Unittest):
    @classmethod
    def setUpClass(cls):
        IO.reset_instance()
        entity = MockEntity()
        cls.io = IO(handler=entity)
        threading.Thread(target=cls.io.run).start()
        time.sleep(3)


    def test_initialization(self):
        self.assertIsNotNone(self.io)

    def test_process_endpoint(self):
        req_str = LotusRequest().json()
        # response = self.client.post("/", content=req_str)
        url = self.io.socket.as_addr(protocol='http')
        response = requests.post(url=url,data=req_str)
        self.assertEqual(response.status_code, 200)

    # def test_transcribe_endpoint(self):
    #     payload = {
    #         "audio_content": "base64_audio_string_here"
    #     }
    #     response = self.client.post("/transcribe", json=payload)
    #     self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    TestEngineIO.execute_all()
    # req_str = LotusRequest().json()
