import uuid
import collections.abc
import sqlite3
import random
from projects.cyberpunk.services.sqlite3_cache_service import COL_SPEAKER_ID

DEFAULT_MOOD_VALUE=50
DEFAULT_OCEAN_NO_VALUE=-1

class WorldData:

    def __init__(self):
        self.time = None
        self.health = None
        self.max_health = None
        self.armor = None
        self.gender = None
        self.location_name = None
        self.quest_name = None
        self.quest_objective = None
        self.lifepath = None
        self.district = None
        self.sub_district = None
        self.food = None
        self.hydration = None
        self.fun = None
        self.relationship = None
        self.combat_state = None
        self.combat_time = None
        self.combat_last_combat = None
        self.combat_duration = None
        self.npc_id_hash = None
        self.npc_record_id_hash = None
        self.npc_class_name = None
        self.npc_display_name = None
        self.npc_tweaks_name = None
        self.npc_appearance = None
        self.npc_gender = None
        self.npc_voice = None
        self.npc_voice_engine = None
        self.npc_voice_arg = None
        self.npc_speaker_id = 0
        self.npc_speaker_tags = None
        self.npc_voice_pitch = 0
        self.npc_backstory = ''
        self.is_main_npc = 0

    def set_default_empty_world_data(self):
        self.id = ''
        self.time = ''
        self.session = ''
        self.health = ''
        self.max_health = ''
        self.armor = ''
        self.gender = ''
        self.location_name = ''
        self.quest_name = ''
        self.quest_objective = ''
        self.lifepath = ''
        self.district = ''
        self.sub_district = ''
        self.food = ''
        self.hydration = ''
        self.fun = ''
        self.relationship = ''
        self.openness = -1
        self.conscientiousness = -1
        self.extraversion = -1
        self.agreeableness = -1
        self.neuroticism = -1
        self.combat_state = ''
        self.combat_time = ''
        self.combat_last_combat = ''
        self.combat_duration = ''
        self.npc_id_hash = ''
        self.npc_record_id_hash = ''
        self.npc_class_name = ''
        self.npc_display_name = ''
        self.npc_tweaks_name = ''
        self.npc_appearance = ''
        self.npc_gender = ''
        self.npc_moods = []
        self.last_action = ''
        self.npc_voice = None
        self.npc_voice_arg = None            
        self.npc_voice_engine = None
        self.npc_speaker_id = 0
        self.npc_speaker_tags = None
        self.npc_changed = True

    def set_json_player_health_and_armor(self, data):
        health_armor = data.get('p_health_armor', 
        {
            "health": 0,
            "maxHealth": 0,
            "armor": 0
        })
        self.health = health_armor.get('health', 0)
        self.max_health = health_armor.get('maxHealth', 0)
        self.armor = health_armor.get('armor', 0)

    def set_json_location(self, data):
        location = data.get('p_location', {
                "name": "unknown",
                "x": 0,
                "y": 0,
                "z": 0,
            })
        self.location_name = location.get('name', 'unknown')
        self.x = location.get('x', 0)
        self.y = location.get('y', 0)
        self.z = location.get('z', 0)

    def set_json_combat(self, data):
        combat_state = data.get('p_combat_state', {
            "state": 0,
            "time": 0,
            "last_combat": 0,
            "combat_duration": 0,
        })
        self.combat_state =  combat_state.get('state', 0)
        self.combat_time =  combat_state.get('time', 0)
        self.combat_last_combat =  combat_state.get('last_combat', 0)
        self.combat_duration =  combat_state.get('combat_duration', 0)

    def set_json_district(self, data):
        district = data.get('p_district', {
            "main": "unknown",
            "sub": "unknown",
        })
        self.district =     district.get('main', 'unknown')
        self.sub_district = district.get('sub', 'unknown')

    def set_json_player_stats(self, data):
        stats = data.get('p_stats', {
            "food": 0,
            "hydration": 0,
            "fun": 0,
            "relationship": 0,
        })
        self.food = stats.get('food', DEFAULT_MOOD_VALUE)
        self.hydration = stats.get('hydration', DEFAULT_MOOD_VALUE)
        self.fun = stats.get('fun', DEFAULT_MOOD_VALUE)
        self.relationship = stats.get('relationship', DEFAULT_MOOD_VALUE)
        self.openness = stats.get('openness',DEFAULT_OCEAN_NO_VALUE)
        self.conscientiousness = stats.get('conscientiousness', DEFAULT_OCEAN_NO_VALUE)
        self.extraversion = stats.get('extraversion', DEFAULT_OCEAN_NO_VALUE)
        self.agreeableness = stats.get('agreeableness', DEFAULT_OCEAN_NO_VALUE)
        self.neuroticism = stats.get('neuroticism', DEFAULT_OCEAN_NO_VALUE)

    def set_json_quest(self, data):
        quest = data.get('p_quest', {
            "name": "unknown",
            "objective": "unknown",
        })
        self.quest_name = quest.get('name')
        self.quest_objective = quest.get('objective')

    def set_json_npc(self, npc):
        self.npc_id_hash = npc.get('id_hash', '')
        self.npc_record_id_hash = npc.get('record_id_hash', '')
        self.npc_class_name = npc.get('class_name', '')
        self.npc_display_name = npc.get('display_name', '')
        self.npc_tweaks_name = npc.get('tweaks_name', '')
        self.npc_appearance = npc.get('appearance', '')
        self.npc_gender = npc.get('gender', '')
        

    def set_json_player_misc(self, data):
        self.time = data.get('p_time', 0)
        self.gender = data.get('p_gender', 'unknown')
        self.lifepath = data.get('p_lifepath', '')
        self.last_action = data.get('p_last_action', '')     

    def get_appearance_keywords(self):
        pass
    

    def is_different_npc(self, external_world_data):
        return self.npc_record_id_hash != external_world_data.npc_record_id_hash

    def try_set_npc_override(self, npc_overrides, keywords, wiki):
        npc_mention = self.npc_appearance
        for key in keywords['main_npc']:
            # before: if isinstance(cyberllama.world_data.npc_appearance, str) and key.lower() in self.npc_appearance.lower():
            if isinstance(self.npc_appearance, str) and key.lower() in self.npc_appearance.lower():
                self.is_main_npc = 1
                npc_mention = key

        self.npc_found_override = False
        for npc_override in npc_overrides:
            if type(npc_mention) is list:
                for tag in npc_mention:                                                
                    if npc_overrides[npc_override].name in tag \
                    or tag in npc_overrides[npc_override].name:
                        self.npc_found_override = True
                        break
            else:
                if npc_mention.lower() in \
                    npc_overrides[npc_override].name:                    
                    self.npc_found_override = True
                    break

            if self.npc_found_override == True:
                word_data_keys = self.__dict__.keys()
                override_dict = npc_overrides[npc_override].__dict__
                for key_override in override_dict:
                    if key_override in word_data_keys:
                        setattr(world_data, key_override, override_dict[key_override])

                if len(npc_overrides[npc_override].wiki_name) != 0:
                    for f in wiki:
                        if npc_overrides[npc_override].wiki_name.lower() in f["file"].lower():
                            self.npc_backstory = f["content"]
                        break
                else:
                    self.npc_backstory = npc_overrides[npc_override].npc_backstory


    def is_list(self, var):
        if isinstance(var, list) or isinstance(var, tuple) or isinstance(var, collections.abc.Sequence):
            return True
        # if '[' in str(var) and ']' in str(var):
        #     return True
        return False

    def split_npc_appearance(self):
        if not isinstance(self.npc_appearance, str):
            return
        
        if len(self.npc_appearance) == 0:
            self.npc_appearance = []
            return
        
        appearance_tags = self.npc_appearance.split('_')
        # append appearance names as tags
        self.npc_appearance = []
        for atag in appearance_tags:
            if len(atag.replace('_', '').strip()) < 2:
                continue            
            self.npc_appearance.append(atag.replace('_', '').replace(' ', '').strip())

    def tts_piper_get_gender_speaker_id_by_tags(self, config, gender, tags=[]):
        if gender == 'female':
            gender = 'v_output_f_map'
        elif gender == 'male':
            gender = 'v_output_m_map'
        else:
            return 0
        conn = sqlite3.connect(config.piper.multi_voice.libritts_r.dataset)
        cur = conn.cursor()        
        where_sql = ''
        if len(tags) > 0:
            where_sql = "where " + " and ".join(list(map(lambda tag: "m.tags like '%" + tag + "%'", tags)))        
        sql = "select m.speaker_id, m.tags from " + gender + " m " + where_sql
        rc = cur.execute(sql)
        res = rc.fetchall()
        conn.close()
        lres = len(res)
        if lres == 1:
            return int(res[0][COL_SPEAKER_ID])
        if lres > 0:
            return int(res[random.randrange(0, len(res))][COL_SPEAKER_ID])
        return 0
    
    def addreplace_fixer_to_cache(self, npc_data, config, cyberllama):
        if not npc_data['id_hash'] in cyberllama.npc_cache:        
            cyberllama.npc_cache[npc_data['id_hash']] = {
                'npc_id_hash': npc_data['id_hash'],
                'npc_record_id_hash': npc_data['id_hash'],
                'npc_class_name': npc_data['class_name'],
                'npc_display_name': npc_data['display_name'],
                'npc_tweaks_name': npc_data['tweaks_name'],
                'npc_appearance': npc_data['appearance'],
                'npc_gender': self.get_gender_based_appearance(npc_data),
                # 'npc_backstory': npc_data.npc_backstory,

                # 'npc_voice': self.npc_voice,
                # 'npc_voice_engine': self.npc_voice_engine,
                # 'npc_voice_arg': self.npc_voice_arg,
                # 'npc_speaker_id': self.npc_speaker_id,
                # 'npc_speaker_tags': self.npc_speaker_tags,
                'npc_conversation': [],
                # stats are not stored in cache
                # here stats come from client
                # these stats will be modified later on by cache_db_ask_ollama
                'food': DEFAULT_MOOD_VALUE,
                'hydration': DEFAULT_MOOD_VALUE,
                'fun': DEFAULT_MOOD_VALUE,
                'relationship': DEFAULT_MOOD_VALUE,
                'last_action': []
            }

        if not 'npc_voice' in cyberllama.npc_cache[npc_data['id_hash']] and\
            not 'npc_voice_arg' in cyberllama.npc_cache[npc_data['id_hash']] and\
            not 'npc_voice_engine' in cyberllama.npc_cache[npc_data['id_hash']]:
            selected_voice_engine = random.randrange(0, len(config.npc_tts))
            use_multilingual = random.randrange(0,100) > 50 and config.piper.multi_voice.libritts_r.path
            
            if config.npc_tts[selected_voice_engine] == 'piper':
                if use_multilingual:
                    voices = [config.piper.multi_voice.libritts_r.path]
                else:
                    if cyberllama.npc_cache[npc_data['id_hash']]['npc_gender'] == 'Female':
                        voices = list(config.piper.female_voices)
                    else:
                        voices = list(config.piper.male_voices)

            elif config.npc_tts[selected_voice_engine] == 'kokoro':
                if cyberllama.npc_cache[npc_data['id_hash']]['npc_gender'] == 'Female':
                    voices = list(config.kokoro.female_voices)
                else:
                    voices = list(config.kokoro.male_voices)
                    
            new_voice = ''
            lvoices = len(voices)
            if lvoices == 0:
                pass
            elif lvoices == 1:
                new_voice = voices[0]
            else:
                new_voice = voices[random.randrange(0, len(voices) - 1)]
            cyberllama.npc_cache[npc_data['id_hash']]['npc_voice'] = new_voice
            cyberllama.npc_cache[npc_data['id_hash']]['npc_voice_arg'] = new_voice
            cyberllama.npc_cache[npc_data['id_hash']]['npc_voice_engine'] = config.npc_tts[selected_voice_engine]
            
            if config.npc_tts[selected_voice_engine] == 'piper' and use_multilingual:
                cyberllama.npc_cache[npc_data['id_hash']]['npc_speaker_id'] = self.tts_piper_get_gender_speaker_id_by_tags(config, cyberllama.npc_cache[npc_data['id_hash']]['npc_gender'].lower())
            else:
                cyberllama.npc_cache[npc_data['id_hash']]['npc_speaker_id'] = 0

        

    def setup_npc_voice(self, config, npc_cache):

        # if self.npc_gender == 'Female' and not npc_found_override:
        if not self.npc_found_override:
            # check for multiple entries
            voices = []
            if not type(config.npc_tts) is list:
                raise 'npc_tts is not a list'
            else:
                selected_voice_engine = random.randrange(0, len(config.npc_tts))
                use_multilingual = random.randrange(0,100) > 50 and config.piper.multi_voice.libritts_r.path
                if config.npc_tts[selected_voice_engine] == 'piper':
                    if use_multilingual:
                        voices = [config.piper.multi_voice.libritts_r.path]
                    else:
                        if self.npc_gender == 'Female':
                            voices = list(config.piper.female_voices)
                        else:
                            voices = list(config.piper.male_voices)

                elif config.npc_tts[selected_voice_engine] == 'kokoro':
                    if self.npc_gender == 'Female':
                        voices = list(config.kokoro.female_voices)
                    else:
                        voices = list(config.kokoro.male_voices)                    

                # do not use random voice. use the last voice stored
                if self.npc_id_hash in npc_cache:
                    self.npc_voice_engine = npc_cache[self.npc_id_hash]['npc_voice_engine']
                    self.npc_voice = npc_cache[self.npc_id_hash]['npc_voice']
                    self.npc_voice_arg = npc_cache[self.npc_id_hash]['npc_voice_arg']
                    self.npc_speaker_id = npc_cache[self.npc_id_hash]['npc_speaker_id']
                    self.npc_speaker_tags = '' if not 'npc_speaker_tags' in npc_cache[self.npc_id_hash] else npc_cache[self.npc_id_hash]['npc_speaker_tags']
                else:
                    new_voice = ''
                    lvoices = len(voices)
                    if lvoices == 0:
                        pass
                    elif lvoices == 1:
                        new_voice = voices[0]
                    else:
                        new_voice = voices[random.randrange(0, len(voices) - 1)]
                    self.npc_voice = new_voice
                    self.npc_voice_arg = new_voice
                    self.npc_voice_engine = config.npc_tts[selected_voice_engine]
                    
                    if config.npc_tts[selected_voice_engine] == 'piper' and use_multilingual:
                        self.npc_speaker_id = self.tts_piper_get_gender_speaker_id_by_tags(config, self.npc_gender.lower())
                    else:
                        self.npc_speaker_id = 0

    def make_world_data(self, data, npc, cyberllama):
        if data is None:
            self.set_default_empty_world_data()
        else:
            self.id = str(uuid.uuid4())
            self.session = data.get('session', '')
            self.set_json_player_misc(data)
            self.set_json_player_health_and_armor(data)
            self.set_json_player_stats(data)
            self.set_json_district(data)
            self.set_json_quest(data)
            # self.set_json_ocean(stats)
            self.set_json_combat(data)
            self.set_json_npc(npc)
            self.set_gender_based_appearance()
            
            # self.location_time = data['p_location']['time']

        npc_changed = self.is_different_npc(cyberllama.world_data)

        if npc_changed:
            self.npc_gender = ''            
            self.npc_voice = ''
            self.npc_voice_engine = ''
            self.npc_voice_arg = ''            
            self.npc_speaker_id = 0
            self.npc_speaker_tags = ''
            self.npc_voice_pitch = 1
            self.is_main_npc = 0
            self.npc_backstory = ''

            # append appearance names as tags
            self.split_npc_appearance()
            self.set_gender_based_appearance()
            self.try_set_npc_override(cyberllama.character_overrides_service.npc_overrides, cyberllama.keywords_service.keywords, cyberllama.wiki_service.wiki)
            self.setup_npc_voice(cyberllama.config, cyberllama.npc_cache)
            
            if len(self.npc_voice) == 0 or len(self.npc_gender) == '':
                print('WARNING: no npc voice detected. preselecting male as default. actually it should be a robot/neutral voice')

            # gen erate only if not in cache
            if self.npc_id_hash in cyberllama.npc_cache:
                self.npc_backstory = '' if 'npc_backstory' not in cyberllama.npc_cache[self.npc_id_hash] else cyberllama.npc_cache[self.npc_id_hash]['npc_backstory']

            else:
                extra = ''
                if cyberllama.npc_evaluator_service.is_nc_resident(self.npc_tweaks_name):
                    person_reference = 'them'
                    if self.npc_gender == 'Male':
                        person_reference = 'he'
                    elif self.npc_gender == 'Female':
                        person_reference = 'she'                    
                    extra = '5. And important: ' + cyberllama.config.world.player_name + ' (the protagonist of the story does not know anything about this CHARACTER. ' + person_reference + ' is a complete stranger to ' + cyberllama.config.world.player_name + '. They don\'t know each other)'
                
                # add corporation background if corporation name matches
                random_corporation = ''
                random_corporation_info = ''
                if 'corpo' in self.npc_appearance:
                    random_corporation = cyberllama.keywords_service.keywords_get_random('corporations', 1)[0]
                    random_corporation_info = cyberllama.wiki_service.lookup_wiki(random_corporation)
                    if random_corporation_info == '(none available)':
                        random_corporation_info = ''
                    else:
                        '<corporation-background>'+random_corporation_info+'</corporation-background>'
                    random_corporation = '<corporation>' + random_corporation + '</corporation>'
                
                # todo: recover previous npc background if possible
                if cyberllama.config.generate_background_story:
                    self.npc_backstory = cyberllama.ollama_service.to_ollama_internal(\
                        'You are functioning now as a character generator of a character in the world of ' + cyberllama.config.world.world_name + '. Write the background story', \
                        '1. generate a character background for an npc with the this gender and tags. tags are based on appearance of the NPC. DO NOT GENERATE A NAME\n'+\
                        '2. keep it brief and short. write 2 to 3 short and brief sentences about the character at maximum \n'+\
                        '3. Don\'t give me any explanations. Give me only the the background story \n'+\
                        '4. Take into account the tags provided for the background story of the character\n'+\
                        extra+\
                        '<gender>'+self.npc_gender+'</gender>\n'+\
                        '<tags>'+', '.join(self.npc_appearance)+'</tags>\n')+\
                        random_corporation+\
                        random_corporation_info
                else:
                    self.npc_backstory = 'You a night city resident'

        else:
            self.npc_gender = cyberllama.world_data.npc_gender            
            self.npc_voice = cyberllama.world_data.npc_voice
            self.npc_voice_engine = cyberllama.world_data.npc_voice_engine
            self.npc_voice_arg = cyberllama.world_data.npc_voice_arg
            self.npc_speaker_id = cyberllama.world_data.npc_speaker_id
            self.npc_voice_pitch = cyberllama.world_data.npc_voice_pitch
            self.is_main_npc = cyberllama.world_data.is_main_npc
            self.npc_backstory = cyberllama.world_data.npc_backstory

        
        # todo: find the avg of the current western / eastern world
        # extrapolate negatively
        self.set_ocean_if_empty(cyberllama.ocean_service)
        
        self.npc_changed = npc_changed
        cyberllama.sqlite3_cache_service.save_world_data(self)
        return self

    def set_gender_based_appearance(self):
        if '_wa' in self.npc_appearance\
            or 'wa_' in self.npc_appearance\
            or 'waf_' in self.npc_appearance\
            or '_waf' in self.npc_appearance:
            self.npc_gender = 'Female'
        elif '_ma' in self.npc_appearance \
            or 'ma_' in self.npc_appearance \
            or 'maf_' in self.npc_appearance \
            or 'maf_' in self.npc_appearance \
            or '_mb' in self.npc_appearance \
            or 'mb_' in self.npc_appearance:
            self.npc_gender = 'Male'

        if 'wa' in self.npc_appearance or \
            'waf' in self.npc_appearance:
            self.npc_gender = 'Female'

    def get_gender_based_appearance(self, npc_data):
        if 'gender' in npc_data and 'ma' in npc_data['gender']:
            return 'Male'
        if 'gender' in npc_data and 'wa' in npc_data['gender']:
            return 'Female'
        if '_wa' in npc_data['appearance']\
            or 'wa_' in npc_data['appearance']\
            or 'waf_' in npc_data['appearance']\
            or '_waf' in npc_data['appearance']:
            return 'Female'
        elif '_ma' in npc_data['appearance'] \
            or 'ma_' in npc_data['appearance'] \
            or 'maf_' in npc_data['appearance'] \
            or 'maf_' in npc_data['appearance'] \
            or '_mb' in npc_data['appearance'] \
            or 'mb_' in npc_data['appearance']:
            return 'Male'

        if 'wa' in npc_data['appearance'] or \
            'waf' in npc_data['appearance']:
            return 'Female'
        
        return 'Male'

    def set_ocean_if_empty(self, ocean_service):
        if  self.openness == -1 and \
            self.conscientiousness == -1 and \
            self.extraversion == -1 and \
            self.agreeableness == -1 and \
            self.neuroticism == -1:
            
            self.ocean = ocean_service.gen_ocean()
            self.openness = self.ocean["openness"]
            self.conscientiousness = self.ocean["conscientiousness"]
            self.extraversion = self.ocean["extraversion"]
            self.agreeableness = self.ocean["agreeableness"]
            self.neuroticism = self.ocean["neuroticism"]

    def sync_npc_data(self, cyberllama, world_data):        
        # world_data = cyberllama.world_data
        last_v_responses = cyberllama.last_v_responses
        # updates the last npc in the npc cache
        # this happens if 
        # new npc client data is not equal to current one
        data_corrupted_or_not_init = not (world_data and \
            self.npc_record_id_hash and \
            cyberllama.world_data and \
            cyberllama.world_data.npc_record_id_hash)
                        
        if not world_data:
            #raise 'DATA CORRUPTED'
            return
        if not self.npc_record_id_hash:
            return
            #raise 'DATA CORRUPTED - no npc record id hash / means client side error'

        if not cyberllama.world_data:
            # don't need to do anything. because world data will be passed on (see code below below => after this mess)
            print('WORLD DATA NOT STORED - possible clean start')
            print('Saving new npc cache data here')
            cyberllama.npc_cache[cyberllama.world_data.npc_id_hash] = {
                'npc_id_hash': cyberllama.world_data.npc_id_hash,
                'npc_record_id_hash': cyberllama.world_data.npc_record_id_hash,
                'npc_class_name': cyberllama.world_data.npc_class_name,
                'npc_display_name': cyberllama.world_data.npc_display_name,
                'npc_tweaks_name': cyberllama.world_data.npc_tweaks_name,
                'npc_appearance': cyberllama.world_data.npc_appearance,
                'npc_gender': cyberllama.world_data.npc_gender,
                'npc_backstory': cyberllama.world_data.npc_backstory,
                'npc_voice': cyberllama.world_data.npc_voice,
                'npc_voice_engine': cyberllama.world_data.npc_voice_engine,
                'npc_voice_arg': cyberllama.world_data.npc_voice_arg,
                'npc_speaker_id': cyberllama.world_data.npc_speaker_id,
                'npc_speaker_tags': cyberllama.world_data.npc_speaker_tags,
                'npc_conversation': [],
                # stats are not stored in cache
                # here stats come from client
                # these stats will be modified later on by cache_db_ask_ollama
                'food': DEFAULT_MOOD_VALUE,
                'hydration': DEFAULT_MOOD_VALUE,
                'fun': DEFAULT_MOOD_VALUE,
                'relationship': DEFAULT_MOOD_VALUE,
                'last_action': cyberllama.world_data.last_action
            }
        else:
            if not cyberllama.world_data.npc_record_id_hash:
                print('DATA CORRUPTED - no npc record id hash / means data stored before didnt have a record id hash')
                cyberllama.npc_cache[world_data.npc_id_hash] = {
                    'npc_id_hash': self.npc_id_hash,
                    'npc_record_id_hash': self.npc_record_id_hash,
                    'npc_class_name': self.npc_class_name,
                    'npc_display_name': self.npc_display_name,
                    'npc_tweaks_name': self.npc_tweaks_name,
                    'npc_appearance': self.npc_appearance,
                    'npc_gender': self.npc_gender,
                    'npc_backstory': self.npc_backstory,
                    'npc_voice': self.npc_voice,
                    'npc_voice_engine': self.npc_voice_engine,
                    'npc_voice_arg': self.npc_voice_arg,
                    'npc_speaker_id': self.npc_speaker_id,
                    'npc_speaker_tags': self.npc_speaker_tags,
                    'npc_conversation': [],
                    # stats are not stored in cache
                    # here stats come from client
                    # these stats will be modified later on by cache_db_ask_ollama
                    'food': DEFAULT_MOOD_VALUE,
                    'hydration': DEFAULT_MOOD_VALUE,
                    'fun': DEFAULT_MOOD_VALUE,
                    'relationship': DEFAULT_MOOD_VALUE,
                    'last_action': self.last_action
                }
            else:
                # new data, npc is the same guy
                client_npc_is_the_same = self.npc_record_id_hash == cyberllama.world_data.npc_record_id_hash

                if client_npc_is_the_same:
                    # npc is the same as before
                    # data has been stored before
                    # data will be updated
                    if not cyberllama.world_data.npc_id_hash in cyberllama.npc_cache:
                        cyberllama.npc_cache[cyberllama.world_data.npc_id_hash] = cyberllama.world_data.__dict__
                    else:
                        same_npc = cyberllama.npc_cache[cyberllama.world_data.npc_id_hash]
                        same_npc['npc_record_id_hash'] = self.npc_record_id_hash
                        same_npc['npc_class_name'] = self.npc_class_name
                        same_npc['npc_display_name'] = self.npc_display_name
                        same_npc['npc_tweaks_name'] = self.npc_tweaks_name
                        same_npc['npc_appearance'] = self.npc_appearance
                        same_npc['last_action'] = self.last_action

                else:
                    # npc is different
                    # cache CURRENT npc data (stored in world_data) before assigning new data
                    # old npc data exists in npc cache                            
                    if cyberllama.world_data.npc_id_hash in cyberllama.npc_cache:
                        old_npc = cyberllama.npc_cache[cyberllama.world_data.npc_id_hash]
                        # old_npc['npc_id_hash'] = cyberllama.world_data.npc_id_hash
                        old_npc['npc_record_id_hash'] = cyberllama.world_data.npc_record_id_hash
                        old_npc['npc_class_name'] = cyberllama.world_data.npc_class_name
                        old_npc['npc_display_name'] = cyberllama.world_data.npc_display_name
                        old_npc['npc_tweaks_name'] = cyberllama.world_data.npc_tweaks_name
                        old_npc['npc_appearance'] = cyberllama.world_data.npc_appearance
                        old_npc['npc_gender'] = cyberllama.world_data.npc_gender                                
                        # old_npc['npc_backstory'] = cyberllama.world_data.npc_backstory
                        # old_npc['npc_voice'] = cyberllama.world_data.npc_voice
                        old_npc['npc_conversation'] = cyberllama.cached_conversation_lines
                        old_npc['food'] = cyberllama.npc_cache[cyberllama.world_data.npc_id_hash]['food']
                        old_npc['hydration'] = cyberllama.npc_cache[cyberllama.world_data.npc_id_hash]['hydration']
                        old_npc['fun'] = cyberllama.npc_cache[cyberllama.world_data.npc_id_hash]['fun']
                        old_npc['relationship'] = cyberllama.npc_cache[cyberllama.world_data.npc_id_hash]['relationship']
                        old_npc['last_action'] = cyberllama.world_data.last_action
                    else:
                        # npc changed and
                        # current npc data has not been stored yet
                        # create entry
                        cyberllama.npc_cache[cyberllama.world_data.npc_id_hash] = {
                            'npc_id_hash': cyberllama.world_data.npc_id_hash,
                            'npc_record_id_hash': cyberllama.world_data.npc_record_id_hash,
                            'npc_class_name': cyberllama.world_data.npc_class_name,
                            'npc_display_name': cyberllama.world_data.npc_display_name,
                            'npc_tweaks_name': cyberllama.world_data.npc_tweaks_name,
                            'npc_appearance': cyberllama.world_data.npc_appearance,
                            'npc_gender': cyberllama.world_data.npc_gender,
                            'npc_backstory': cyberllama.world_data.npc_backstory,
                            'npc_voice': cyberllama.world_data.npc_voice,
                            'npc_voice_engine': cyberllama.world_data.npc_voice_engine,
                            'npc_voice_arg': cyberllama.world_data.npc_voice_arg,
                            'npc_speaker_id': cyberllama.world_data.npc_speaker_id,
                            'npc_speaker_tags': cyberllama.world_data.npc_speaker_tags,
                            'npc_conversation': cyberllama.cached_conversation_lines,
                            # stats are not stored in cache
                            # here stats come from client
                            # these stats will be modified later on by cache_db_ask_ollama
                            'food': cyberllama.world_data.food,
                            'hydration': cyberllama.world_data.hydration,
                            'fun': cyberllama.world_data.fun,
                            'relationship': cyberllama.world_data.relationship,
                            'last_action': cyberllama.world_data.last_action
                        }

                    # and now check if new npc is also in npc cache
                    if self.npc_id_hash in cyberllama.npc_cache:
                        new_npc = cyberllama.npc_cache[world_data.npc_id_hash]
                        # new_npc['npc_id_hash'] = cyberllama.world_data.npc_id_hash
                        new_npc['npc_record_id_hash'] = self.npc_record_id_hash
                        new_npc['npc_class_name'] = self.npc_class_name
                        new_npc['npc_display_name'] = self.npc_display_name
                        new_npc['npc_tweaks_name'] = self.npc_tweaks_name
                        new_npc['npc_appearance'] = self.npc_appearance
                        new_npc['npc_gender'] = self.npc_gender                                
                        # new_npc['npc_backstory'] = self.npc_backstory
                        # new_npc['npc_voice'] = self.npc_voice
                        # new_npc['npc_conversation'] = cached_conversation_lines
                        # # stats are not stored in cache
                        # # here stats come from client
                        # # these stats will be modified later on by cache_db_ask_ollama
                        # new_npc['food'] = npc_cache[cyberllama.world_data.npc_id_hash]['food']
                        # new_npc['hydration'] = npc_cache[cyberllama.world_data.npc_id_hash]['hydration']
                        # new_npc['fun'] = npc_cache[cyberllama.world_data.npc_id_hash]['fun']
                        # new_npc['relationship'] = npc_cache[cyberllama.world_data.npc_id_hash]['relationship']
                        new_npc['last_action'] = self.last_action
                    else:
                        # npc changed and
                        # current npc data has not been stored yet
                        # create entry
                        cyberllama.npc_cache[world_data.npc_id_hash] = {
                            'npc_id_hash': self.npc_id_hash,
                            'npc_record_id_hash': self.npc_record_id_hash,
                            'npc_class_name': self.npc_class_name,
                            'npc_display_name': self.npc_display_name,
                            'npc_tweaks_name': self.npc_tweaks_name,
                            'npc_appearance': self.npc_appearance,
                            'npc_gender': self.npc_gender,
                            'npc_backstory': self.npc_backstory,
                            'npc_voice': self.npc_voice,
                            'npc_voice_arg': self.npc_voice_arg,
                            'npc_voice_engine': self.npc_voice_engine,
                            'npc_speaker_id': self.npc_speaker_id,
                            'npc_speaker_tags': self.npc_speaker_tags,
                            'npc_conversation': [],
                            # stats are not stored in cache
                            # here stats come from client
                            # these stats will be modified later on by cache_db_ask_ollama
                            'food': DEFAULT_MOOD_VALUE,
                            'hydration': DEFAULT_MOOD_VALUE,
                            'fun': DEFAULT_MOOD_VALUE,
                            'relationship': DEFAULT_MOOD_VALUE,
                            'last_action': self.last_action
                        }

                    cyberllama.cached_conversation_lines = []
                    
        if not (world_data.npc_id_hash in cyberllama.npc_cache):
            cyberllama.v_speak('Huh')
            # raise 'Could not cache npc'