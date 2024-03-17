from __future__ import annotations
import time
import threading
import requests
import base64
from hollarek.devtools import Unittest, FileSpoofer

from api import LotusRequest, TranscribeRequest
from tests.spoofs import MockEntity
from engine.l5_singletons.io.engine_io import IO
# --------------------------------------------

class TestEngineIO(Unittest):
    @classmethod
    def setUpClass(cls):
        IO.reset_instance()
        entity = MockEntity()
        cls.io = IO(handler=entity)
        cls.server_proc = cls.io.dev_run()
        time.sleep(0.1)
        cls.addr = cls.io.socket.as_addr(protocol='http')


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
        print(response.text)

    @classmethod
    def tearDownClass(cls):
        cls.server_proc.terminate()
        cls.server_proc.join()

def to_base64(data: bytes) -> str:
    return base64.b64encode(data).decode()


if __name__ == '__main__':
    TestEngineIO.execute_all()
    # req_str = LotusRequest().json()
