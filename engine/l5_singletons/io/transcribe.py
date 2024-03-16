import speech_recognition as sr
from .types import Pipe
from openai import OpenAI
from engine.l5_singletons import LotusSettings

class Transcriber:
    def __init__(self):
        self.client = OpenAI(api_key=LotusSettings.get_openai_apikey())
        self.recognizer = sr.Recognizer()
        self.recognizer.non_speaking_duration = 0.3
        self.recognizer.pause_threshold = 0.1

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
                audio_data.get_raw_data()
            try:
                text = self.get_text(audio_data=audio_data)
                print(f"You said: {text}")
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")


    def get_text(self, audio_data : bytes):
        transcription = self.client.audio.transcriptions.create(model="whisper-1", file=audio_data)
        return transcription.text



if __name__ == "__main__":
    transcriber = Transcriber()
    transcriber.start()