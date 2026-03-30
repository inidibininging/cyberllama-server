class IntentionService:
    def __init__(self, keyword_service, mentions_service):
        self.keyword_service = keyword_service
        self.mentions_service = mentions_service
        
    def is_drink_intention(self, text):
        return self.keyword_service.keyword_matches_text(text, self.keyword_service.keywords['drink_intention'])
    
    def is_eat_intention(self, text):
        return self.keyword_service.keyword_matches_text(text, self.keyword_service.keywords['eat_intention'])

    def is_kill_intention(self, text):
        return self.keyword_service.keyword_matches_text(text, self.keyword_service.keywords['kill_intention'])

    def mentions_district(self, text):
        return self.keyword_service.keyword_matches_text(text, self.keyword_service.keywords['districts'])        

    def mentions_location(self, text):
        return self.keyword_service.keyword_matches_text(text, self.keyword_service.keywords['locations'])

    def mentions_faction(self, text):
        return self.keyword_service.keyword_in_text(text, self.keyword_service.keywords['factions'])

    def mentions_company(self, text):
        return self.keyword_service.keyword_in_text(text, self.keyword_service.keywords['companies'])

    def is_move_intention(self, text):
        return self.keyword_service.keyword_in_text(text, self.keyword_service.keywords['move_intention'])
    
    def is_hold_intention(self, text):
        return self.keyword_service.keyword_in_text(text, self.keyword_service.keywords['hold_intention'])

    def is_follow_intention(self, text):
        return self.keyword_service.keyword_in_text(text, self.keyword_service.keywords['follow_intention'])

    def is_get_intention(self, text):
        return self.keyword_service.keyword_in_text(text, self.keyword_service.keywords['get_intention'])

    def is_hide_intention(self, text):
        return self.keyword_service.keyword_in_text(text, self.keyword_service.keywords['hide_intention'])
    
    def is_money_intention(self, text):
        return self.keyword_service.keyword_in_text(text, self.keyword_service.keywords['money_intention'])
    
    def is_quest_intention(self, text):
        return self.keyword_service.keyword_in_text(text, self.keyword_service.keywords['quest_intention'])

    def is_get_up_intention(self, text):
        # data = ['get up', 'stand up', 'get back up']
        # return self.is_maybe_keyword(text, data)
        return self.keyword_service.keyword_in_text(text, self.keyword_service.keywords['getup_intention'])
    
    
    def get_intentions(self, speak_line, character, npc_cache):
        # mentions 
        # 
        character_is_kill = self.is_kill_intention(speak_line)
        character_is_drink = self.is_drink_intention(speak_line)
        character_is_eat = self.is_eat_intention(speak_line)
        character_is_hide = self.is_hide_intention(speak_line)
        character_is_move = self.is_move_intention(speak_line)
        character_is_hold = self.is_hold_intention(speak_line)
        character_is_follow = self.is_follow_intention(speak_line)
        character_is_get = self.is_get_intention(speak_line)
        character_is_get_up = self.is_get_up_intention(speak_line)
        character_is_quest = self.is_quest_intention(speak_line)
        character_is_money = self.is_money_intention(speak_line)
        character_mentions_character = self.mentions_service.mentions_character(speak_line, npc_cache)
        character_mentions_faction = self.mentions_service.mentions_faction_in_text(speak_line)
        character_mentions_location = self.mentions_location(speak_line)
        character_mentions_district = self.mentions_district(speak_line)
        character_mentions_company = self.mentions_company(speak_line)
        # npc_is_goodbye = self.is_goodbye_intention(prompt)

        return {
            character + "_is_kill": str(character_is_kill),
            character + "_is_drink": str(character_is_drink),
            character + "_is_eat": str(character_is_eat),
            character + "_is_hide": str(character_is_hide),
            character + "_is_move": str(character_is_move),
            character + "_is_hold": str(character_is_hold),
            character + "_is_follow": str(character_is_follow),
            character + "_is_get": str(character_is_get),
            character + "_is_get_up": str(character_is_get_up),
            character + "_is_quest" : str(character_is_quest),
            character + "_is_money" : str(character_is_money),
            character + "_mentions_character": str(character_mentions_character),
            character + "_mentions_faction" : str(character_mentions_faction),
            character + "_mentions_location" : str(character_mentions_location),
            character + "_mentions_district" : str(character_mentions_district),
            character + "_mentions_company" : str(character_mentions_company),
        }