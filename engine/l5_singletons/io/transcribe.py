import time
import speech_recognition as sr
from speech_recognition import Recognizer
import whisper
import torch
import numpy as np

from sys import platform
from whisper import Whisper
from io import BytesIO
from .types import Pipe


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
        self.source = self.get_source()

        self.recorder : Recognizer = Recognizer()
        self.recorder.energy_threshold = 10000
        self.recorder.dynamic_energy_threshold = True

        self.pipes : list[Pipe] = []
        self.audio_buffer : BytesIO = BytesIO()
        self.text_buffer : str = ''
        self.stop_handle = None

    def get_output_pipe(self) -> Pipe:
        pipe = Pipe()
        self.pipes.append(pipe)
        return pipe

    def start(self):
        with self.source:
            self.recorder.adjust_for_ambient_noise(self.source)
        self.stop_handle = self.recorder.listen_in_background(source=self.source, callback=self._process_speech)

    # def _process_speech(self) -> None:
    #     print(f'Heard something')
    #     # self.audio_buffer = BytesIO()
    #     # self.audio_buffer.write(audio.get_raw_data())
    #     text = self.get_text(audio=)
    #     self.text_buffer += text
    #     for pipe in self.pipes:
    #         pipe.put(msg=text)


    def stop(self):
        print(f'Stopped listening')
        self.stop_handle(wait_for_stop = False)

    def get_text(self, audio_data : bytes):
        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
        result = self.model.transcribe(audio_np, fp16=torch.cuda.is_available())
        text = result['text'].strip()

        return text


    # --------------------------------------------

    @staticmethod
    def get_source(target_name : str = 'default'):
        mic_names = sr.Microphone.list_microphone_names()
        if 'linux' in platform:
            mic_map = {name : j for j,name in enumerate(mic_names)}
            target_index = mic_map.get(target_name)
            if target_index:
                source = sr.Microphone(sample_rate=16000, device_index=target_index)
            else:
                raise ValueError(f"Microphone with name {target_name} not found")
        else:
            source = sr.Microphone(sample_rate=16000)
        print(f'Source successfully retreived')
        return source


    @classmethod
    def get_available_mics(cls) -> list[str]:
        return sr.Microphone.list_microphone_names()





if __name__ == "__main__":
    import sounddevice as sd
    import numpy as np
    from engine.l5_singletons import Transcriber
    import speech_recognition as sr

    sr.Microphone

    duration = 4  # seconds
    fs = 16000  # Sample rate

    # Record audio

    myrecording = sd.rec(frames=int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    print("Recording...")
    sd.wait()  # Wait until recording is finished
    print("Recording finished")

    audio_bytes = myrecording.tobytes()

    print(len(myrecording))
    transcriber = Transcriber()
    print(transcriber.get_text(audio_data=audio_bytes))

    print("Playing back...")
    sd.play(myrecording, fs)
    sd.wait()  # Wait until playback is finished
