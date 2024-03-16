from typing import BinaryIO

import speech_recognition as sr
from .types import Pipe
from openai import OpenAI
from engine.l5_singletons import LotusSettings
import tempfile


class Transcriber:
    def __init__(self):
        self.client = OpenAI(api_key=LotusSettings().get_openai_apikey())
        self.recognizer = sr.Recognizer()
        self.recognizer.non_speaking_duration = 0.1
        self.recognizer.pause_threshold = 0.2
        self.recognizer.energy_threshold = 750

        self.pipes : list[Pipe] = []
        self.text_buffer : str = ''

    def register_pipe(self) -> Pipe:
        pipe = Pipe()
        self.pipes.append(pipe)
        return pipe

    def start(self):
        while True:
            with sr.Microphone() as source:
                audio_data = self.recognizer.listen(source)
            try:
                text = self.get_text(wav_bytes=audio_data.get_wav_data())
                print(f"You said: {text}")
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")


    def get_text(self, wav_bytes : bytes):
        wav_io = self.to_wav(audio_data=wav_bytes)
        transcription = self.client.audio.transcriptions.create(model="whisper-1", file=wav_io)
        wav_io.close()
        return transcription.text


    @staticmethod
    def to_wav(audio_data : bytes) -> BinaryIO:
        temp_file_fd, temp_file_path = tempfile.mkstemp(suffix=".wav")
        with open(temp_file_path, 'wb') as f:
            f.write(audio_data)
        return open(temp_file_path, 'rb')





if __name__ == "__main__":
    transcriber = Transcriber()
    transcriber.start()