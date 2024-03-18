from PIL.Image import Image as PILImage
from typing import Optional
from api import LotusRequest
import requests
from requests import Response
from hollarek.file import ImageSerializer
from engine.l5_singletons import EngineIO, Recorder
# ----------------------------------------------


class DevUser:
    def __init__(self, engineIO : EngineIO):
        self.engine_io : EngineIO = engineIO
        self.buffer : str = ''
        self.recorder : Recorder = Recorder()

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