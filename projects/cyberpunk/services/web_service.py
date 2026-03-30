import json
import logging
import uuid
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from urllib.parse import parse_qsl, urlparse

from projects.all.services.whisper_service import TALK_START_CMD, TALK_DONE_CMD, TALK_LISTEN_CMD, SHUTUP_CMD

from projects.cyberpunk.services.sqlite3_cache_service import COL_ID, COL_CHARACTER, COL_LINE, COL_PARENT, COL_LOCATION, COL_FACTION, COL_MOOD
from projects.cyberpunk.models.world_data import WorldData

global CURRENT_CMD
global CURRENT_POST_DATA


# lazyness
# global self.last_v_responses

CURRENT_CMD = SHUTUP_CMD
CURRENT_POST_DATA = {}

PROMPT_TTS_PLAYER_FEED=0
PROMPT_TTS_NPC_FEED=1
PROMPT_NPC_GENERATE_LINES=2
PROMPT_DONE=3
CURRENT_PROMPT_STATE = PROMPT_DONE
PROMPT_LAST_TURN=PROMPT_TTS_PLAYER_FEED

def set_cyberllama(cyberllama, server):
    server.cyberllama = cyberllama

class WebService(BaseHTTPRequestHandler):

    def get_clean_prompt(self, CURRENT_POST_DATA):
        cleaned_t = ''
        if CURRENT_POST_DATA == None:
            return ''
        for character in CURRENT_POST_DATA:
            if character.isalnum() \
                or character == '.' \
                or character == "'" \
                or character == '!' \
                or character == ' ' \
                or character == ',\n' \
                or character == ',' \
                or character == '?':
                cleaned_t += character
        cleaned_t = cleaned_t.replace('*', '')
        return cleaned_t    
    
    def on_comment(self, data, dataj):
        global CURRENT_CMD        
        
        global CURRENT_POST_DATA
        
        CURRENT_POST_DATA = {}
        if not self.on_prompt_ceremony(data, dataj):
            self.send_OK({})        
        
        comment = ''
        if(CURRENT_POST_DATA['prompt'] == 'location'):
            comment = self.server.cyberllama.cyber_prompt_service.get_lazy_reaction_from_location(
                CURRENT_POST_DATA['prompt_args'], 
                world_data.npc_tweaks_name, 
                world_data, 
                world_data.quest_name)

        elif (CURRENT_POST_DATA['prompt'] == 'stats'):
            comment = self.server.cyberllama.comment_service.gen_stats_comment(
                self.server.cyberllama.world_data.food,
                self.server.cyberllama.world_data.hydration, 
                self.server.cyberllama.world_data.fun,
                self.server.cyberllama.world_data.relationship,
                self.server.cyberllama.world_data.npc_tweaks_name,
                self.server.cyberllama.world_data.npc_backstory)

        elif (CURRENT_POST_DATA['prompt'] == 'health'):
            comment = self.server.cyberllama.comment_service.gen_health(
                self.server.cyberllama.world_data.health, 
                self.server.cyberllama.world_data.max_health, 
                self.server.cyberllama.world_data.armor, 
                self.server.cyberllama.world_data.time, 
                self.server.cyberllama.world_data.npc_tweaks_name, 
                self.server.cyberllama.world_data.npc_backstory)

        elif (CURRENT_POST_DATA['prompt'] == 'quest'):
            comment = self.server.cyberllama.comment_service.gen_quest(
                self.server.cyberllama.world_data.quest_name,
                self.server.cyberllama.world_data.quest_objective, 
                self.server.cyberllama.world_data.time,                    
                self.server.cyberllama.world_data.npc_tweaks_name,
                self.server.cyberllama.world_data.npc_backstory)
        
        elif (CURRENT_POST_DATA['prompt'] == 'district'):
            comment = self.server.cyberllama.comment_service.gen_district(
                self.server.cyberllama.world_data.district,
                self.server.cyberllama.world_data.sub_district, 
                self.server.cyberllama.world_data.time,
                self.server.cyberllama.world_data.npc_tweaks_name,
                self.server.cyberllama.world_data.npc_backstory)
            
        # if len(comment) != 0:
        #     self.server.cyberllama.npc_speak(
        #         comment, 
        #     )
        self.send_OK({
            "text" : comment if len(comment) != 0 else ""
        })

    def on_expand(self, data, dataj):
        global CURRENT_CMD        
        
        global CURRENT_POST_DATA
        print(data)
        topic = self.get_clean_prompt(dataj.get('prompt'))
        topics = self.server.cyberllama.expand_topic(topic)                
        self.send_OK({
            "actions": topics, 
            "mood": 0, 
            "expression": '',
            "food": 0, 
            "hydration": 0,
            "fun": 0,
            "relationship": 0,
            'last_action': ''
        })

    # ONLY USED BY NPCS
    # IF ITS USED BY V => NEED TO CHECK IF I MEAN V OR NPC 
    def on_aify(self, data, dataj):
        global CURRENT_CMD        
        
        global CURRENT_POST_DATA
        print(data)
        CURRENT_POST_DATA = dataj
        topic = self.server.cyberllama.cleaner_service.get_clean_prompt(dataj.get('prompt'))
        
        world_data = self.server.cyberllama.world_data.make_world_data(
            dataj.get('stats'),
            dataj.get('npc', {}), 
            self.server.cyberllama)
        forced_needle = [topic]
        
        cleaned_t = self.server.cyberllama.aify_text(topic, forced_needle, world_data.npc_display_name, post_data=CURRENT_POST_DATA)
        
        try:
            self.server.cyberllama.world_data.sync_npc_data(self.server.cyberllama, world_data)
        except Exception as e:
            logging.error(str(e))

        self.server.cyberllama.world_data = world_data

        self.send_OK({
            "text": cleaned_t
        })

     
    def on_prompt_ceremony(self, data, dataj):
        print("on_prompt_ceremony")
        global CURRENT_CMD
        global CURRENT_POST_DATA
        CURRENT_POST_DATA = {}        
        cleaned_t = self.server.cyberllama.cleaner_service.get_clean_prompt(dataj.get('prompt'))
        
        if self.on_nevermind(cleaned_t):
            logging.info("Nevermind engaged")
            return False
            # raise 'nevermind'

        CURRENT_POST_DATA['prompt'] = cleaned_t
        CURRENT_POST_DATA['prompt_args'] = dataj.get('prompt_args')
        world_data = WorldData().make_world_data(
            dataj.get('stats'),
            dataj.get('npc', {}),
            self.server.cyberllama)

        sync_success = False
        try:
            # TODO: FIX THIS . DUNNO WHICH WORLD_DATA IS THE RIGHT ONE
            self.server.cyberllama.world_data.sync_npc_data(self.server.cyberllama, world_data)
            sync_success = True
        except Exception as e:
            logging.error(str(e))
            
        self.server.cyberllama.world_data = world_data
        return sync_success

        # cleaned_t = self.server.cyberllama.aify_text(cleaned_t, world_data.npc_voice_arg)

    def on_recstart(self, data, dataj):
        global CURRENT_CMD
        global CURRENT_POST_DATA
        if CURRENT_CMD == TALK_LISTEN_CMD:
            self.send_OK({
                "error":"TALK_LISTEN_CMD"
            })
        
        world_data = self.server.cyberllama.world_data.make_world_data(
            dataj.get('stats'),
            dataj.get('npc', {}), 
            self.server.cyberllama)

        if world_data and \
            world_data.npc_record_id_hash and \
            self.server.cyberllama.world_data and \
            self.server.cyberllama.world_data.npc_record_id_hash and \
            world_data.npc_record_id_hash != self.server.cyberllama.world_data.npc_record_id_hash:
            ''' npc changed '''
            print('NPC changed!')                    
        else:
            self.server.cyberllama.world_data = world_data                    
        
        CURRENT_CMD = TALK_LISTEN_CMD
        self.server.cyberllama.v_random_filler()
        response = requests.post(self.server.cyberllama.config.whisper.url+'/listen', verify=False, json={})
        
        self.send_OK(response.json())

    def on_recstop(self, data, dataj):
        global CURRENT_CMD
        
        global CURRENT_POST_DATA
        if CURRENT_CMD == TALK_DONE_CMD:
            self.send_OK({
                "error":"TALK_DONE_CMD"
            })
        CURRENT_CMD = TALK_DONE_CMD

        response = requests.post(self.server.cyberllama.config.whisper.url+'/stop', verify=False, json={})
        # TODO: check if pending

        tries = 3
        whisper_data = response.json()

        while tries > 0:
            tries = tries - 1
            time.sleep(2)                  
            response = requests.post(self.server.cyberllama.config.whisper.url+'/stat', verify=False, json={})
            whisper_data = response.json()
            if "text" in whisper_data and \
                "state" in whisper_data and \
                "message" in whisper_data and \
                whisper_data["state"] == '1' and \
                whisper_data["message"] == 'stat':
                tries = 0
        
        dataj["prompt"] = whisper_data["text"]
        dataj["prompt_args"] = ''
        self.on_prompt_continue_2(data, dataj)

    def on_nevermind(self, prompt):
        if prompt == 'Nevermind':
            self.server.cyberllama.last_v_responses = []
            self.send_OK({
                "actions": [], 
                "mood": 0, 
                "food": 0, 
                "hydration": 0,
                "fun": 0,
                "relationship": 0,
                "last_action": ''
            })
            return True
        else:
            return False
        
    def on_npc_sync(self, data, dataj):
        print(data)
        global CURRENT_PROMPT_STATE
        global CURRENT_POST_DATA
        # first 
        if not self.on_prompt_ceremony(dataj.get('npc'), dataj):
           self.send_OK({
            "error": "on_prompt_ceremony"
           })
        self.send_OK({})
  
    def on_prompt_continue_2(self, data, dataj):
        print(data)
        global CURRENT_PROMPT_STATE
        global CURRENT_POST_DATA
        global PROMPT_LAST_TURN
        # first 
        if not self.on_prompt_ceremony(dataj.get('npc'), dataj):
            return

        npc_cache = {
            "food": 0,
            "hydration": 0,
            "fun": 0,
            "relationship": 0
        }        
        
        if self.server.cyberllama.player_feed == None:
            self.server.cyberllama.player_feed = []
        
        if self.server.cyberllama.npc_feed == None:
            self.server.cyberllama.player_feed = []

        if self.server.cyberllama.world_data.npc_changed:
           # clear 
           CURRENT_PROMPT_STATE = PROMPT_TTS_PLAYER_FEED
           # add something if the npc feed is not finished (npc got interrupted)
           # NICE_TO_HAVE: maybe add lines here and a dialog for continuing the dialog (maybe with a prompt "summarize as if you were to remember what we were talking about (add v last dialog + the content of the last dialog)"?)
           # this could also be a menu entry "(last conversation)" in the mod
           # also remove the content if it was X minutes ago
           self.server.cyberllama.all_player_lines = ''
           self.server.cyberllama.all_npc_feed_lines = ''
           self.server.cyberllama.player_feed = []
           self.server.cyberllama.npc_feed = []
        #    NEW HERE CHECK ME UP IF WRONG
           self.server.cyberllama.cached_conversation_lines = []

           if self.server.cyberllama.world_data.npc_id_hash and self.server.cyberllama.world_data.npc_id_hash in self.server.cyberllama.npc_cache:
                npc_cache["food"] = self.server.cyberllama.npc_cache[self.server.cyberllama.world_data.npc_id_hash]['food']
                npc_cache["hydration"] = self.server.cyberllama.npc_cache[self.server.cyberllama.world_data.npc_id_hash]['hydration']
                npc_cache["fun"] = self.server.cyberllama.npc_cache[self.server.cyberllama.world_data.npc_id_hash]['fun']
                npc_cache["relationship"] = self.server.cyberllama.npc_cache[self.server.cyberllama.world_data.npc_id_hash]['relationship']
        #    self.server.cyberllama.v_speak("Interrupt")
        else:
            npc_cache["food"] = self.server.cyberllama.world_data.food
            npc_cache["hydration"] = self.server.cyberllama.world_data.hydration
            npc_cache["fun"] = self.server.cyberllama.world_data.fun
            npc_cache["relationship"] = self.server.cyberllama.world_data.relationship
            if CURRENT_PROMPT_STATE == PROMPT_DONE:
                CURRENT_PROMPT_STATE = PROMPT_TTS_PLAYER_FEED
                # if PROMPT_LAST_TURN == PROMPT_TTS_PLAYER_FEED:
                #     CURRENT_PROMPT_STATE = PROMPT_TTS_NPC_FEED
                # else:
                #     CURRENT_PROMPT_STATE = PROMPT_TTS_PLAYER_FEED

                self.server.cyberllama.all_player_lines = ''
                self.server.cyberllama.all_npc_feed_lines = ''
                self.server.cyberllama.player_feed = []
                self.server.cyberllama.npc_feed = []
                # self.send_OK({
                #     "actions": [], 
                #     "mood": None, 
                #     "expression": None,
                #     "food": npc_cache["food"],
                #     "hydration": npc_cache["hydration"],
                #     "fun": npc_cache["fun"],
                #     "relationship": npc_cache["relationship"],
                #     'last_action': self.server.cyberllama.world_data.last_action,
                #     "v_intentions": None,
                #     "npc_intentions": None,
                #     "v_subtitles": self.server.cyberllama.player_feed,
                #     "npc_subtitles": self.server.cyberllama.npc_feed,
                #     "state": CURRENT_PROMPT_STATE
                # })
                # return 
                self.server.cyberllama.v_random_filler()
                # TODO
                # self.server.cyberllama.zip_conversation()


        contains_prompt = len(CURRENT_POST_DATA['prompt']) > 0
        if CURRENT_PROMPT_STATE == PROMPT_TTS_PLAYER_FEED:
            feed_length = len(self.server.cyberllama.player_feed)
            if self.server.cyberllama.player_feed and feed_length > 0:
                # continue feeding v answers 
                if contains_prompt:
                    # self.server.cyberllama.all_player_lines = CURRENT_POST_DATA['prompt']
                    self.server.cyberllama.all_player_lines = self.server.cyberllama.aify_text(CURRENT_POST_DATA['prompt'], self.server.cyberllama.world_data.npc_voice_arg)
                    self.server.cyberllama.cached_conversation_lines.append((
                        str(uuid.uuid4()),
                        'V',
                        self.server.cyberllama.all_player_lines,
                    ))
                
                last_v_line = self.server.cyberllama.player_feed[0]
                # self.server.cyberllama.v_speak(last_v_line)
                
                PROMPT_LAST_TURN = PROMPT_TTS_PLAYER_FEED
                if feed_length == 1:
                    self.server.cyberllama.player_feed = []
                    CURRENT_PROMPT_STATE = PROMPT_TTS_NPC_FEED
                    self.send_OK({
                        "actions": [], 
                        "mood": None, 
                        "expression": None,
                        "food": npc_cache["food"],
                        "hydration": npc_cache["hydration"],
                        "fun": npc_cache["fun"],
                        "relationship": npc_cache["relationship"],
                        'last_action': self.server.cyberllama.world_data.last_action,
                        "v_intentions": None,
                        "npc_intentions": None,
                        "v_subtitles": last_v_line,
                        "npc_subtitles": None,
                        "state": "PROMPT_TTS_NPC_FEED",                        
                    })
                    return
                else:
                    self.server.cyberllama.player_feed = self.server.cyberllama.player_feed[1:]
                    self.server.cyberllama.player_feed = list(map(lambda y: self.server.cyberllama.cleaner_service.clean_text(y.strip()), filter(lambda x: len(x.strip()) > 1, self.server.cyberllama.player_feed)))
                    self.send_OK({
                        "actions": [], 
                        "mood": None, 
                        "expression": None,
                        "food": npc_cache["food"],
                        "hydration": npc_cache["hydration"],
                        "fun": npc_cache["fun"],
                        "relationship": npc_cache["relationship"],
                        'last_action': self.server.cyberllama.world_data.last_action,
                        "v_intentions": None,
                        "npc_intentions": None,
                        "v_subtitles": last_v_line,
                        "npc_subtitles": None,
                        "state": "PROMPT_TTS_PLAYER_FEED",                        
                    })
                    return


            else:
                # add feed                
                if contains_prompt:
                    self.server.cyberllama.all_player_lines = self.server.cyberllama.aify_text(CURRENT_POST_DATA['prompt'], self.server.cyberllama.world_data.npc_voice_arg)
                    self.server.cyberllama.cached_conversation_lines.append((
                        str(uuid.uuid4()),
                        'V',
                        self.server.cyberllama.all_player_lines,
                    ))

                PROMPT_LAST_TURN = PROMPT_TTS_PLAYER_FEED                
                cleaned_t = self.server.cyberllama.all_player_lines, 
                self.server.cyberllama.player_feed = list(
                    map(
                        lambda y: self.server.cyberllama.cleaner_service.clean_text(y.strip()), 
                        filter(lambda x: len(x.strip()) > 1, 
                            cleaned_t[0] if isinstance(cleaned_t, tuple) else cleaned_t.split("."))
                    ))
                # TODO PROBLEM FIX: add generated V line to cache conversation

                new_state =  "PROMPT_TTS_PLAYER_FEED"
                last_v_line = None
                last_npc_line = None
                if len(self.server.cyberllama.player_feed) == 0:
                    CURRENT_PROMPT_STATE = PROMPT_TTS_NPC_FEED
                    new_state = "PROMPT_TTS_NPC_FEED"
                    if len(self.server.cyberllama.npc_feed) == 0:
                        cleaned_t = self.server.cyberllama.cyber_prompt_service.gen_npc_response_to_line(CURRENT_POST_DATA['prompt'], self.server.cyberllama.cached_conversation_lines)
                        if len(cleaned_t) == 0:
                            cleaned_t = self.server.cyberllama.cyber_prompt_service.text_random_end_filler()

                        self.server.cyberllama.all_npc_feed_lines = cleaned_t
                        self.server.cyberllama.npc_feed = list(map(lambda y: self.server.cyberllama.cleaner_service.clean_text(y.strip()), filter(lambda x: len(x.strip()) > 1, cleaned_t.split("."))))                        
                        last_npc_line = self.server.cyberllama.npc_feed[0]
                        self.server.cyberllama.npc_feed = self.server.cyberllama.npc_feed[1:]
                        # self.server.cyberllama.npc_speak(last_npc_line, self.server.cyberllama.world_data)
                else:
                    last_v_line = self.server.cyberllama.player_feed[0]
                    self.server.cyberllama.player_feed = self.server.cyberllama.player_feed[1:]
                    # self.server.cyberllama.v_speak(last_v_line)

                self.send_OK({
                    "actions": [], 
                    "mood": None, 
                    "expression": None,
                    "food": npc_cache["food"],
                    "hydration": npc_cache["hydration"],
                    "fun": npc_cache["fun"],
                    "relationship": npc_cache["relationship"],
                    'last_action': self.server.cyberllama.world_data.last_action,
                    "v_intentions": None,
                    "npc_intentions": None,
                    "v_subtitles": last_v_line,
                    "npc_subtitles": last_npc_line,
                    "state": new_state
                })
                return 
            
        elif CURRENT_PROMPT_STATE == PROMPT_TTS_NPC_FEED:
            feed_length = len(self.server.cyberllama.npc_feed)
            
            if self.server.cyberllama.npc_feed and feed_length > 0:
                # continue feeding v answers
                last_npc_line = self.server.cyberllama.npc_feed[0]
                # self.server.cyberllama.npc_speak(last_npc_line, self.server.cyberllama.world_data)
                if feed_length == 1:
                    
                    self.server.cyberllama.npc_feed = []
                    PROMPT_LAST_TURN = PROMPT_TTS_NPC_FEED
                    CURRENT_PROMPT_STATE = PROMPT_DONE
                    v_intentions = self.server.cyberllama.intention_service.get_intentions(self.server.cyberllama.all_player_lines, 'v', self.server.cyberllama.npc_cache)
                    npc_intentions = self.server.cyberllama.intention_service.get_intentions(self.server.cyberllama.all_npc_feed_lines, self.server.cyberllama.world_data.npc_tweaks_name, self.server.cyberllama.npc_cache)
                    actions = self.server.cyberllama.cyber_prompt_service.state_v_responses(\
                            self.server.cyberllama.all_npc_feed_lines,\
                            self.server.cyberllama.world_data.npc_tweaks_name,\
                            self.server.cyberllama.world_data,
                            self.server.cyberllama.cached_conversation_lines)
                    self.send_OK({
                        "actions": actions, 
                        "mood": self.server.cyberllama.mood_service.get_mood_value_of_prompt(self.server.cyberllama.all_npc_feed_lines), 
                        "expression": self.server.cyberllama.mood_service.get_mood_of_prompt(self.server.cyberllama.all_npc_feed_lines),
                        "food": npc_cache["food"],
                        "hydration": npc_cache["hydration"],
                        "fun": npc_cache["fun"],
                        "relationship": npc_cache["relationship"],
                        'last_action': self.server.cyberllama.world_data.last_action,
                        "v_intentions": v_intentions,
                        "npc_intentions": npc_intentions,
                        "v_subtitles": None,
                        "npc_subtitles": last_npc_line,
                        "state": "PROMPT_DONE"
                    })
                    return
                else:
                    self.server.cyberllama.npc_feed = self.server.cyberllama.npc_feed[1:]
                    self.server.cyberllama.npc_feed = list(map(lambda y: self.server.cyberllama.cleaner_service.clean_text(y.strip()), filter(lambda x: len(x.strip()) > 1, self.server.cyberllama.npc_feed)))
                    self.send_OK({
                        "actions": [], 
                        "mood": None, 
                        "expression": None,
                        "food": npc_cache["food"],
                        "hydration": npc_cache["hydration"],
                        "fun": npc_cache["fun"],
                        "relationship": npc_cache["relationship"],
                        'last_action': self.server.cyberllama.world_data.last_action,
                        "v_intentions": None,
                        "npc_intentions": None,
                        "v_subtitles": None,
                        "npc_subtitles": last_npc_line,
                        "state": "PROMPT_TTS_NPC_FEED"
                    })
                    return
            else:
                # add feed
                if contains_prompt:
                    pass
                    # self.server.cyberllama.v_speak(CURRENT_POST_DATA['prompt'])
                # the problem: 
                # npc generates lines not based on the past v lines. and also not based
                vline_to_pick = ''
                if contains_prompt:
                    vline_to_pick = CURRENT_POST_DATA['prompt']
                else:
                    vline_to_pick = self.server.cyberllama.cached_conversation_lines[\
                        len(self.server.cyberllama.cached_conversation_lines) - 1\
                    ][COL_LINE]
                # !!!! READ THIS !!!!
                # !!!! gen_npc_response_to_line already adds line to npc cached conversation lines!!!!!
                # CHANGE IN FUTURE. THIS IS GARBAGE
                cleaned_t = self.server.cyberllama.cyber_prompt_service.gen_npc_response_to_line(
                    vline_to_pick, 
                    self.server.cyberllama.cached_conversation_lines)
                self.server.cyberllama.all_npc_feed_lines = cleaned_t
                
                self.server.cyberllama.npc_feed = list(map(lambda y: self.server.cyberllama.cleaner_service.clean_text(y.strip()), filter(lambda x: len(x.strip()) > 1, cleaned_t.split("."))))
                
                v_intentions = None
                npc_intentions = None
                actions = []
                mood = None
                expression = None
                last_npc_line = None
                new_state = "PROMPT_TTS_NPC_FEED"
                if len(self.server.cyberllama.npc_feed) == 0:
                    PROMPT_LAST_TURN = PROMPT_TTS_NPC_FEED
                    CURRENT_PROMPT_STATE = PROMPT_DONE                    
                else:    
                    last_npc_line = self.server.cyberllama.npc_feed[0]                    
                    self.server.cyberllama.npc_feed = self.server.cyberllama.npc_feed[1:]
                    # self.server.cyberllama.npc_speak(last_npc_line, self.server.cyberllama.world_data)
                
                if len(self.server.cyberllama.npc_feed) == 0:
                    PROMPT_LAST_TURN = PROMPT_TTS_NPC_FEED
                    new_state = "PROMPT_DONE"
                    v_intentions = self.server.cyberllama.intention_service.get_intentions(self.server.cyberllama.all_player_lines, 'V', self.server.cyberllama.npc_cache)
                    npc_intentions = self.server.cyberllama.intention_service.get_intentions(self.server.cyberllama.all_npc_feed_lines, self.server.cyberllama.world_data.npc_display_name, self.server.cyberllama.npc_cache)
                    actions = self.server.cyberllama.cyber_prompt_service.state_v_responses(\
                            self.server.cyberllama.all_npc_feed_lines,\
                            self.server.cyberllama.world_data.npc_tweaks_name,\
                            self.server.cyberllama.world_data,
                            self.server.cyberllama.cached_conversation_lines)
                    mood = self.server.cyberllama.mood_service.get_mood_value_of_prompt(self.server.cyberllama.all_npc_feed_lines)
                    expression = self.server.cyberllama.mood_service.get_mood_of_prompt(self.server.cyberllama.all_npc_feed_lines)

                self.send_OK({
                    "actions": actions, 
                    "mood": mood, 
                    "expression": expression,
                    "food": self.server.cyberllama.world_data.food,
                    "hydration": self.server.cyberllama.world_data.hydration,
                    "fun": self.server.cyberllama.world_data.fun,
                    "relationship": self.server.cyberllama.world_data.relationship,
                    'last_action': self.server.cyberllama.world_data.last_action,
                    "v_intentions": v_intentions,
                    "npc_intentions": npc_intentions,
                    "v_subtitles": CURRENT_POST_DATA['prompt'] if contains_prompt else None,
                    "npc_subtitles": last_npc_line,
                    "state": new_state
                })
                return

        elif CURRENT_PROMPT_STATE == PROMPT_NPC_GENERATE_LINES:
            pass
        elif CURRENT_PROMPT_STATE == PROMPT_DONE:            
            v_intentions = self.server.cyberllama.intention_service.get_intentions(self.server.cyberllama.all_player_lines, 'V')
            npc_intentions = self.server.cyberllama.intention_service.get_intentions(self.server.cyberllama.all_npc_feed_lines, self.server.cyberllama.world_data.npc_display_name)
            actions = self.server.cyberllama.cyber_prompt_service.state_v_responses(\
                    self.server.cyberllama.all_npc_feed_lines,\
                    self.server.cyberllama.world_data.npc_tweaks_name,\
                    self.server.cyberllama.world_data,
                    self.server.cyberllama.cached_conversation_lines)
            mood = self.server.cyberllama.mood_service.get_mood_value_of_prompt(self.server.cyberllama.all_npc_feed_lines)
            expression = self.server.cyberllama.mood_service.get_mood_of_prompt(self.server.cyberllama.all_npc_feed_lines)
            self.send_OK({
                "actions": actions, 
                "mood": mood, 
                "expression": expresseion,
                "food": npc_cache["food"],
                "hydration": npc_cache["hydration"],
                "fun": npc_cache["fun"],
                "relationship": npc_cache["relationship"],
                'last_action': self.server.cyberllama.world_data.last_action,
                "v_intentions": v_intentions,
                "npc_intentions": npc_intentions,
                "v_subtitles": None,
                "npc_subtitles": None,
                "state": "PROMPT_DONE"
            })
            return
        else:
            pass
    
    def on_prompt_continue_3(self, data, dataj):
        print(data)
        global CURRENT_PROMPT_STATE
        global CURRENT_POST_DATA
        # first 
        if not self.on_prompt_ceremony(dataj.get('npc'), dataj):
            return
        
        if CURRENT_POST_DATA['prompt_args'] == 'PROMPT_TTS_PLAYER_FEED':
            self.on_prompt_continue_3_v_conversation_start(data, dataj)
        elif CURRENT_POST_DATA['prompt_args'] == 'PROMPT_TTS_NPC_FEED':
            self.on_prompt_continue_3_npc_response(data, dataj)
        elif CURRENT_POST_DATA['prompt_args'] == 'PROMPT_DONE':
            self.on_prompt_continue_3_v_response_lines(data, dataj)

        
    def on_prompt_continue_3_v_conversation_start(self, data, dataj):
        print(data)
        global CURRENT_PROMPT_STATE
        global CURRENT_POST_DATA
        
        
        last_v_line = self.server.cyberllama.aify_text(CURRENT_POST_DATA['prompt'])
        self.server.cyberllama.cached_conversation_lines.append((
            str(uuid.uuid4()),
            'V',
            last_v_line,
        ))
        self.send_OK({
            "actions": [], 
            "mood": None, 
            "expression": None,
            "food": None,
            "hydration": None,
            "fun": None,
            "relationship": None,
            'last_action': self.server.cyberllama.world_data.last_action,
            "v_intentions": None,
            "npc_intentions": None,
            "v_subtitles": last_v_line,
            "npc_subtitles": None,
            "state": "PROMPT_TTS_PLAYER_FEED"
        })

    def on_prompt_continue_3_npc_response(self, data, dataj):
        print(data)
        global CURRENT_PROMPT_STATE
        global CURRENT_POST_DATA
        
        # last_npc_line = self.server.cyberllama.aify_text(CURRENT_POST_DATA['prompt'], self.server.cyberllama.world_data.npc_voice_arg)
        last_npc_line = self.server.cyberllama.cyber_prompt_service.gen_npc_response_to_line(CURRENT_POST_DATA['prompt'], self.server.cyberllama.cached_conversation_lines)
        self.server.cyberllama.cached_conversation_lines.append((
            str(uuid.uuid4()),
            self.server.cyberllama.world_data.npc_display_name,
            last_npc_line,
        ))
        self.send_OK({
            "actions": [], 
            "mood": None, 
            "expression": None,
            "food": None,
            "hydration": None,
            "fun": None,
            "relationship": None,
            'last_action': self.server.cyberllama.world_data.last_action,
            "v_intentions": None,
            "npc_intentions": None,
            "v_subtitles": None,
            "npc_subtitles": last_npc_line,
            "state": "PROMPT_TTS_NPC_FEED"
        })

    def on_prompt_continue_3_v_response_lines(self, data, dataj):
        print(data)
        global CURRENT_PROMPT_STATE
        global CURRENT_POST_DATA
       
        last_npc_response = CURRENT_POST_DATA['prompt_args']
        actions = self.server.cyberllama.cyber_prompt_service.state_v_responses(\
                    last_npc_response,\
                    self.server.cyberllama.world_data.npc_tweaks_name,\
                    self.server.cyberllama.world_data,
                    self.server.cyberllama.cached_conversation_lines)
        
        self.send_OK({
            "actions": actions, 
            "mood": None, 
            "expression": None,
            "food": None,
            "hydration": None,
            "fun": None,
            "relationship": None,
            'last_action': self.server.cyberllama.world_data.last_action,
            "v_intentions": None,
            "npc_intentions": None,
            "v_subtitles": None,
            "npc_subtitles": None,
            "state": "PROMPT_DONE"
        })

    def on_prompt(self, data, dataj):
        print(data)
        global CURRENT_PROMPT_STATE
        # first 
        if not self.on_prompt_ceremony(data, dataj):
            return
        
        cleaned_t = self.server.cyberllama.aify_text(CURRENT_POST_DATA['prompt'], self.server.cyberllama.world_data.npc_voice_arg)
        result = self.server.cyberllama.old_on_prompt(cleaned_t, self.server.cyberllama.world_data, self.server.cyberllama.world_data.npc_tweaks_name)
        v_lines = result[0]

        npc_cache = {
            "food": 0,
            "hydration": 0,
            "fun": 0,
            "relationship": 0
        }
        
        if self.server.cyberllama.world_data.npc_id_hash and self.server.cyberllama.world_data.npc_id_hash in self.server.cyberllama.npc_cache:
            npc_cache["food"] = self.server.cyberllama.npc_cache[self.server.cyberllama.world_data.npc_id_hash]['food']
            npc_cache["hydration"] = self.server.cyberllama.npc_cache[self.server.cyberllama.world_data.npc_id_hash]['hydration']
            npc_cache["fun"] = self.server.cyberllama.npc_cache[self.server.cyberllama.world_data.npc_id_hash]['fun']
            npc_cache["relationship"] = self.server.cyberllama.npc_cache[self.server.cyberllama.world_data.npc_id_hash]['relationship']

        if(v_lines):                    
            self.send_OK({
                "actions": v_lines, 
                "mood": result[2], 
                "expression": result[1],
                "food": npc_cache["food"],
                "hydration": npc_cache["hydration"],
                "fun": npc_cache["fun"],
                "relationship": npc_cache["relationship"],
                'last_action': self.server.cyberllama.world_data.last_action,
                "v_intentions": result[3],
                "npc_intentions": result[4],
                "v_subtitles": None,
                "npc_subtitles": None
            })
        else:
            self.send_OK({
                "actions": [], 
                "mood": result[2], 
                "expression": result[1],
                "food": self.server.cyberllama.world_data.food, 
                "hydration": self.server.cyberllama.world_data.hydration,
                "fun": self.server.cyberllama.world_data.fun,
                "relationship": self.server.cyberllama.world_data.relationship,
                'last_action': self.server.cyberllama.world_data.last_action,
                "v_intentions": result[3],
                "npc_intentions": result[4],
                "v_subtitles": None,
                "npc_subtitles": None
            })

    def on_tts(self, data, dataj):
        global CURRENT_CMD        
        
        global CURRENT_POST_DATA
        # self.on_prompt_ceremony(data, dataj, self.server.cyberllama)
        # no need for npc data here
        print(data)
        
        CURRENT_POST_DATA['prompt'] = dataj.get('prompt')
        CURRENT_POST_DATA['prompt_args'] = dataj.get('prompt_args')

        tts = CURRENT_POST_DATA['prompt_args']['tts']
        voice = CURRENT_POST_DATA['prompt_args']['voice']
        npc_id = CURRENT_POST_DATA['prompt_args']['npc_id']
        
        text = self.server.cyberllama.cleaner_service.get_clean_prompt(CURRENT_POST_DATA['prompt_args']['text'])
        text = self.server.cyberllama.aify_text(text, use_limit=False)

        if voice == 'v':
            self.server.cyberllama.v_speak(text)
            self.send_OK({
                "text": text
            })
        else:
            if len(npc_id) > 0:
                foundHash = None
                # lookup the npc data
                for npc_id_hash in self.server.cyberllama.npc_cache:
                    if npc_id_hash != npc_id:
                        continue
                    foundHash = npc_id_hash

                # add data + random VOICE data to fixer
                npc_data = dataj['npc']
                if foundHash == None:
                    # and 'fixer_' in npc_id or \
                    # 'cyberpunk' in npc_data['appearance'] or \
                    # 'aldecaldo' in npc_data['appearance'] or \
                    # 'mox' in npc_data['appearance']:
                    # TODO: fix this nightmare later on (see the args)
                    self.server.cyberllama.world_data.addreplace_fixer_to_cache(npc_data, self.server.cyberllama.config, self.server.cyberllama)

                if npc_id in self.server.cyberllama.npc_cache:
                    self.server.cyberllama.npc_speak(text, self.server.cyberllama.npc_cache[npc_id])
                else:
                    # this happens if the player scans an npc with the same name. the entity is not 100% the same.. so this happens
                    for npc_k in self.server.cyberllama.npc_cache:
                        if self.server.cyberllama.npc_cache[npc_k]['npc_display_name'] == npc_data['display_name']:
                            self.server.cyberllama.npc_cache[npc_id] = self.server.cyberllama.npc_cache[npc_k]
                            
                            print("Horrible code ahead!")
                            self.server.cyberllama.npc_speak(text, self.server.cyberllama.npc_cache[npc_id])
                            break
                # silent errors here
                self.send_OK({
                    "text": text
                })
            else:
                if tts == 'kokoro':
                    self.server.cyberllama.tts_kokoro(text, voice)

                elif tts == 'piper':
                    self.server.cyberllama.tts_piper(text, voice)

                self.send_OK({
                    "text": text
                })

    def on_revlookup(self,data,dataj):
        global CURRENT_CMD        
        
        global CURRENT_POST_DATA
        session = float(dataj.get('session'))
        appearances = self.server.cyberllama.get_stored_appearances(session)

        full_data = []
        entity_appearance_index = 0
        entity_tweak_index = 1
        entity_display_name_index = 2
        for appearance in appearances:
            spawn_appearance = self.server.cyberllama.reverse_lookup_character(appearance[0])
            if spawn_appearance != None:
                full_data.append({
                    "appearance": spawn_appearance[entity_appearance_index],
                    "tweak": spawn_appearance[entity_display_name_index],
                    "display": spawn_appearance[entity_display_name_index]
                })
        self.send_OK({
            "appearances": full_data
        })

    def on_make_title(self, data, dataj):
        global CURRENT_CMD        
        
        global CURRENT_POST_DATA

        location_title = self.server.cyberllama.image_to_text_service.make_location_title()

        if len(location_title.strip()) == 0:
            location_title = "Some location"
        self.send_OK({
            'title': location_title
        })

    def on_forget_conversation(self, data, dataj):
        global CURRENT_CMD        
        
        global CURRENT_POST_DATA

        self.server.cyberllama.npc_cache[self.server.cyberllama.world_data.npc_id_hash]['npc_conversation'] = []
        self.server.cyberllama.v_speak("Forget it")

        self.send_OK({})

    def on_reset(self, data, dataj):
        global CURRENT_CMD        
        
        global CURRENT_POST_DATA
        self.server.cyberllama.v_speak("reset")
        self.server.cyberllama = self.server.cyberllama()
        self.send_OK({})
    
    def on_soft_reset(self, data, dataj):
        global CURRENT_CMD        
        
        global CURRENT_POST_DATA
        self.server.cyberllama.npc_cache = dict()
        self.server.cyberllama.last_v_responses = []
        self.server.cyberllama.cached_conversation_lines = []
        self.server.cyberllama.all_player_lines = ''
        self.server.cyberllama.all_npc_feed_lines = ''
        self.server.cyberllama.player_feed = []
        self.server.cyberllama.npc_feed = []
        self.server.cyberllama.world_data = WorldData()
        self.server.cyberllama.v_speak("soft reset")
        self.send_OK({})

    
        
    def on_savesession(self, data, dataj):
        # readSessionKey => which is os.time
        key = dataj.get('key')
        self.server.cyberllama.save_session()
        self.send_OK({})

    def do_POST(self):        
        content_len = int(self.headers.get('Content-Length'))
        print(content_len)
        global CURRENT_CMD        
        
        global CURRENT_POST_DATA
        if content_len != 0:
            # self.server.cyberllama.v_speak(self.path)
            data = self.rfile.read(content_len)
            dataj = json.loads(data)
            if "comment" in self.path:
               self.on_comment(data, dataj)

            # expands on a topic by giving keywords (kind of a way of guiding more the conversation)
            elif "expand" in self.path:
                self.on_expand(data, dataj)  
            
            elif "aify" in self.path:
                self.on_aify(data, dataj)

            elif "maketitle" in self.path:
                self.on_make_title(data, dataj)

            elif "forgetconversations" in self.path:
                self.on_forget_conversation(data, dataj)
                
            elif "promptcontinue" in self.path:
                self.on_prompt_continue_2(data, dataj)

            elif "promptclient" in self.path:
                self.on_prompt_continue_3(data, dataj)

            elif "prompt" in self.path:
                self.on_prompt(data, dataj)

            elif "tts" in self.path:
                self.on_tts(data, dataj)

            # wrote this because im being lazy. can be put on the lua side
            elif "revlookup" in self.path:
                self.on_revlookup(data, dataj)

            elif "npcsync" in self.path:
                self.on_npc_sync(data, dataj)

            elif "reset" in self.path:
                self.on_soft_reset(data, dataj)
            
            elif "recstart" in self.path:
                self.on_recstart(data, dataj)
            
            # calls whisper to stop, then asks for 
            elif "recstop" in self.path:
                self.on_recstop(data, dataj)

            elif "createproject" in self.path:
                self.on_create_project(data, dataj)

            ## not needed now
            # elif "recstat" in self.path:                
            #     response = requests.post(self.server.cyberllama.config.whisper.url+'/stat', verify=False, json={})                
            #     self.send_OK(response.json())
            
            elif "savesession" in self.path:
                self.on_savesession(data, dataj)

            else:
                print(data)

                

    def send_OK(self, response_obj):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        content = json.dumps(response_obj).encode("utf-8")
        with open('server_log.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps(response_obj)+',\n')

        self.wfile.write(content)

    # self.do_GET()
        
