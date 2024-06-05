from __future__ import annotations
import time
import requests
import base64
from holytools.devtools import Unittest
from holytools.file import FileMock

from api import LotusRequest, TranscribeRequest
from tests.spoofs import MockEntity
from engine.l0_main import DevServer
# --------------------------------------------

class TestEngineIO(Unittest):
    @classmethod
    def setUpClass(cls):
        io = DevServer(handler=MockEntity())
        io.run()
        cls.addr = io.socket.as_addr(protocol='http')
        cls.io = io
        time.sleep(0.1)

    def test_initialization(self):
        self.assertIsNotNone(self.io)

    def test_process_endpoint(self):
        req_str = LotusRequest().model_dump_json()
        process_endpoint = self.io.get_process_endpoint()
        url = f'{self.addr}{process_endpoint.path}'
        response = requests.post(url=url, data=req_str, stream=True)
        for chunk in response.iter_content(chunk_size=None):
            print(chunk)
        self.assertEqual(response.status_code, 200)

    def test_transcribe_endpoint(self):
        spoof_wav = FileMock.lend_wav()
        with open(spoof_wav.fpath, 'rb') as f:
            data = f.read()
        url = f'{self.addr}/transcribe'
        req_str = TranscribeRequest(wav_base64=to_base64(data=data)).model_dump_json()
        response = requests.post(url,data=req_str)
        self.assertIn(f'Four score and seven years ago'.lower(),response.text.lower())
        print(f'Transcription output: {response.text}')

    # noinspection PyUnresolvedReferences
    @classmethod
    def tearDownClass(cls):
        cls.io.kill()


def to_base64(data: bytes) -> str:
    return base64.b64encode(data).decode()

if __name__ == '__main__':
    TestEngineIO.execute_all()
    # req_str = LotusRequest().model_dump_json()
