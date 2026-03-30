from io import BytesIO
import base64
import sounddevice as sd
import requests

class ZonosService:
    def tts_zonos(self, text, npc, model_path='', mood=''):
        if len(text) == 0:
            return
        if len(npc) == 0:
            return
        # if len(voice) == 0:
        #     return
        logging.info(f"Converting text to speech: {text}")
        mood_model = self.npc_get_voice_mood(mood)
        lines = []
        if not mood_model:
            lines = list(
                map(
                    lambda l: { "line":l, "name": model_path },  
                    text.split(r"?<!\w\.\w.)(?<!\b[A-Z][a-z]\.)(?<![A-Z]\.)(?<=\.|\?)\s|\\n))"))
                )
        else:
            lines = list(
                map(
                    lambda l: { "line":l, "name": mood_model },  
                    text.split(r"?<!\w\.\w.)(?<!\b[A-Z][a-z]\.)(?<![A-Z]\.)(?<=\.|\?)\s|\\n))"))
                )

        url = self.config.zonos.url
        data = { "lines": lines }

        # Fetch array of actions from API
        response = requests.post(url, verify=False, json=data)
        res = json.loads(response.text)

        if "refs" in res:
            try:
                for voice_file in res["refs"]:
                    # buffered = BytesIO()                
                    samples = base64.b64decode(voice_file["file64"].encode('ascii'))
                    audio_data, samplerate = sf.read(BytesIO(samples), dtype='float32')
                    sample_rate = int(voice_file["sampling_rate"])
                    sd.play(audio_data, 44100)
                    sd.wait()
            except Exception as e:
                logging.error(f"An error occurred during speech playback: {str(e)}")
    