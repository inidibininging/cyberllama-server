import logging
import random
from projects.cyberpunk.services.sqlite3_cache_service import COL_ID, COL_CHARACTER, COL_LINE, COL_PARENT, COL_LOCATION, COL_FACTION, COL_MOOD

OLLAMA_INTERNAL_SENTIMENT_PROMPT = "Analyze the sentiment from -1 for negative 0 for neutral and 1 for positive for the following prompt. Do not explain further, give only the mood value:"

class MoodService:
    def __init__(self, config, ollama_service, character_overrides_service, ocean_expr_map, get_world_data):
        self.config = config
        self.ollama_service = ollama_service        
        self.character_overrides_service = character_overrides_service
        self.ocean_expr_map = ocean_expr_map
        self.get_world_data = get_world_data

    def get_random_mood(self):
        mood_choice = random.randrange(0, 100)
        mood = 'neutral'
        if mood_choice < 80:
            mood = 'funny'
        elif mood_choice < 60:
            mood = 'sarcastic'
        elif mood_choice < 40:
            mood = 'cynical'
        elif mood_choice < 20:
            mood = 'depressing'
        return mood
    
    # used for getting the mood of a line by mapping certain words as +1, 0 or -1    
    def hard_coded_get_mood_value(self, mood):
        sentiment_scores = {
            "Smile": 1,
            "Joy": 1,
            "Interested": 1,
            "Interest": 1,
            "Amused": 1,
            "Surprise": 1,
            "Confident": 1,
            "Challenge": 0,
            "Curious": 1,    
            "Neutral": 0,
            "Desire": 0,
            "Nervous": -1,
            "Sadness": -1,
            "Disappointed": -1,
            "Exertion": -1,
            "Sad": -1,
            "Pain": -1,
            "Relief": 0,
            "Disinterested": 0,
            "Confused": 0,
            "Agitated": -1,
            "Discomfort": -1,
            "Defiance": -1,
            "Amusement": 1,
            "Concern": 1,
            "Deception": -1,
            "Agreement": 0,
            "Interest/Confidence": 1,
            "Joy/Flirtation": 1,
            "Joy/Amusement": 1,
            "Joy/Compliment": 1,
            "Aggressive/Jauntiness": -1,
            "Aggressive/Flirtation": -1,
            "Interested/Flirtation": 1,
            "Surprise/Interst": 1,
            "Joy/Interest": 1,
            "Confidence/Assertiveness": 1,
            "Confidence/Challenge": 0,
            "Aggressive/Defensive": -1,
            "Anger/Defiance": -1
        }
        if mood in sentiment_scores:
            return sentiment_scores[mood]
        else:
            return 0

    def get_mood_of_prompt(self, prompt):
        moods = [ \
            "Neutral",\
            "Joy",\
            "Smile",\
            "Sad",\
            "Surprise",\
            "Aggressive",\
            "Anger",\
            "Interested",\
            "Disinterested",\
            "Disappointed",\
            "Disgust",\
            "Exertion",\
            "Nervous",\
            "Fear",\
            "Terrified",\
            "Pain",\
            "Sleepy",\
            "Unconscious",\
            "Dead",\
        ]
        q = "Analyze the sentiment of the prompt and return only one value from the following list(" + ",".join(moods) + "). Do not explain further and do not concatenate any values. Here is the prompt:"
        return self.ollama_service.to_ollama_internal(q, prompt, self.config.ollama.mood_eval_model)

    def get_mood_value_of_prompt(self, prompt):        
        ''' tries to get the sentiment value of a prompt by using ollama '''
        response = self.ollama_service.to_ollama_internal(OLLAMA_INTERNAL_SENTIMENT_PROMPT, prompt, self.config.ollama.mood_eval_model)
        return response
    
    def get_mood_value_of_conversation(self, conversation):
        ''' tries to get the sentiment value of a prompt by using ollama '''
        conversation_lines = "\n".join(list(map(lambda l: l[COL_CHARACTER]+":"+l[COL_LINE], conversation)))
        response = self.ollama_service.to_ollama_internal("""
        Analyze the sentiment as a floating point value.
        use the following range:
        0 (for negative)
        1 (for positive) 
        
        for the following conversation so far.
        Take more into account the last part of the conversation.
        Do not explain further, give only the mood value as a floating point value
        """, 
        conversation_lines,
        self.config.ollama.mood_eval_model)
        final_response = ''
        for c in response:
            if c in ['0', '1', '2', '3', '4', '5', '6', '7', '8','9', '.', '-']:
                final_response = final_response + c
        final_response = 0
        try:
            final_response = round(float(response))
        except Exception as e:
            logging.error(f"An error occurred during speech playback: {str(e)}")

        if final_response >= 1:
            return 10
        if final_response <= 0:
            return -10
        
        # final_response = final_response - 0.5
        # somehow the answers are more positive or more negatice depending on the model and prompt
        # lets balance this out by making it weigh more
        if final_response < 0:
            final_response = final_response 
        else:
            final_response = final_response
        return final_response * 10
    
    def npc_get_voice_mood(self, mood):
        moodl = mood.lower()
        for name in self.character_overrides_service.npc_overrides:
            if not self.character_overrides_service.npc_override_matches(self.character_overrides_service.npc_overrides[name]):
                continue
            emotions = [
                "joy",
                "smile",
                "neutral",
                "smile",
                "sad",
                "surprise",
                "aggressive",
                "anger",
                "interested",
                "disinterested",
                "disappointed",
                "disgust",
                "exertion",
                "nervous",
                "fear",
                "terrified",
                "pain",
                "sleepy",
                "unconscious",
                "dead",
            ]
            if not moodl in emotions:
                continue

            return getattr(npc_override, "npc_" + emotion)

    def npc_apply_ocean_values(self, mood, mood_value):
        mood_value_2=mood_value
        world_data = self.get_world_data()
        for emotion in self.ocean_expr_map.emotions:
            if emotion['emotion'] != mood:
                continue
            if emotion['ocean_traits'] == None:
                # mood_value_2=0
                continue
                        
            for ptrait in emotion['ocean_traits']:                
                pvalue = getattr(world_data, ptrait.lower())
                mood_value_2 = mood_value_2 + pvalue
        return mood_value_2