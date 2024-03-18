from __future__ import annotations
import time
import requests
import base64
from hollarek.devtools import Unittest
from hollarek.file import FileSpoofer

from api import LotusRequest, TranscribeRequest
from tests.spoofs import MockEntity
from engine.l5_singletons.io.engine_io import EngineIO
# --------------------------------------------

class TestEngineIO(Unittest):
    # noinspection PyUnresolvedReferences
    @classmethod
    def setUpClass(cls):
        EngineIO.reset_instance()
        cls.io = EngineIO(handler=MockEntity())
        cls.io.dev_run()
        cls.addr = cls.io.socket.as_addr(protocol='http')
        time.sleep(0.1)

    def test_initialization(self):
        self.assertIsNotNone(self.io)

    def test_process_endpoint(self):
        req_str = LotusRequest().json()
        response = requests.post(url=self.addr, data=req_str, stream=True)
        for chunk in response.iter_content(chunk_size=None):
            print(chunk)
        self.assertEqual(response.status_code, 200)

    def test_transcribe_endpoint(self):
        spoof_wav = FileSpoofer.lend_wav()
        with open(spoof_wav.fpath, 'rb') as f:
            data = f.read()
        url = f'{self.addr}/transcribe'
        req_str = TranscribeRequest(wav_base64=to_base64(data=data)).json()
        response = requests.post(url,data=req_str)
        self.assertIn(f'Four score and seven years ago'.lower(),response.text.lower())
        print(f'Transcription output: {response.text}')

    # noinspection PyUnresolvedReferences
    @classmethod
    def tearDownClass(cls):
        cls.io.dev_kill()


def to_base64(data: bytes) -> str:
    return base64.b64encode(data).decode()

if __name__ == '__main__':
    TestEngineIO.execute_all()
    # req_str = LotusRequest().json()
