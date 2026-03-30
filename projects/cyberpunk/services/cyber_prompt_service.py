import random
import uuid
import logging
from projects.cyberpunk.services.sqlite3_cache_service import COL_ID, COL_CHARACTER, COL_LINE, COL_PARENT, COL_LOCATION, COL_FACTION, COL_MOOD
from projects.all.services.basic_prompt_service import OLLAMA_INTERNAL_INSTR_DO_NOT_ENUMERATE, OLLAMA_INTERNAL_INSTR_DO_NOT_NARRATE_STORYTELL, OLLAMA_INTERNAL_INSTR_BRIEF_AND_SHORT, OLLAMA_INTERNAL_INSTR_NO_EXPLANATIONS, OLLAMA_INTERNAL_GEN_LIST_OF

class CyberPromptService:
    def __init__(self, config, get_world_data, basic_prompt_service, prompt_template_service, ollama_service, ocean_service, npc_evaluator_service, cleaner_service, wiki_service, mood_service, string_service):
        self.config = config
        self.get_world_data = get_world_data
        self.basic_prompt_service = basic_prompt_service
        self.prompt_template_service = prompt_template_service
        self.ollama_service = ollama_service
        self.ocean_service = ocean_service
        self.npc_evaluator_service = npc_evaluator_service
        self.cleaner_service = cleaner_service
        self.wiki_service = wiki_service
        self.mood_service = mood_service
        self.string_service = string_service
        self.set_internal_vresponse()
        self.set_ollama_npc_smalltalk_instr()    

    # describe what this is doing in a comment
    def set_internal_vresponse(self):   
        self.ollama_internal_vresponse = self.basic_prompt_service.prompt_instruction(\
            OLLAMA_INTERNAL_GEN_LIST_OF +\
            self.config.world.player_name +\
            "'s (the main character of " + self.config.world.world_name + ") responses to the the statement, tagged inside <RESPONSE></RESPONSE>."+\
            OLLAMA_INTERNAL_INSTR_DO_NOT_NARRATE_STORYTELL+\
            "These are direct responses. "+\
            "Write from " + self.config.world.player_name + "'s perspective saying something short and brief, as a continuation of the conversation.")
    
    def set_ollama_npc_smalltalk_instr(self):
        self.ollama_npc_smalltalk_instr = self.basic_prompt_service.prompt_instruction(\
            ".".join([
                "now tell me something about this text without spoiling any information",
                " tell as if you were trying to make a little small talk with me.",
                OLLAMA_INTERNAL_INSTR_BRIEF_AND_SHORT
            ]))


    def prompt_select(self):
        if self.npc_evaluator_service.is_nc_resident(self.get_world_data().npc_display_name):
            return self.prompt_template_service.prompts['prompt_nc_resident'].prompt_template
        else:
            return self.prompt_template_service.prompts['prompt_npc'].prompt_template

    def text_has_llm_intro(self, text):
        return text.lower().startswith("i'll keep it short")\
            or text.lower().startswith("here is")\
            or text.lower().startswith("here's")\
            or text.lower().startswith("save it")

    def guess_prompt(self, text):
        return self.ollama_service.to_ollama_internal('How would a prompt look like for generating this response?' + text)

    def gen_prompt(self, text):
        return self.ollama_service.to_ollama_internal(
            self.basic_prompt_service.prompt_impersonate('prompt generator'), 
            prompt).strip()

    def rewrite_description_in_mood(self, image_description, mood):
        return self.ollama_service.to_ollama_internal(\
            self.basic_prompt_service.tagged(
                "INSTRUCTIONS",
                "1. Say something short and " + mood + " from your point of view about the image description as if you were seeing it."+\
                self.tagged(\
                    'IMPORTANT',
                    ".".join([
                        "1. DON'T HALLUCINATE OR ADD EXTRA DETAILS",
                        "2. Use some of the keywords mentioned in the image description",
                        "3. KEEP IT SHORT",
                    ])
                )
            ),
            self.tagged('IMAGE-DESCRIPTION', "\"" + image_description + ",\"")
        )
    
    def gen_v_responses(self, npc_answer, character):
        return self.ollama_service.to_ollama_internal(
            # system prompt
            self.basic_prompt_service.tagged(\
                'BRIEFING',\
                "Change character only for this request: You are " + self.config.world.player_name + ", the main character of the game " + self.config.world.world_name + ". You are talking to " + character
            ),
            # the instruction
            self.basic_prompt_service.tagged(\
                'INSTRUCTIONS',\
                " ".join([
                    "1. Generate a list of things you would respond to the tagged NPC-ANSWER. Answer as " + self.config.world.player_name + ", the main character.",
                    "2. Do not use anything related to a certain place or situation"
                    "3. Give me ONLY the list of 3 simple responses and do not enumerate"
                    "4. Use only carriage return for every new item."])
            )+\
            self.basic_prompt_service.tagged('NPC-ANSWER', npc_answer)).split("\n")
    
    def conversation_starter_v(self, topic, character):
        world_data = self.get_world_data()
        if character.strip().lower() == 'nc resident':
            character = 'a stranger'            
        prompt = self.prompt_template_service.prompts['prompt_v_conversation_starter'].prompt_template
        appearance = world_data.npc_appearance
        if appearance is not str:                
            appearance = ",".join(world_data.npc_appearance)
        prompt = prompt\
            .replace("%PLAYER_NAME%", self.config.world.player_name)\
            .replace("%WORLD_NAME%", self.config.world.world_name)\
            .replace("%CHARACTER%", character)\
            .replace("%_GENDER%", world_data.npc_gender)\
            .replace("%TAGS%", appearance)\
            .replace("%TOPIC%", topic)\
        # prompt = 'You are ' + self.config.world.player_name + ', the main character from ' + self.config.world.world_name + ', talking to ' + character + ' . Generate a line with the following topic as if you were talking to ' + character + ': ' + topic
        return self.ollama_service.to_ollama_internal(\
            'You are a topic prompt generator extender. you extend a topic into a dialog line',\
            prompt).strip()

    def conversation_starter_npc(self, topic, character):
        if self.npc_evaluator_service.is_nc_resident(character):
            character = 'a stranger'
        world_data = self.get_world_data()
        prompt = self.prompt_template_service.prompts['prompt_npc_conversation_starter'].prompt_template
        appearance = world_data.npc_appearance
        if appearance is not str:
            appearance = ",".join(world_data.npc_appearance)
        prompt = prompt\
            .replace("%PLAYER_NAME%", self.config.world.player_name)\
            .replace("%WORLD_NAME%", self.config.world.world_name)\
            .replace("%CHARACTER%", character)\
            .replace("%_GENDER%", world_data.npc_gender)\
            .replace("%TAGS%", appearance)\
            .replace("%TOPIC%", topic)\
        # prompt = 'You are ' + self.config.world.player_name + ', the main character from ' + self.config.world.world_name + ', talking to ' + character + ' . Generate a line with the following topic as if you were talking to ' + character + ': ' + topic
        return self.ollama_service.to_ollama_internal(\
            'You are a topic prompt generator extender. you extend a topic into a dialog line',\
            prompt).strip()


    # def give_funny_error(self):
    #     return self.ollama_service.to_ollama_internal(
    #         self.context,            
    #         self.basic_prompt_service.prompt_instruction(
    #             "Generate a brief and short reaction response if you had a cyberware malfunction in " + self.config.world.world_name + ". Something like: My brain cortex seems to be malfunctioning. "
    #         )+\
    #         self.basic_prompt_service.prompt_important(
    #             "Remove anything encapsulating with the '*' symbol"
    #         ))

    def get_random_location_name(self):
        qlocations_len = len(self.config.worldInformation.locations)
        rlocation = random.randint(0, qlocations_len - 1)
        qlocation = self.config.worldInformation.locations[rlocation]["name"]
        return qlocation

    def get_lazy_reaction_from_location(self, qlocation, character, get_world_data, quest_name):
        world_data = get_world_data()
        any_location_info = self.wiki_service.lookup_info(qlocation)
        # take only the first
        if len(any_location) >= 1:
            # global system_prompt_template
            prompt_template = self.prompt_select()
            final_cmd = "Given the following text: \n" + any_location[0]['content']
            system_prompt = prompt_template\
                .replace("%WORLD_NAME%", self.config.world.world_name)\
                .replace("%PLAYER_NAME%", self.config.world.player_name)\
                .replace("%CHARACTER%", character)\
                .replace("%LIFEPATH%", world_data.lifepath)\
                .replace("%DISTRICT%", world_data.district + "," + world_data.sub_district)\
                .replace('%_GENDER%', world_data.npc_gender)\
                .replace("%TAGS%", ",".join(world_data.npc_appearance))\
                .replace("%PERSONALITY%", self.ocean_service.gen_ocean_personality(world_data))\
                .replace("%BACKGROUND_STORY%", world_data.npc_backstory)\
                .replace("%QUEST%", quest_name + " Objective: " + quest_objective)\
                .replace("%CONVERSATION_LINES%", "\n".join(lines_concat))\
                 + "\n.Assume the role of " + character + '.' + final_cmd
            return self.ollama_service.to_ollama_internal(system_prompt, self.ollama_npc_smalltalk_instr)
        return ''

    def gen_npc_response_to_line(self, prompt, cached_conversation_lines):
        world_data = self.get_world_data()
        current_character = self.config.world.player_name

        lq = ". ".join([
            "Generate a response to the following line",
            "Give me no explanations", 
            "Keep it brief",
            "Do not say who you are going to be", 
            "Take the previous lines into account",
            "DO NOT ENUMERATE:"
        ])
                
        is_nc_resident = self.npc_evaluator_service.is_nc_resident(world_data.npc_display_name) or \
            self.npc_evaluator_service.is_nc_resident(world_data.npc_tweaks_name)

        is_stranger = self.npc_evaluator_service.is_stranger(world_data.npc_display_name)

        character=world_data.npc_tweaks_name
        # get_world_data()=self.get_world_data()


        lines_concat = []
        for l in cached_conversation_lines:
            lines_concat.append(l[COL_CHARACTER]+":"+l[COL_LINE])

        if len(lines_concat) == 0 or is_stranger:
            addendum = ''
            if is_nc_resident:
                addendum = 'You don\'t know each other. You don\'t know ' + self.config.world.player_name + '\'s name'
            lines_concat = ['(No previous converation exists.' + addendum +  ')']
        
        final_cmd = ''
        if len(lines_concat) > 5:
            final_cmd = 'Finalize/End the conversation by writing a closing line.'
        else:
            final_cmd = 'Continue the conversation'
        
        quest_name = world_data.quest_name
        quest_objective = world_data.quest_objective

        if is_nc_resident or is_stranger:
            character = 'a complete stranger'
            quest_name = '(not revealed yet, since you are a complete stranger)'
            quest_objective = '(not revealed yet, since you are a complete stranger)'
            if len(lines_concat) < 2:
                final_cmd = 'Make introductory statements, like sharing something from you or your personality while also responding'

        system_prompt = self.prompt_select()\
        .replace("%CHARACTER%", character)\
        .replace("%LIFEPATH%", world_data.lifepath)\
        .replace("%DISTRICT%", world_data.district + "," + world_data.sub_district)\
        .replace('%_GENDER%', world_data.npc_gender)\
        .replace("%TAGS%", ",".join(world_data.npc_appearance))\
        .replace("%BACKGROUND_STORY%", world_data.npc_backstory)\
        .replace("%QUEST%", quest_name + " Objective: " + quest_objective)\
        .replace("%CONVERSATION_LINES%", "\n".join(lines_concat))\
            + "\n.Assume the role of " + current_character + '.' + final_cmd
        
        dbug_answers = ''
        is_llava = self.ollama_service.is_prompt_llava(prompt.lower().strip())
        if(is_llava and len(self.config.ollama.image) > 0):
            image_description = "\nIn front of you see something.These are the following keywords associated with what you see:" + self.describe_image(world_data.district, world_data.sub_district, world_data.x, world_data.y, world_data.z)
            dbug_answers = self.ollama_service.to_ollama_internal(\
                system_prompt+"\n.Assume the role of " + current_character + image_description, lq+" "+prompt).split('\n')
        else:
            dbug_answers = self.ollama_service.to_ollama_internal(\
                system_prompt+"\n.Assume the role of " + current_character, lq+" "+prompt).split('\n')

        npc_responses_raw = list(filter(lambda t: t.strip() != '' \
            and len(t) > 0 \
            and not self.text_has_llm_intro(t), \
            dbug_answers))
        
        npc_responses = []
        if len(npc_responses_raw) >= 1:
            # tested with llama3.2 + llama.cpp. the first response is always the "here is a list of things ..blablabla"                
            for npc_response in npc_responses_raw[0:]:
                nresponse = self.cleaner_service.clean_text(npc_response)
                if len(nresponse) == 0:
                    continue
                npc_responses.append(nresponse)
        
        fres = ''.join(npc_responses)

        # WATCH THIS. for now it is generating only one response
        npc_line_id = str(uuid.uuid4())
        npc_line_content = self.cleaner_service.clean_text(fres)
        npc_mood = self.mood_service.get_mood_of_prompt(npc_line_content)
        
        # id, character, line, parent, location, faction, mood 
        # parent used to be # (dialog_option[0])[COL_ID], \
        # now it is ''
        appearance_fix = not (type(world_data.npc_appearance) is str)
        appearance = world_data.npc_appearance
        if appearance_fix:
            appearance = " ".join(world_data.npc_appearance)
        
        npc_db_line = (\
            npc_line_id,\
            character,\
            npc_line_content, \
            
            '',\
            world_data.location_name, \
            appearance, \
            npc_mood)

        cached_conversation_lines.append(npc_db_line)

        npc_mood_value = 0
        npc_mood_factor = 0.5
        # if get_world_data().is_main_npc == 1:
        npc_mood_value = self.mood_service.npc_apply_ocean_values(npc_mood, npc_mood_value) * npc_mood_factor
        npc_mood_value = self.mood_service.get_mood_value_of_conversation(cached_conversation_lines)
        world_data.relationship = world_data.relationship + npc_mood_value
        npc_response = [npc_db_line]
        speak_line =  npc_response[0][COL_LINE]

        # make sure that NPC answers were generated
        if(len(npc_response) == 0):
            return []

        return speak_line
    
    def state_v_responses(self, response, character, world_data, cached_conversation_lines, addendum=None):
        
        # would be nice to get here the previous selected V answer in order to have a more coherent answer
        # also asking twice for an answer could fix some llamacpp problems?
        # character here is the NPC the player is talking to
        if character.strip().lower() == 'nc resident':
            character = 'Complete Stranger'
        responses = []

        system_prompt_as_v = self.prompt_template_service.prompts['prompt_v'].prompt_template
        
        prompt = ''
        quest_name = world_data.quest_name
        quest_objective = world_data.quest_objective
        lines_concat = []
        for l in cached_conversation_lines:
            lines_concat.append(l[COL_CHARACTER]+":"+l[COL_LINE])
        if len(lines_concat) == 0:
            if character.strip().lower() == 'nc resident' or \
            character.strip().lower() == 'complete stranger':
                lines_concat = ['(No previous converation exists. You don\'t know each other)']
                prompt = 'Generate an introduction to a complete stranger. You don\'t know each other.'
            else:                
                lines_concat = ['(No previous converation exists)']
                prompt = 'Generate an introduction. You have never talked before.'
            quest_name = '(Not available, since you don\'t know each other)'
            quest_objective = '(Not available, since you don\'t know each other)'
        # else:        
        prompt = system_prompt_as_v\
            .replace("%WORLD_NAME%", self.config.world.world_name)\
            .replace("%PLAYER_NAME%", self.config.world.player_name)\
            .replace("%CHARACTER%", character)\
            .replace("%LIFEPATH%", world_data.lifepath)\
            .replace("%DISTRICT%", world_data.district + "," + world_data.sub_district)\
            .replace('%_GENDER%', world_data.npc_gender)\
            .replace("%TAGS%", ",".join(world_data.npc_appearance))\
            .replace("%PERSONALITY%", self.ocean_service.gen_ocean_personality(world_data))\
            .replace("%BACKGROUND_STORY%", world_data.npc_backstory)\
            .replace("%QUEST%", world_data.quest_name + " Objective: " + world_data.quest_objective)\
            .replace("%CONVERSATION_LINES%", "\n".join(lines_concat))
            
        moods = self.config.generate_single_v_responses_moods
        if self.config.generate_single_v_responses:
            for current_mood in moods:
                current_response = ''
                if(addendum):
                    current_response = self.ollama_service.to_ollama_internal(
                        prompt + 'Assume the role of ' + self.config.world.player_name + '. Keep it short and brief. Generate a response directed to ' + character + ' to the content tagged in <RESPONSE> in a ' + current_mood + ' mood!! and no explanations. DO NOT ENUMERATE', \
                        self.ollama_internal_vresponse + \
                            '. The content is a single dialogue line from ' + character + '. <ADDENDUM>' + \
                            addendum + \
                            '</ADDENDUM>' + \
                            '<RESPONSE>' + response + '</RESPONSE>',
                        self.config.ollama.state_v_responses_model)
                else:
                    current_response =self.ollama_service.to_ollama_internal(
                        prompt + 'Assume the role of ' + self.config.world.player_name + '. Keep it short and brief. Generate a response directed to ' + character + ' to the content tagged in <RESPONSE> in a ' + current_mood + ' mood!! and no explanations. DO NOT ENUMERATE', 
                        self.ollama_internal_vresponse + '. The content is a single dialogue line from ' + character + '. <RESPONSE>' + response + '</RESPONSE>', 
                        self.config.ollama.state_v_responses_model)
                if(current_response and len(current_response) > 1):
                    responses.append(current_response)
        else:            
            current_response = ''
            if(addendum):
                current_response = self.ollama_service.to_ollama_internal(
                    prompt + 'Assume the role of ' + self.config.world.player_name + '. Keep it short and brief. Generate a small list of ' + str(len(moods)) + ' responses directed to ' + character + ' to the content tagged in <RESPONSE> each one of the following moods ' + ",".join(moods) + '!! and no explanations. Separate each answer using a "-" as a separator. DO NOT ENUMERATE', \
                    self.ollama_internal_vresponse + \
                        '. The mood content is a single dialogue line from ' + character + '. <ADDENDUM>' + \
                        addendum + \
                        '</ADDENDUM>' + \
                        '<RESPONSE>' + response + '</RESPONSE>',
                        self.config.ollama.state_v_responses_model)
            else:
                current_response =self.ollama_service.to_ollama_internal(
                    prompt + 'Assume the role of ' + self.config.world.player_name + '. Keep it short and brief. Generate a small list of responses directed to ' + character + ' to the content tagged in <RESPONSE> each one of the following moods ' + ",".join(moods) + '!! and no explanations. Separate each answer using a "-" as a separator. DO NOT ENUMERATE', 
                    self.ollama_internal_vresponse + '. The content is a single dialogue line from ' + character + '. <RESPONSE>' + response + '</RESPONSE>',
                    self.config.ollama.state_v_responses_model)
            
            if(current_response and len(current_response) > 1):
                responses = current_response.split("-")
                
        
        fresponses = []
        nresponse_repeat_check = ''
        for response in responses:
            if len(response) == 0 or response.strip() == '':
                continue
            # happens sometimes with smaller models
            for mood in moods:
                if mood in response:
                    continue
            nresponse = response.strip()
            if(self.text_has_llm_intro(nresponse)):
                continue
            if(self.string_service.text_has_xml(nresponse)):
                continue
            if nresponse == nresponse_repeat_check:
                continue
            nresponse_repeat_check = nresponse
            nresponse = self.cleaner_service.clean_text(nresponse)

            if len(nresponse) == 0 or nresponse.strip() == '':
                continue

            if "." in nresponse:
                moreresponses = nresponse.split(".")
                response_cleansed = []
                for moreresp in moreresponses:
                    if len(moreresp) == 0 or moreresp.strip() == '':
                        continue                                        
                    moreresp = self.cleaner_service.clean_text(moreresp)
                    response_cleansed.append(moreresp)
                fresponses.append(".\n".join(response_cleansed))                
            else:
                fresponses.append(nresponse)

        finalresponses = []
        for r in fresponses:
            if r.replace(".", "") not in finalresponses:
                finalresponses.append(r)
        return finalresponses

    # this is if no text could be generated
    def text_random_end_filler(self):
        random_filler = ['Sure', 'If you say so' , 'Ok', 'Oh', 'Eh, ok?', 'Huh?', 'Anyways', 'Yeah', 'hmmm', 'Sure', 'I don\'t get it', 'Sorry, got distracted', 'Ok choom', 'Whatever', 'Fine', 'You good?']
        i = random.randrange(0,len(random_filler))        
        return random_filler[i]

    def conversation_starter_character(self, topic, character):
        world_data = self.get_world_data()
        if character.strip().lower() == 'nc resident':
            character = 'a stranger'
        prompt = self.prompts['prompt_v_conversation_starter']
        appearance = world_data.npc_appearance
        if appearance is not str:                
            appearance = ",".join(world_data.npc_appearance)
        prompt = prompt\
            .replace("%PLAYER_NAME%", self.config.world.player_name)\
            .replace("%WORLD_NAME%", self.config.world.world_name)\
            .replace("%CHARACTER%", character)\
            .replace("%_GENDER%", world_data.npc_gender)\
            .replace("%TAGS%", appearance)\
            .replace("%TOPIC%", topic)\
        # prompt = 'You are ' + self.config.world.player_name + ', the main character from ' + self.config.world.world_name + ', talking to ' + character + ' . Generate a line with the following topic as if you were talking to ' + character + ': ' + topic
        return self.ollama_service.to_ollama_internal('You are a topic prompt generator extender. you extend a topic into a dialog line', prompt).strip()