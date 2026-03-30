# import pyaudio
import wave
import soundfile as sf
import numpy as np
# needs => apt-get install portaudio19-dev
import base64
import sounddevice as sd
import requests
import sys
import os
from piper.voice import PiperVoice, SynthesisConfig
import logging
if sys.platform == 'win32' or os.environ.get('OS','') == 'Windows_NT':
    from phonemizer.backend.espeak.wrapper import EspeakWrapper
    import pyaudio
    EspeakWrapper.set_library('C:\\Program Files\\eSpeak NG\\libespeak-ng.dll')

class PiperService:
    def __init__(self,config,mood_service):
        self.config = config
        self.mood_service = mood_service

    # def tts_piper_get_gender_speaker_id_by_tags(self, gender, tags=[]):
    #     if gender == 'female':
    #         gender = 'v_output_f_map'
    #     elif gender == 'male':
    #         gender = 'v_output_m_map'
    #     else:
    #         return 0
    #     conn = sqlite3.connect(self.config.piper.multi_voice.libritts_r.dataset)
    #     cur = conn.cursor()        
    #     where_sql = ''
    #     if len(tags) > 0:
    #         where_sql = "where " + " and ".join(list(map(lambda tag: "m.tags like '%" + tag + "%'", tags)))        
    #     sql = "select m.speaker_id, m.tags from " + gender + " m " + where_sql
    #     rc = cur.execute(sql)
    #     res = rc.fetchall()
    #     conn.close()
    #     lres = len(res)
    #     if lres == 1:
    #         return int(res[0][COL_SPEAKER_ID])
    #     if lres > 0:
    #         return int(res[random.randrange(0, len(res))][COL_SPEAKER_ID])
    #     return 0

    def tts_piper_win(self, text, model_path='', mood='', sample_rate=22000):
        # i get this weird error, that piper doesnt have the synthesize_stream_raw function
        # this is a work around as long as this error persists on windows (10)
        if(model_path == ''):
            model_path = self.config.piper.model

        logging.info(f"Converting text to speech: {text}")
        text = self.aify_text(text, model_path)
        try:
            logging.info("Initializing PIPER TTS engine")
            logging.info("-------- TTS ---------")
            
            os.system("python -m piper -m " + model_path + " -f output.wav -- '" + self.clean_text(text) + "'")
            with wave.open("output.wav", 'rb') as wfile:
                p = pyaudio.PyAudio()
                stream = p.open(format = p.get_format_from_width(wfile.getsampwidth()),  
                channels = wfile.getnchannels(),  
                rate = wfile.getframerate(),  
                output = True)
                data = wfile.readframes(1024)  
                while data:  
                    stream.write(data)
                    data = wfile.readframes(1024)
                stream.stop_stream()  
                stream.close()  
                p.terminate()
            logging.info("Speech playback completed")
        except Exception as e:
            logging.error(f"An error occurred during speech playback: {str(e)}")

    def tts_piper(self, text, model_path='', mood='', sample_rate=22000, speaker_id=0):
        if(model_path == ''):
            model_path = self.config.piper.player_model
        if len(text) == 0:
            return
        logging.info(f"Converting text to speech: {text}")
        
        # if sys.platform == 'win32' or os.environ.get('OS','') == 'Windows_NT':
        #     self.tts_piper_win(text, model_path, mood, sample_rate)
        #     return
        
        mood_model = self.mood_service.npc_get_voice_mood(mood)
        try:
            logging.info("Initializing PIPER TTS engine")
            logging.info("-------- TTS ---------")  
            # voices https://tderflinger.github.io/piper-docs/codereading/python_run/piper/http_server/
            # speaker_id
            piper_model = model_path
            if mood_model != None and len(mood_model.trim()) != 0:
                piper_model = mood_model
            # gpu
            # install using "pip install -r requirements_piper_gpu.txt"
            piper = PiperVoice.load(piper_model, use_cuda=self.config.piper.use_gpu)
            stream = sd.OutputStream(samplerate=sample_rate, channels=1, dtype='int16')
            stream.start()
            audio_bytes_arr = None
            
            syn_config = SynthesisConfig(speaker_id=speaker_id, volume=0.5)
            for chunk in piper.synthesize(text, syn_config):
                int_data = np.frombuffer(chunk.audio_int16_bytes, dtype=np.int16)             
                stream.write(int_data)

            stream.stop()
            stream.close()
            logging.info("Speech playback completed")
        except Exception as e:
            logging.error(f"An error occurred during speech playback: {str(e)}")