# from PIL.Image import Image as PILImage
# from api import Entry
# from typing import Optional
# from engine.l5_singletons.io import Task, EngineIO
# from api import LotusRequest
# import requests
# # ----------------------------------------------
#
#
# class ConsoleUser:
#     def send(self, msg : str, image : Optional[PILImage] = None):
#         req_str = LotusRequest().json()
#         response = requests.post(url=self.addr, data=req_str, stream=True)
#
#     def test_process_endpoint(self):
#         for chunk in response.iter_content(chunk_size=None):
#             print(chunk)
#         self.assertEqual(response.status_code, 200)
#
#     def test_transcribe_endpoint(self):
#         spoof_wav = FileSpoofer.lend_wav()
#         with open(spoof_wav.fpath, 'rb') as f:
#             data = f.read()
#         url = f'{self.addr}/transcribe'
#         req_str = TranscribeRequest(wav_base64=to_base64(data=data)).json()
#         response = requests.post(url,data=req_str)
#         self.assertIn(f'Four score and seven years ago'.lower(),response.text.lower())
#         print(f'Transcription output: {response.text}')
