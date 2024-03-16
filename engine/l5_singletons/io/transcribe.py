from typing import BinaryIO, Optional

import speech_recognition as sr
from queue import Queue
from openai import OpenAI
import tempfile
from engine.l5_singletons.settings import LotusSettings
from .pipes import BytePipe


class Recorder:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.non_speaking_duration = 0.1
        self.recognizer.pause_threshold = 0.2
        self.recognizer.energy_threshold = 750

        self.is_running : bool = False
        self.pipes: list[BytePipe] = []

    def register_pipe(self) -> Queue[bytes]:
        pipe = BytePipe()
        self.pipes.append(pipe)
        return pipe

    def start(self):
        with sr.Microphone() as source:
            self.listen(source=source)

    def stop(self):
        self.is_running = False

    def listen(self, source : sr.AudioSource):
        while True:
            if not self.is_running:
                break
            audio_data = self.recognizer.listen(source)
            wav_bytes = audio_data.get_wav_data()
            for pipe in self.pipes:
                pipe.put(wav_bytes)


class Transcriber:
    def __init__(self):
        self.client = OpenAI(api_key=LotusSettings().get_openai_apikey())
        self.text_buffer : str = ''

    def get_text(self, wav_bytes : bytes) -> Optional[str]:
        wav_io = self.to_wav(audio_data=wav_bytes)
        try:
            transcription = self.client.audio.transcriptions.create(model="whisper-1", file=wav_io)
            return transcription.text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
        finally:
            wav_io.close()


    @staticmethod
    def to_wav(audio_data : bytes) -> BinaryIO:
        temp_file_fd, temp_file_path = tempfile.mkstemp(suffix=".wav")
        with open(temp_file_path, 'wb') as f:
            f.write(audio_data)
        return open(temp_file_path, 'rb')



if __name__ == "__main__":
    transcriber = Transcriber()