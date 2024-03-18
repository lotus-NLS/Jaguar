import threading
import requests
from api import LotusRequest, TranscribeRequest
from hollarek.hardware import Recorder
from base64 import b64encode
from .server import Server
# ----------------------------------------------


class DevUser:
    def __init__(self, engineIO : Server, use_misc : bool = False):
        self.engine_io : Server = engineIO
        self.buffer : str = ''
        if use_misc:
            self.recorder : Recorder = Recorder()
            self.recorder.start()
            threading.Thread(target=self.listen).start()

    def add_input(self, msg : str):
        self.buffer += msg

    def fire(self):
        req_str = LotusRequest(msg=self.buffer).json()

        process_endpoint = self.engine_io.get_process_endpoint()
        url = process_endpoint.get_url(protocol=self.engine_io.get_protocol())
        return requests.post(url=url, data=req_str, stream=True)

    def listen(self):
        audio_pipe = self.recorder.register_pipe()

        while True:
            audio_data = audio_pipe.get()
            wav_base64 = to_base64(data=audio_data)
            req_str = TranscribeRequest(wav_base64=wav_base64).json()
            transcribe_endpoint = self.engine_io.get_transcribe_endpoint()

            url = transcribe_endpoint.get_url(protocol=self.engine_io.get_protocol())
            response = requests.post(url=url, data=req_str)
            if response.status_code == 200:
                print(response.text, end='')
                self.add_input(msg=response.text)


def to_base64(data: bytes) -> str:
    return b64encode(data).decode()
