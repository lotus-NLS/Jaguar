import threading

from PIL.Image import Image as PILImage
from typing import Optional
from api import LotusRequest, TranscribeRequest
import requests
from requests import Response
from hollarek.file import ImageSerializer
from engine.l5_singletons import EngineIO, Recorder
from base64 import b64encode
# ----------------------------------------------


class DevUser:
    def __init__(self, engineIO : EngineIO):
        self.engine_io : EngineIO = engineIO
        self.buffer : str = ''
        self.recorder : Recorder = Recorder()
        threading.Thread(target=self.listen).start()


    def add_input(self, msg : str):
        self.buffer += msg
        print(msg, end='')

    def fire(self) -> Response:
        return self.write(msg=self.buffer)

    def write(self, msg : str, image : Optional[PILImage] = None):
        if image:
            image = ImageSerializer.as_base64_str(image=image)
        req_str = LotusRequest(msg=msg, img=image).json()

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
                self.write(msg=response.text)


def to_base64(data: bytes) -> str:
    return b64encode(data).decode()
