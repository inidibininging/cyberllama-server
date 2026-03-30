import random
import json
from projects.all.services.basic_prompt_service import OLLAMA_INTERNAL_INSTR_BRIEF_AND_SHORT

class QuestService:
    def __init__(self, config, keyword_service, cyber_prompt_service, wiki_service, cleaner_service):
        self.config = config
        self.keyword_service = keyword_service
        self.cyber_prompt_service = cyber_prompt_service
        self.wiki_service = wiki_service
        self.cleaner_service = cleaner_service

    def quest_generator_server(
        self,
        character,
        artists_count=1, 
        brands_count=1, 
        characters_count=1, 
        companies_count=1, 
        corporations_count=1, 
        gangs_count=1):

        artists = "(artist),".join(self.keyword_service.keywords_get_random('artists', artists_count))
        brands = "(brands),".join(self.keyword_service.keywords_get_random('brands', brands_count))
        characters = "(characters),".join(self.keyword_service.keywords_get_random('characters', characters_count))
        companies = "(companies),".join(self.keyword_service.keywords_get_random('companies', companies_count))
        corporations = "(corporations),".join(self.keyword_service.keywords_get_random('corporations', corporations_count))
        locations = "(locations),".join(self.keyword_service.keywords_get_random('locations', corporations_count))
        gangs = "(gangs),".join(self.keyword_service.keywords_get_random('gangs', gangs_count))

        # ideas here
        # TODO: implementation of a protococonversation_starterl or format for taking quests in cyberpunk 2077
        quest_types = ['kill'] # ['fetch', 'kill', 'escort', 'gather information']
        quest_reward = random.randrange(500, 10000)
        # TODO: add background info from wiki if possible
        quest_type = 'kill' # quest_types[random.randrange(0, len(quest_types) - 1)]
        return self.cyber_prompt_service.conversation_starter_v(
            quest_type + ' quest involving at least one of these: ' + locations + characters + companies + corporations + gangs + brands + ". add information about the quest reward of " + str(quest_reward) + " eddies",
            character)

    def gen_quest_v_text(
        self, 
        character,
        # formerly prompt_args from POST
        quest_data):

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
        # global CURRENT_POST_DATA
        post_data = ''
        if post_data == '':
            post_data = {
                'prompt': 'quest',
                'prompt_args': '',
            }
        data = post_data['prompt_args']
        if data == '' or data == None:
            data = {
                'quest_type': 'kill',
                'gang': 'unknown',
                'location': 'unknown',
                'district': 'unknown'
            }
        # else:
        #     data = json.loads(data)
        quest_data = data
        quest_district = quest_data['districtName']
        quest_type = quest_data['questType']
        quest_location = quest_data['location']
        quest_gang = quest_data['gangName']
        
        # wiki files should be written with underscores + all in lower case
        quest_district_lookup = self.cleaner_service.clean_text(quest_district).replace(' ', '_').lower()
        quest_district_backstory = ''
        quest_location_lookup = self.cleaner_service.clean_text(quest_location['name']).replace(' ', '_').replace('&', 'and').lower()
        quest_location_backstory = ''
        quest_gang_lookup = self.cleaner_service.clean_text(quest_gang).replace(' ', '_').lower()
        quest_gang_backstory = ''
        
        quest_district_lookup = self.wiki_service.lookup_wiki(quest_district_lookup)        
        quest_district_backstory = 'background district information: ' + quest_district_lookup

        quest_location_lookup = self.wiki_service.lookup_wiki(quest_location_lookup)
        quest_location_backstory = 'background location information: ' + quest_location_lookup

        quest_gang_lookup = self.wiki_service.lookup_wiki(quest_gang_lookup)
        quest_gang_backstory = 'background gang information: ' + quest_gang_lookup

        topic = [
            quest_type + ' quest involving at least one of the following location: ' + quest_location['name'] + ' the quest is related to this gang: ' + quest_gang + ". add information about the quest reward of ",
            str(quest_reward) + " eddies. ",
            "you are giving " + self.config.world.player_name + " this quest.",
            quest_district_backstory,
            quest_location_backstory,
            quest_gang_backstory
        ]
        return self.cyber_prompt_service.conversation_starter_v("".join(topic), character)
    
    
    def gen_quest_driver_job_fixer_text(
        self,
        character,
        post_data):
        quest_data = post_data['prompt_args']

        quest_district = quest_data['districtName']
        quest_type = quest_data['questType']
        quest_location = quest_data['location']        
        quest_reward = quest_data['questReward']
        
        # wiki files should be written with underscores + all in lower case
        quest_district_lookup = self.cleaner_service.clean_text(quest_district).replace(' ', '_').lower()
        quest_district_backstory = ''
        quest_location_lookup = self.cleaner_service.clean_text(quest_location['name']).replace(' ', '_').replace('&', 'and').lower()
        quest_location_backstory = ''        
        
        quest_district_lookup = self.wiki_service.lookup_wiki(quest_district_lookup)        
        quest_district_backstory = 'background district information: ' + quest_district_lookup

        quest_location_lookup = self.wiki_service.lookup_wiki(quest_location_lookup)
        quest_location_backstory = 'background location information: ' + quest_location_lookup

        topic = [
            'You are giving ' + self.config.world_data.player_name + ' a job. The job involves the following:',
            quest_type + '(' + self.config.world.player_name + ' [NOT YOU!!!] has to meet a client and drive him around) quest involving at least one of the following location: ' + quest_location['name'] + ". add information about the quest reward of ",
            str(quest_reward) + " eddies. ",
            "you are trying to persuade " + self.config.world.player_name + " to help you with the quest.",
            quest_district_backstory,
            quest_location_backstory,            
            OLLAMA_INTERNAL_INSTR_BRIEF_AND_SHORT
        ]
        return self.cyber_prompt_service.conversation_starter_npc(
            "".join(topic),
            character)

    def gen_quest_kill_job_fixer_text(
        self,
        character,
        post_data):
        quest_data = post_data['prompt_args']
        quest_district = quest_data['districtName']
        quest_type = quest_data['questType']
        quest_location = quest_data['location']
        quest_gang = quest_data['gangName']
        quest_reward = quest_data['questReward']
        
        # wiki files should be written with underscores + all in lower case
        quest_district_lookup = self.cleaner_service.clean_text(quest_district).replace(' ', '_').lower()
        quest_district_backstory = ''
        quest_location_lookup = self.cleaner_service.clean_text(quest_location['name']).replace(' ', '_').replace('&', 'and').lower()
        quest_location_backstory = ''
        quest_gang_lookup = self.cleaner_service.clean_text(quest_gang).replace(' ', '_').lower()
        quest_gang_backstory = ''
        
        quest_district_lookup = self.wiki_service.lookup_wiki(quest_district_lookup)        
        quest_district_backstory = 'background district information: ' + quest_district_lookup

        quest_location_lookup = self.wiki_service.lookup_wiki(quest_location_lookup)
        quest_location_backstory = 'background location information: ' + quest_location_lookup

        quest_gang_lookup = self.wiki_service.lookup_wiki(quest_gang_lookup)
        quest_gang_backstory = 'background gang information: ' + quest_gang_lookup


        topic = [
            'We are roleplaying in the world of ' + self.config.world.world_name,
            'You ('+ character +') are talking to me ('+ self.config.world.player_name +')',
            'You are giving me (' + self.config.world.player_name + ') a job. You are a fixer. A fixer is someone who gives jobs to mercenaries. The job involves the following:',
            self.quest_type_to_string(quest_type) + ' job involving at least one of the following location: ' + quest_location['name'] + ' the quest is related to this gang: ' + quest_gang + ". add information about the quest reward of ",
            str(quest_reward) + " eddies. ",
            quest_district_backstory,
            quest_location_backstory,
            quest_gang_backstory,
            "You ("+ character+") are trying to describe the job to  " + self.config.world.player_name + ". Write as if you were give the tasks to me",
            # OLLAMA_INTERNAL_INSTR_BRIEF_AND_SHORT
        ]
        return self.cyber_prompt_service.ollama_service.to_ollama_internal(
            'You will assume the role of ' + character + ', a fixer. You are talking to me (' + self.config.world.player_name + '). Write from your perspective only. Give me only the dialog lines you would say and nothing more. Think hard, before you write. DO NOT CONFLATE YOUR NAME WITH MINE. WRITE TO ME. KEEPT IT SHORT AND BRIEF',
            "".join(topic),
            )
    def quest_type_to_string(self, quest_type):
        if quest_type == 1:
            return 'Kill'
        if quest_type == 2:
            return 'Drive'
        if quest_type == 3:
            return 'Rescue'
        if quest_type == 4:
            return 'Hack'
    def get_random_quest(self, character):
        quest_line = self.cyber_prompt_service.conversation_starter_v('random quest', character).strip()
        fake_conversation = 'You are ' + self.config.world.player_name + ', the main character from ' + self.config.world.world_name + ', talking to ' + character + ' . Generate a line with the following topic as if you were talking to ' + character + ': random quest.' + "\nResponse:" + quest_line
        possible_quest = self.ollama_service.to_ollama_internal('You are a helpful cyberllama', "Given is the following conversation till now: \"" + fake_conversation + "\". How would you structure this into a quest made in json. Use only the following attributes: quest_name(String), quest_objective(String), location(String), quest_type(String) (fetch, go_to, kill)? Give me only the json output")
        try:
            return json.loads(posssible_quest)
        except Exception as e:
            logging.error(f"An error occurred during speech playback: {str(e)}")
        return {}