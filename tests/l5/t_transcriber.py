from hollarek.file import FileSpoofer
from hollarek.devtools import Unittest
from engine.l0_main import Transcriber

class TestTranscriber(Unittest):
    def setUp(self):
        self.transcriber = Transcriber()

    def test_recognize_gettysburg(self):
        spoof_wav = FileSpoofer.lend_wav()

        with open(spoof_wav.fpath, 'rb') as f:
            spoof_wav_bytes = f.read()

        transcribed_text = self.transcriber.get_text(wav_bytes=spoof_wav_bytes)
        expected_transcription_text = "Four score and seven years ago"
        self.assertIn(expected_transcription_text.lower(), transcribed_text.lower())



if __name__ == '__main__':
    TestTranscriber.execute_all()
