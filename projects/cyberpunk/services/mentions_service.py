class MentionsService:
    def __init__(self, keyword_service):
        self.keyword_service = keyword_service

    def mentions_faction_in_text(self, text):
        
        if self.keyword_service.keyword_matches_text(text, self.keyword_service.keywords['gangs']):
            return True
        if self.keyword_service.keyword_matches_text(text, self.keyword_service.keywords['corporations']):
            return True
        text_low = text.lower().strip()
        for gang in self.keyword_service.keywords['gangs']:
            if gang.lower().strip() in text_low:
                return True
        for gang in self.keyword_service.keywords['corporations']:
            if gang.lower().strip() in text_low:
                return True
        return False
    

    def mentions_character(self, text, npc_cache):       
        return self.keyword_service.keyword_matches_text(text, self.keyword_service.keywords['characters']) or \
             self.keyword_service.keyword_matches_text (text, list(filter(lambda npc: text in npc_cache[npc]['npc_display_name'].lower(), npc_cache)))
    