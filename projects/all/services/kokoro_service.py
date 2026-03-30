import base64
import sounddevice as sd
import requests
from kokoro_onnx import Kokoro

class KokoroService:
    def __init__(self, config):
        self.kokoro = Kokoro(self.config.kokoro.model, self.config.kokoro.voices_path)
    
    def tts_kokoro(self, text, model_path, mood=''):
        if len(text) == 0:
            return
        if len(model_path) == 0:
            return
        
        logging.info(f"Converting text to speech: {text}")
        text = self.aify_text(text, model_path)

        print('AI:', text.strip())
        mood_model = self.npc_get_voice_mood(mood)
        try:
            if not mood_model:
                samples, sample_rate = self.kokoro.create(
                    text, voice=model_path, speed=1.0, lang="en-us"
                )
                sd.play(samples, sample_rate)
                sd.wait()
            else:
                samples, sample_rate = self.kokoro.create(
                    text, voice=mood_model, speed=1.0, lang="en-us"
                )
                sd.play(samples, sample_rate)
                sd.wait()
        except Exception as e:
            logging.error(f"An error occurred during speech playback: {str(e)}")
    
    def tts_kokoro_create_voice(self, voices):
        # TODO mix and combine voices
        pass
    