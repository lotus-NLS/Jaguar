# from typing import BinaryIO, Optional
#
# # import speech_recognition as sr
# from openai import OpenAI
# import tempfile
# from engine.l5_settings import LotusSettings
#
#
# class Transcriber:
#     def __init__(self):
#         self.client = OpenAI(api_key=LotusSettings().get_openai_apikey())
#         self.text_buffer : str = ''
#
#     def get_text(self, wav_bytes : bytes) -> Optional[str]:
#         wav_io = self.to_wav(audio_data=wav_bytes)
#         try:
#             transcription = self.client.audio.transcriptions.create(model="whisper-1", file=wav_io)
#             return transcription.text
#         except sr.UnknownValueError:
#             print("Google Speech Recognition could not understand audio")
#         except sr.RequestError as e:
#             print(f"Could not request results from Google Speech Recognition service; {e}")
#         finally:
#             wav_io.close()
#
#
#     @staticmethod
#     def to_wav(audio_data : bytes) -> BinaryIO:
#         temp_file_fd, temp_file_path = tempfile.mkstemp(suffix=".wav")
#         with open(temp_file_path, 'wb') as f:
#             f.write(audio_data)
#         return open(temp_file_path, 'rb')