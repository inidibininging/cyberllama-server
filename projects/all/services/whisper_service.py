import requests
import logging

TALK_START_CMD=1
TALK_DONE_CMD=2
TALK_LISTEN_CMD=3
SHUTUP_CMD=0

class WhisperService:
    def __init__(self, config):
        self.config = config
        self.current_cmd = SHUTUP_CMD
        self.max_stat_tries = 3

    def rec_start(self):
        
        if self.current_cmd == TALK_LISTEN_CMD:
            raise 'TALK_LISTEN_CMD'
        self.current_cmd = TALK_LISTEN_CMD
        
        return requests.post(self.config.whisper.url+'/listen', verify=False, json={})
    
    def rec_stop(self):
        
        if self.current_cmd == TALK_DONE_CMD:
           raise "TALK_DONE_CMD"
        self.current_cmd = TALK_DONE_CMD

        response = requests.post(self.config.whisper.url+'/stop', verify=False, json={})
        # TODO: check if pending

        tries = self.max_stat_tries
        whisper_data = response.json()

        while tries > 0:
            tries = tries - 1
            time.sleep(2)                  
            response = requests.post(cyberllama.config.whisper.url+'/stat', verify=False, json={})
            whisper_data = response.json()
            if "text" in whisper_data and \
                "state" in whisper_data and \
                "message" in whisper_data and \
                whisper_data["state"] == '1' and \
                whisper_data["message"] == 'stat':
                tries = 0
        
        return whisper_data["text"]

    