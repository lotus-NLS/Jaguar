import speech_recognition as sr
import whisper
import torch
import numpy as np

from whisper import Whisper
from api.communication.messages import Pipe


class ModelDownloader:
    @classmethod
    def get_tiny(cls) -> Whisper:
        return whisper.load_model('tiny')

    @classmethod
    def get_base(cls) -> Whisper:
        return whisper.load_model('base')

    @classmethod
    def get_small(cls) -> Whisper:
        return whisper.load_model('small')

    @classmethod
    def get_medium(cls) -> Whisper:
        return whisper.load_model('medium')

    @classmethod
    def get_large(cls) -> Whisper:
        return whisper.load_model('large')


class Transcriber:
    def __init__(self, model : Whisper = ModelDownloader.get_tiny()):
        self.model : Whisper =  model

        self.recognizer = sr.Recognizer()
        self.recognizer.non_speaking_duration = 0.3
        self.recognizer.pause_threshold = 0.1

        self.pipes : list[Pipe] = []
        self.text_buffer : str = ''

    def get_output_pipe(self) -> Pipe:
        pipe = Pipe()
        self.pipes.append(pipe)
        return pipe

    def start(self):
        while True:
            with sr.Microphone() as source:
                audio_data = self.recognizer.listen(source)
            try:
                text = self.recognizer.recognize_google(audio_data)
                print(f"You said: {text}")
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")


    def get_text(self, audio_data : bytes):
        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
        result = self.model.transcribe(audio_np, fp16=torch.cuda.is_available())
        text = result['text'].strip()

        return text




if __name__ == "__main__":
    transcriber = Transcriber()
    transcriber.start()