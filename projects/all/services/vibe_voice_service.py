# use https://github.com/vibevoice-community/VibeVoice-API
from openai import OpenAI

base_path = "/v1"  # or your VIBEVOICE_API_BASE_PATH
# client = OpenAI(base_url=f"http://127.0.0.1:8000{base_path}", api_key="<YOUR_API_KEY>")

class VibeVoiceService:
    def __init__(self, config):
        self.config = config
        self.client = OpenAI(base_url=self.config.vibe_voice.path)
    
    def tts_vibe_voice(text, character, mood_model):
        speech = client.audio.speech.create(
            model="vibevoice/VibeVoice-1.5B",
            voice=character,
            input=text,
            response_format="wav")
        try:
            logging.info("Initializing VIVE VOICE TTS engine")
            logging.info("-------- TTS ---------")  
            
            stream = sd.OutputStream(samplerate=44100, channels=1, dtype='int16')
            stream.start()
            bytes = speech.read()
           
            int_data = np.frombuffer(chunk.audio_int16_bytes, dtype=np.int16)             
            stream.write(int_data)

            stream.stop()
            stream.close()
            logging.info("Speech playback completed")
        except Exception as e:
            logging.error(f"An error occurred during speech playback: {str(e)}")


with open("out.wav", "wb") as f:
    f.write(speech.read())