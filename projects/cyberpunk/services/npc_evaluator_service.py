class NpcEvaluatorService:
    def is_nc_resident(self, character):
        return character.lower().strip() == 'nc resident'

    def is_stranger(self, character):
        return character.lower().strip() in \
            ['customer'
            'patron'
            'bar patron puppet'
            'club patron'
            'female club patron'
            'npcpuppet'
            'puppet'
            'npc puppet']