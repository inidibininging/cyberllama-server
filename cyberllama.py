import string
import sys
import platform
import json
import random
import datetime
import time
import pyttsx3
import torch
import requests
import yaml
import os
import shlex, subprocess
import sqlite3
import base64
import math
import uuid
import logging
import psutil


import re
# http stuff for python server
import json
import ssl 

import time
import pathlib
from io import BytesIO
# from functools import cached_property
import asyncio
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configure logging
logging.basicConfig(level=logging.DEBUG, \
    format='%(asctime)s / %(levelname)s : %(message)s')

global cyberllama
global llava_prompts
global current_mood

##########################################################
# cyberllama
##########################################################

import yaml
from projects.all.services.config_node import ConfigNode
from projects.all.services.config_service import ConfigService
from projects.all.services.prompt_template_service import PromptTemplateService
from projects.all.services.keywords_service import KeywordsService
from projects.all.services.character_overrides_service import CharacterOverridesService
from projects.all.services.ocean_service import OceanService

from projects.all.services.piper_service import PiperService
from projects.all.services.basic_prompt_service import BasicPromptService
from projects.all.services.volume_control import VolumeControl
from projects.all.services.wiki_service import WikiService
from projects.all.services.ollama_service import OllamaService
from projects.all.services.string_service import StringService
from projects.all.services.screenshot_service import ScreenshotService

from projects.cyberpunk.services.cyber_replacers_service import CyberReplacersService
from projects.cyberpunk.services.cleaner_service import CleanerService
from projects.cyberpunk.services.sqlite3_cache_service import Sqlite3CacheService
from projects.cyberpunk.services.mood_service import MoodService
from projects.cyberpunk.services.quest_service import QuestService
from projects.cyberpunk.services.web_service import WebService, set_cyberllama
from projects.cyberpunk.services.image_to_text_service import ImageToTextService
from projects.cyberpunk.services.cyber_prompt_service import CyberPromptService
from projects.cyberpunk.services.intention_service import IntentionService
from projects.cyberpunk.services.mentions_service import MentionsService
from projects.cyberpunk.services.comment_service import CommentService
from projects.cyberpunk.services.npc_evaluator_service import NpcEvaluatorService
from projects.cyberpunk.models.world_data import WorldData

class Cyberllama:
    def __init__(self):
        logging.info("Booting Cyberllama ...")
        
        self.config_service = ConfigService('cyberpunk')        
        self.config = self.config_service.init_config()
        self.world_data = WorldData()
        self.string_service = StringService()
        self.screenshot_service = ScreenshotService()
        self.basic_prompt_service = BasicPromptService('cyberpunk')
        self.cyber_replacer_service = CyberReplacersService()

        self.cleaner_service = CleanerService(
            self.string_service,
            self.cyber_replacer_service) 

        self.ollama_service = OllamaService(
            self.config,
            self.string_service)

        self.prompt_template_service = PromptTemplateService('cyberpunk')
        self.prompt_template_service.init_prompts()            

        self.keywords_service = KeywordsService('cyberpunk')
        self.keywords_service.keywords = self.keywords_service.init_keywords()       

        self.character_overrides_service = CharacterOverridesService('cyberpunk', self.world_data)
        self.character_overrides_service.npc_overrides = self.character_overrides_service.init_npc_overrides()        

        self.ocean_service = OceanService('all')
        self.ocean_expr_map = self.ocean_service.init_ocean_expr()
        
        self.npc_evaluator_service = NpcEvaluatorService()
        self.mentions_service = MentionsService(self.keywords_service)
        self.intention_service = IntentionService(self.keywords_service, self.mentions_service)

        if 'kokoro' in self.config.npc_tts:
            from projects.all.services.kokoro_service import KokoroService
            self.kokoro_service = KokoroService(self.config)            

        self.cached_conversation_lines = []
        self.all_player_lines = ''
        self.all_npc_feed_lines = ''
        self.player_feed = []
        self.npc_feed = []

        self.wiki_service = WikiService('cyberpunk')
        self.wiki_service.load_wiki()        

        self.load_appearances()
        self.npc_cache = dict()        
        self.volume_control = VolumeControl()
        self.volume_control.set_volume(0.5)
        self.context = []
        self.save_your_breath_lines = None
        self.whats_your_angle_lines = None
        self.spare_me_line_replace_lines = None
        self.are_you_kidding_line_replace_lines = None
        self.sweetheart_replace_lines = None

        time.sleep(0.5)
        
        self.ollama_service.to_ollama_internal(self.prompt_template_service.prompts['prompt_npc'].prompt_template, '')
        item_count = 20
       
        self.last_v_responses = []

        if (self.config.cache.init_mood_lines):
            self.tts_piper('Building in memory generic mood answers')
            self.append_hunger_cache(item_count)
            self.append_no_hunger_cache(item_count)
            self.append_thirst_cache(item_count)
            self.append_no_thirst_cache(item_count)
            self.append_relationship_low_cache(item_count)
            self.append_relationship_mid_cache(item_count)
            self.append_relationship_high_cache(item_count)
            self.append_fun_low_cache(item_count)
            self.append_fun_mid_cache(item_count)
            self.append_fun_high_cache(item_count)

        # if (self.config.cache.init_data):
        self.ocean_expr_map = self.ocean_service.init_ocean_expr()
        self.mood_service = MoodService(self.config, self.ollama_service, self.character_overrides_service, self.ocean_expr_map, lambda: self.world_data)
        self.piper_service = PiperService(self.config, self.mood_service)
        self.piper_service.tts_piper('Pipes on')

        self.sqlite3_cache_service = Sqlite3CacheService(self.config)
        self.sqlite3_cache_service.cache_db_init()
        self.sqlite3_cache_service.cache_db_init_npc_cache()
        self.sqlite3_cache_service.cache_db_init_npc_mood()
        self.sqlite3_cache_service.cache_db_init_location_description()
        self.sqlite3_cache_service.cache_db_init_world_data()

        self.image_to_text_service = ImageToTextService(
            self.config,
            self.basic_prompt_service,            
            self.ollama_service,
            self.screenshot_service,
            self.cleaner_service,
            self.sqlite3_cache_service)

        self.cyber_prompt_service = CyberPromptService(
            self.config, 
            lambda : self.world_data,
            self.basic_prompt_service, 
            self.prompt_template_service,
            self.ollama_service, 
            self.ocean_service, 
            self.npc_evaluator_service,
            self.cleaner_service, 
            self.wiki_service,
            self.mood_service,
            self.string_service
        )
        self.comment_service = CommentService(
            self.config,
            self.ollama_service,
            self.cleaner_service,
            self.basic_prompt_service,
            self.wiki_service
        )

        self.quest_service = QuestService(
            self.config,
            self.keywords_service,
            self.cyber_prompt_service,
            self.wiki_service,
            self.cleaner_service)

        self.piper_service.tts_piper('Ready.')

    def silent_log(self, txt):
        print(txt)

    def load_appearances(self):
        # sorry. i borrowed this from somewhere and i don't know where
        with open(os.getcwd() + "/appearances.csv", "r", encoding='utf-8') as af:
            self.appearances = list(map(lambda l: l.split(","), af.readlines()))

    def get_stored_appearances(self, session_key):
        conn = sqlite3.connect(self.config.db.path)
        cur = conn.cursor()
        sql = 'SELECT DISTINCT(npc_appearance), session FROM world_data WHERE session = "' + str(session_key) + '"'
        rc = cur.execute(sql)
        # cur.commit()
        res = rc.fetchall()
        conn.close()
        return res

    # used for spawns (means npc's you have talked to and now need to be spawned)
    def reverse_lookup_character(self, appearance):
        for a in self.appearances:
            if a[0] == appearance:
                return a
        
        # self.cache_db_add_location_description(uuid.uuid4(), district, sub_district, x, y, z, cleaned_t)
        return cleaned_t

    def pick_pre_answer_look(self):
        global llava_prompts
        plen = len(llava_prompts)
        psel = random.randrange(0, plen - 1)
        return llava_prompts[psel]


    def init_vlines_cache(self, item_count, npc_answer):
        # TODO: generate cached dialogue tree (how deep?)
        # looks horribly like this is heading towards the ORM-Version of prompting
        pass

    def v_select_last_response(self, prompt):
        if(len(self.last_v_responses) > 0):
            for vdoption in self.last_v_responses:
                if self.cleaner_service.clean_text(vdoption[COL_LINE]) != prompt:
                    continue
                return [vdoption]
                break
        return None

    def v_lookup_last_response_in_db(self, prompt):
        return self.sqlite3_cache_service.cache_db_get_dialog_line_by_line('V', prompt)    

    def npc_speak(self, text, world_data=None):
        world_data_used=world_data
        if type(world_data) is dict:
            world_data_used=ConfigNode(world_data)
        if world_data_used == None:
            world_data_used=self.world_data        

        if text == None or len(text) == 0:
            return        
        if world_data_used.npc_voice_arg == None or \
            len(world_data_used.npc_voice_arg) == 0 or \
            world_data_used.npc_voice == None or \
            len(world_data_used.npc_voice) == 0:
            voices = []
            
            if world_data_used.npc_gender == 'Female':
                voices = list(self.config.kokoro.female_voices)
            elif world_data_used.npc_gender == 'Male':
                voices = list(self.config.kokoro.male_voices)
            # happens if the no npc sync happened (i guess). dirty fix
            elif len(world_data_used.npc_gender) == 0:
                if random.randrange(0, 10) > 5:
                    voices = list(self.config.kokoro.male_voices)
                else:
                    voices = list(self.config.kokoro.female_voices)
            new_voice = random.randrange(0, len(voices) - 1)
            world_data_used.npc_voice = voices[new_voice]
            world_data_used.npc_voice_arg = voices[new_voice]


        mood = self.mood_service.get_mood_of_prompt(text)
        multiple_voice_engines = type(world_data_used.npc_voice_engine) is list
        if multiple_voice_engines and len(world_data_used.npc_voice_engine) == 0:
            pass
            # self.tts_kokoro(text, model_path=world_data_used.npc_voice_arg, mood=mood)
        else:
            if world_data_used.npc_voice_engine == "piper":
                self.piper_service.tts_piper(text, model_path=world_data_used.npc_voice_arg, mood=mood, speaker_id=world_data_used.npc_speaker_id)
            elif world_data_used.npc_voice_engine == "zonos":
                self.zonos_service.tts_zonos(text, model_path=world_data_used.npc_voice_arg, mood=mood)
            elif world_data_used.npc_voice_engine == "kokoro":
                self.kokoro_service.tts_kokoro(text, model_path=world_data_used.npc_voice_arg, mood=mood)
            else:
                self.piper_service.tts_piper(text, model_path=world_data_used.npc_voice_arg, mood=mood, speaker_id=world_data_used.npc_speaker_id)



    # so the idea is to generate topics
    # out of the topics, generate generic lines
    # (the user has the possiblity to express more on a specific topic. This gives the user more control about what she/he says)
    def expand_topic(self, text):
        stuff_preroll = []

        # add random topic from something along these world of cyberpunk 2077
        # check last district if ANY there
        # add random topic (like brands)
        max_topics=4
        if(text == 'talk'):
            for topic in self.wiki:
                if max_topics <= 0:
                    break
                r = random.randrange(0, 100)
                if(r > 50):
                    continue
                if "full" in topic["file"]:
                    continue
                text = text + topic["content"].strip()
                max_topics = max_topics - 1
        prompt = 'Given is the world of ' + OLLAMA_WORLD_NAME + '. What kind of single word topics can you expand on the following input. Give me only related keywords comma separated: the input is \'' + text + '\''
        topics = self.to_ollama_internal('You are a helpful topic expander. You follow my instructions to the letter', prompt).strip().split(',')
        final_topics = []
        
        for topic in topics:
            topic = topic.strip().lower()
            if len(topic) < 1 or len(topic) > 20:
                continue
            # somehow somewhere is still a ref to phantom liberty in the wiki
            if "phantom" in topic.lower().strip():
                continue
            final_topics.append(topic)        

        
        if len(final_topics) > 6:
            final_topics = final_topics[-6:]
        return final_topics


    
    def convert_appearance_to_description(self, npc_appearance):
        pass

    def aify_text(self, text, forced_needle=[], character=None, post_data=None, use_limit=True):
        needles = ['kill job fixer', 'driver job fixer','vision','joke', 'talk', 'insult', 'brag', 'drink', 'food', 'hunger', 'quest', 'flirt', 'admire', 'hate', 'love', 'kill', 'death', 'quest', 'background story', 'location', 'move here']
        intro_needles = [
            "introduce yourself",
            'ask for nc residents background story',
            "ask for a place to eat",
            "ask for a place to drink",
            "ask for a place for buying or selling weapons",
            "ask about about an aspect of nc residents life",
            "ask about nc residents job",
            "ask for a place for buying medicine",
        ]
        text_used = ''
        if forced_needle == None:
            forced_needle = []
        if text.lower() in needles \
        or text.lower() in intro_needles \
        or text.lower() in forced_needle:
            character_used = character if character != None else self.world_data.npc_display_name
            if text == 'quest':
                # TODO: PROVIDE  QUEST DATA HERE
                text_used = self.quest_service.gen_quest_v_text(character_used, post_data)
                use_limit = False
            if text == 'kill job fixer':
                text_used = self.quest_service.gen_quest_kill_job_fixer_text(character_used, post_data)
                use_limit = False
            if text == 'driver job fixer':
                text_used = self.quest_service.gen_quest_driver_job_fixer_text(character_used, post_data)
                use_limit = False
            elif text == 'location':
                text_used = self.comment_service.location_comment(character_used, post_data)
                use_limit = False
            elif text == 'vision':
                text_used = 'what do you see?'
            elif text == 'move here':
                text_used = self.cyber_prompt_service.conversation_starter_v('can you move here?', character_used)
            elif len(text_used) == 0:
                text_used = self.cyber_prompt_service.conversation_starter_v(text, character_used)
        

        # print('AI:', text.strip())
        if len(text_used) == 0:
            text_used = text
        return self.cleaner_service.clean_text(text_used, use_limit=use_limit)

    
    def v_speak(self, text):
        # fasten answers, since v is talking something else is happening        
        self.piper_service.tts_piper(text.replace("!", "."), model_path=self.config.piper.default_v_male)

    def v_random_filler(self):
        random_filler = [
            '',\
            'So.',\
            'Oh',\
            'Eh',\
            'Huh',\
            'Anyways',\
            'Yeah',\
            'hmmm',\
            'Sure',\
            '',\
            'As I was saying',\
            'Actually',\
            "Like,",\
            "You know,",\
            "Honestly,",\
            "I mean,",\
            "Basically,",\
            "So,",\
            "Actually,",\
            "Right?",\
            "To be honest,",\
            "In fact,"\
            "Um,",\
            "Well,",\
            "See,",\
            "Kind of,",\
            "Sort of,",\
            "You see,",\
            "Literally,",\
            "Frankly,",\
            "To tell the truth",\
            ]
        i = random.randrange(0,len(random_filler))
        if random_filler[i] != '':
            cyberllama.v_speak(random_filler[i])

def get_ssl_context(certfile, keyfile):
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(certfile, keyfile)
    context.set_ciphers("@SECLEVEL=1:ALL")
    return context

if __name__ == "__main__":
    logging.info("Welcome to the desert of the real")
    global cyberllama
    global llava_prompts
    # tts for the npc character before using llava
    llava_prompts = ['Im curious', 'Whats this?', 'Can I touch it?', 'Is it safe?', 'Interesting', 'Does it smell weird ', 'Let me see...']
    cyberllama = Cyberllama()
    logging.info(llava_prompts)
    server = HTTPServer(("0.0.0.0", 8089), WebService)
    set_cyberllama(cyberllama, server)
    context = get_ssl_context("cert.pem", "key.pem")
    server.socket = context.wrap_socket(server.socket, server_side=True)
    server.serve_forever()
