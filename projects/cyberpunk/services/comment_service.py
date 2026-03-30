import random


# TODO: move this to cyberllama
global cached_hunger
global cached_no_hunger
global cached_thirst
global cached_no_thirst
global cached_low_relationship
global cached_mid_relationship
global cached_high_relationship
global cached_low_fun
global cached_mid_fun
global cached_high_fun

class CommentService:

    def __init__(self, config, ollama_service, cleaner_service, basic_prompt_service, wiki_service):
        self.config = config
        self.ollama_service = ollama_service
        self.cleaner_service = cleaner_service
        self.basic_prompt_service = basic_prompt_service
        self.wiki_service = wiki_service
    
    # old OLLAMA_QUEST_RANDOM_LOCATION
    def gen_location_reaction(self):
        return "Generate a brief and short reaction response as if you were interested in going to the location tagged inside '<PROMPT>'. You are roleplaying a character in " + OLLAMA_WORLD_NAME + ". Mention the location<IMPORTANT>1. Do not describe any scene or take the role of the narrator. 2. Remove anything encapsulating with the '*' symbol</IMPORTANT>"

    def get_reaction_from_location(self, qlocation):
        return self.ollama_service.to_ollama_internal(self.gen_location_reaction(), qlocation)


    def gen_stats_comment(self, food, hydration, fun, relationship, character, character_prompt):
        # global system_prompt_template
        text = ''
        if food and food > 0: 
            if int(food) < 15:
                text = text + 'You are starving.'
            elif int(food) < 35:
                text = text + 'Your stomach is asking for food.'
            elif int(food) < 50:
                text = text + 'Maybe it is time that you would eat something.'
            elif int(food) < 80:
                text = text + 'You are satiated.'
            elif int(food) == 100:
                text = text + 'You are full and stuffed.'

        if hydration and hydration > 0: 
            if int(hydration) < 15:
                text = text + 'You are severely dehydrated.'
            elif int(hydration) < 35:
                text = text + 'You need to drink something. You are thirsty.'
            elif int(hydration) < 50:
                text = text + 'Soon you will be needing a little drink.'
            elif int(hydration) < 80:
                text = text + 'Your thirst is quenched.'
            elif int(hydration) == 100:
                text = text + 'You don\'t need to drink something.'

        if fun and fun > 0: 
            if int(fun) < 15:
                text = text + 'You are bored to death. You need some action or go to a club, to a restaurant or something.'
            elif int(fun) < 35:
                text = text + 'You are feeling the monotony and need to do something else.'
            elif int(fun) < 50:
                text = text + 'Soon you will be needing to do something else.'
            elif int(fun) < 80:
                text = text + 'You are having fun.'
            elif int(fun) == 100:
                text = text + 'You are happy.'

        if relationship and relationship > 0: 
            if int(relationship) < 15:
                text = 'You are angry'
            elif int(relationship) < 35:
                text = 'You are slightly annoyed'
            elif int(relationship) < 50:
                text = 'You feel ok'
            elif int(relationship) < 80:
                text = 'You are a positively impacted'
            elif int(relationship) == 100:
                text = 'You and I have a strong connection'
        
        if len(text) == 0:
            return ''
        return self.ollama_service.to_ollama_internal(character_prompt+' Simulate ' + character + '. Generate something you would say to me (V) about your current state of mind. Keep it brief and short.', text)
        
    def gen_district(self, district, sub, time, character, character_prompt):
        if(not district or len(district) < 0):
            return ''
        # global system_prompt_template
        text = ''
        text = text + 'We are in the following district:' + district + '.'
        if(sub and len(sub) > 0):
            text = text + 'To be more precise, the sub district is called: ' + sub + '.'
        
        quest_district_lookup = self.wiki_service.lookup_wiki(district)        
        quest_district_backstory = 'background information about the district: ' + quest_district_lookup

        # FIX ME
        if time and time['td'] and time['th'] and time['tm']:
            if int(time['th']) > 22:
                text = text + 'It is evening.'
            elif int(time['th']) > 18:
                text = text + 'The sun coming down.'
            elif int(time['th']) > 12:
                text = text + 'The sun has come up. It is 1 PM.'
            elif int(time['th']) > 6:
                text = text + 'It is morning. The sun is coming up soon.'
            elif int(time['th']) > 0:
                text = text + 'It is late in the night.'
        
        if len(text) == 0:
            return ''
        return self.ollama_service.to_ollama_internal(
            character_prompt + ' Simulate ' + character + \
            '. Generate a remark you would say to me (V) as ' + character + \
            '. Keep it brief and short.', 
            'What can you tell me about the current district at this time of day? ' + \
                quest_district_backstory + \
                "" + text)

    def gen_quest(self, quest_name, quest_objective, time, character, character_prompt):
        if(not quest_name or len(quest_name) < 0):
            return ''
        # global system_prompt_template
        text = ''
        if time and time['td'] and time['th'] and time['tm']:
            if int(time['th']) > 22:
                text = 'It is evening.'
            elif int(time['th']) > 18:
                text = 'The sun coming down.'
            elif int(time['th']) > 12:
                text = 'The sun has come up. It is 1 PM.'
            elif int(time['th']) > 6:
                text = 'It is morning. The sun is coming up soon.'
            elif int(time['th']) > 0:
                text = 'It is late in the night.'
        if len(text) == 0:
            return ''
        return self.ollama_service.to_ollama_internal(character_prompt + text + ' Simulate ' + character + '. Generate a remark you would say to me (V) as ' + character + ' about the current quest and quest objective. Keep it brief and short.', 'Quest: ' + quest_name + ' Objective: ' + quest_objective + '. Keep it brief and say it from your perspective as if you were talking to me (V)')

    def gen_health(self, health, max_health, armor, time, character, character_prompt):
        if(not health or not max_health or not armor):
            return ''
        # global system_prompt_template
        text = 'V\'s current health status is the following: ' + str(health) + '. The current max health is ' + str(max_health)

        if health > 100:
            text = 'V\'s looks very healthy.'
        elif health > 80:
            text = 'V\'s looks healthy'
        elif health > 50:
            text = 'V\'s looks worn down, from a health perspective'
        elif health > 20:
            text = 'V\'s health looks bad and needs medical attention'
        elif health > 10:
            text = 'V is at the brink of extreme medical attention'
        
        return self.ollama_service.to_ollama_internal(character_prompt+' Simulate ' + character + '. Generate a remark you would say about my health', text)

    def location_comment(
        self,
        character,
        post_data):

        # artists = "(artist),".join(self.keywords_get_random('artists', artists_count))
        # brands = "(brands),".join(self.keywords_get_random('brands', brands_count))
        # characters = "(characters),".join(self.keywords_get_random('characters', characters_count))
        # companies = "(companies),".join(self.keywords_get_random('companies', companies_count))
        # corporations = "(corporations),".join(self.keywords_get_random('corporations', corporations_count))
        # locations = "(locations),".join(self.keywords_get_random('locations', corporations_count))
        # gangs = "(gangs),".join(self.keywords_get_random('gangs', gangs_count))

        # ideas here
        # TODO: implementation of a protocol or format for taking quests in cyberpunk 2077        
        quest_reward = random.randrange(500, 10000)
        # TODO: add background info from wiki if possible
        
        last_location = ''
        if post_data == '':
            return 'dunno what to say'

        if 'prompt_args' in post_data:
            last_location = post_data['prompt_args']
        else:
            return 'dunno what to say'

        
        # wiki files should be written with underscores + all in lower case
        last_location_lookup = self.cleaner_service.clean_text(last_location).replace(' ', '_').lower()
        location_backstory = ''
        
        for f in cyberllama.wiki:
            if last_location_lookup in f["file"]:
                location_backstory = 'background gang information: ' + f['content']

        return self.cyber_prompt_service.conversation_starter_v( "location named " + last_location +
            location_backstory,
            character
        )
    
    def append_hunger_cache(self, item_count):
        global cached_hunger
        cached_hunger = self.ollama_service.to_ollama_internal(OLLAMA_INTERNAL_INSTR_BEGIN, "Generate a list of " + str(item_count) + " things you would say if I ask you wether you are hungry. " + OLLAMA_INTERNAL_GEN_LIST_CLEAN_FIX + OLLAMA_INTERNAL_INSTR_END).split("\n")

    def append_no_hunger_cache(self, item_count):
        global cached_no_hunger
        cached_no_hunger = []
        cached_no_hunger.append(self.basic_prompt_service.gen_list_of(item_count, " things you would say if I ask you wether you are hungry and you are not. "))

    def append_thirst_cache(self, item_count):
        global cached_thirst
        cached_thirst = []
        cached_thirst.append(self.basic_prompt_service.gen_list_of(item_count, " things you would say if I ask you wether you are thirsty and you are not. "))

    def append_no_thirst_cache(self, item_count):
        global cached_no_thirst
        cached_no_thirst = []
        cached_no_thirst.append(self.basic_prompt_service.gen_list_of(item_count, " things you would say if I ask you wether you are thirsty and you are not. "))

    def append_relationship_low_cache(self, item_count):
        global cached_low_relationship
        cached_low_relationship = []
        cached_low_relationship.append(self.basic_prompt_service.gen_list_of(item_count, " things you would say if I ask you anything about our relationship and for now it is as almost non existant. "))

    def append_relationship_mid_cache(self, item_count):
        global cached_mid_relationship
        cached_mid_relationship = []
        cached_mid_relationship.append(self.basic_prompt_service.gen_list_of(item_count, " things you would say if I ask you you anything about our relationship and for now we are good. "))

    def append_relationship_high_cache(self, item_count):
        global cached_high_relationship
        cached_high_relationship = []
        cached_high_relationship.append(self.basic_prompt_service.gen_list_of(item_count, " things you would say if I ask you you anything about our relationship and for now you have a crush on me. "))

    def append_fun_low_cache(self, item_count):
        global cached_low_fun
        cached_low_fun = []
        cached_low_fun.append(self.basic_prompt_service.gen_list_of(item_count, " things you would say if I ask you anything wether you are having fun (but you are totally bored!). "))

    def append_fun_mid_cache(self, item_count):
        global cached_mid_fun
        cached_mid_fun = []
        cached_mid_fun.append(self.basic_prompt_service.gen_list_of(item_count, " things you would say if I ask you you anything wether you are having fun (you do but it could be more). "))

    def append_fun_high_cache(self, item_count):
        global cached_high_fun
        cached_high_fun = []
        cached_high_fun.append(self.basic_prompt_service.gen_list_of(item_count, " things you would say if I ask you you anything wether you are having fun (and you are!). "))

