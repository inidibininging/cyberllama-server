from projects.all.services.basic_prompt_service import OLLAMA_INTERNAL_INSTR_BEGIN, OLLAMA_INTERNAL_INSTR_END

class CleanerService:
    def __init__(self, string_service, cyber_replacer_service):
        self.string_service = string_service
        self.cyber_replacer_service = cyber_replacer_service

    def get_clean_prompt(self, text):
        cleaned_t = ''
        if text == None:
            return ''
        for character in text:
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

    def clean_text(self, text, use_limit=True):
        cleaned_t = ''
        if text == None:
            return cleaned_t
        last_char = ''
        text = self.clean_llamacpp_output(text, useLimit=use_limit)
        text = text.strip()
        # pls dont hate me for this. i know regex is a wonderful and horrible invention        
        if '<' in text or '>' in text:
            text = self.string_service.trim_html_tags(text)
        if '(' in text or ')' in text:
            text = self.string_service.trim_parentheses(text)
        if '*' in text:
            text = self.string_service.trim_marked(text)

        text = self.string_service.collapse_trailing_dots(text)
        for character in text:
            if character.isalnum() \
                or character == '.' \
                or character == ',' \
                or character == ';' \
                or character == "'" \
                or character == '!' \
                or character == ' ' \
                or character == '\n' \
                or character == '?':
                cleaned_t += character

        # for the response part : leveshstein instead of capturing every response
        cleaned_t = cleaned_t.replace('*', '')\
                .replace("\n", " ")\
                .replace("I'll", "I will")\
                .replace("I'd", "I would")\
                .replace("I've", "I have")\
                .replace("I'm", "I am")\
                .replace("It's", "It is")\
                .replace("Youll", "You will")\
                .replace("Youd", "You would")\
                .replace("Youve", "You have")\
                .replace("Youre", "You are")\
                .replace("You'll", "You will")\
                .replace("You'd", "You would")\
                .replace("You've", "You have")\
                .replace("You're", "You are")\
                .replace("He'll", "He will")\
                .replace("He'd", "He would")\
                .replace("He's", "He is")\
                .replace("She'll", "She will")\
                .replace("She'd", "She would")\
                .replace("She's", "She is")\
                .replace("They'll", "They will")\
                .replace("They'd", "They would")\
                .replace("They're", "They are")\
                .replace("What's your angle", self.cyber_replacer_service.whats_your_angle_line())\
                .replace("What's the angle", self.cyber_replacer_service.whats_your_angle_line())\
                .replace("What is your angle", self.cyber_replacer_service.whats_your_angle_line())\
                .replace("What is the angle", self.cyber_replacer_service.whats_your_angle_line())\
                .replace("Whats your angle", self.cyber_replacer_service.whats_your_angle_line())\
                .replace("Whats the angle", self.cyber_replacer_service.whats_your_angle_line())\
                .replace("What's", "What is")\
                .replace(" dont", " do not")\
                .replace("it's", "it is")\
                .replace("'s", "s")\
                .replace("'", "")\
                .replace("Are you kidding", self.cyber_replacer_service.are_you_kidding_line_replace_line())\
                .replace("Save your breath", self.cyber_replacer_service.save_your_breath_line())\
                .replace("save your breath", self.cyber_replacer_service.save_your_breath_line())\
                .replace("Kid", "Choom")\
                .replace("kid", "choom")\
                .replace("|", "")\
                .replace("resPONSE", "")\
                .replace("reSPONSE", "")\
                .replace("rESPONSE", "")\
                .replace("RESPONSE", "")\
                .replace("RESPONCE", "")\
                .replace("RESPONS", "")\
                .replace("RESPOSE", "")\
                .replace("RESPOONSE", "")\
                .replace("REPOSE", "")\
                .replace("RESPTON", "")\
                .replace("repose", "")\
                .replace("Response", "")\
                .replace(" b ", "")\
                .replace("http", "")\
                .replace("youtube", "")\
                .replace("cyberpunkcharacterresponse", "")\
                .replace("Keanu", "Johny")\
                .replace("keanu", "johny")\
                .replace("nuyen", "eddies")\
                .replace("INSTRUCTION", "")\
                .replace("TAGGED", "")\
                .replace("TAG", "")\
                .replace("HTML", "")\
                .replace("html", "")\
                .replace("brBR", "")\
                .replace(" chum", "choom")\
                .replace("RESONANCE", "")\
                .replace(" sighs ", " huh, choom ")\
                .replace(" sigh ", "huh")\
                .replace("Spare me the theatrics", self.cyber_replacer_service.spare_me_line_replace_line())\
                .replace("spare me the theatrics", self.cyber_replacer_service.spare_me_line_replace_line())\
                .replace("sweetheart", self.cyber_replacer_service.sweetheart_replace_line())
        
        cleaned_t = cleaned_t.strip()
        cleaned_t = self.string_service.remove_at_start(cleaned_t, "sigh")
        cleaned_t = self.string_service.remove_at_start(cleaned_t, "sarcastic")
        cleaned_t = self.string_service.remove_at_start(cleaned_t, "shrugs")
        cleaned_t = cleaned_t.strip()
        
        if cleaned_t.startswith("i") and cleaned_t.endswith("i"):
            cleaned_t = self.string_service.remove_at_start(cleaned_t, "i")
            cleaned_t = self.string_service.remove_at_end(cleaned_t, "i")
        return cleaned_t

    def clean_llamacpp_output(self, response, useLimit=True):
        # covers rough split up stuff and things like  "no", "oh" etc
        # with a regex over words => we can minimize by providing the length of the shortest sentence ... dunno (3 words?)
        if (len(response) < 2 or len(response) > 350) and useLimit:
            return ''
        nresponse = response.strip()
        lowered = nresponse.lower()
        if(lowered.startswith("i'll keep it short")\
            or lowered.startswith("here's the list")\
            or lowered.startswith("here is the list")):
            return ''
        nresponse = self.string_service.remove_at_start(nresponse, '1.')
        nresponse = self.string_service.remove_at_start(nresponse, '2.')
        nresponse = self.string_service.remove_at_start(nresponse, '3.')
        nresponse = self.string_service.remove_at_start(nresponse, '4.')
        nresponse = self.string_service.remove_at_start(nresponse, '5.')
        nresponse = self.string_service.remove_at_start(nresponse, '6.')
        nresponse = self.string_service.remove_at_start(nresponse, '7.')
        nresponse = self.string_service.remove_at_start(nresponse, '8.')
        nresponse = self.string_service.remove_at_start(nresponse, '9.')
        nresponse = self.string_service.remove_at_start(nresponse, '10.')
        nresponse = self.string_service.remove_at_start(nresponse, '<RESPONSE>')
        nresponse = self.string_service.remove_at_start(nresponse, '</RESPONSE>')
        nresponse = self.string_service.remove_at_start(nresponse, 'RESPONSE')
        nresponse = self.string_service.remove_at_start(nresponse, OLLAMA_INTERNAL_INSTR_BEGIN)
        nresponse = self.string_service.remove_at_start(nresponse, OLLAMA_INTERNAL_INSTR_END)
        nresponse = self.string_service.remove_at_start(nresponse, 'response')        
        nresponse = self.string_service.remove_at_start(nresponse, 'V')
        nresponse = self.string_service.remove_at_start(nresponse, 'Vs response')
        nresponse = self.string_service.remove_at_start(nresponse, 'V\'s response')
        nresponse = self.string_service.remove_at_start(nresponse, 'V\'s Response')
        nresponse = self.string_service.remove_at_start(nresponse, 'V\'s RESPONSE')
        nresponse = self.string_service.remove_at_start(nresponse, 'Vs')
        nresponse = self.string_service.remove_at_start(nresponse, 'V\'s')
        nresponse = self.string_service.remove_at_start(nresponse, 'Vincent\'s')
        nresponse = self.string_service.remove_at_start(nresponse, 'VINCENT\'s')
        nresponse = self.string_service.remove_at_start(nresponse, 'V.')
        nresponse = self.string_service.remove_at_start(nresponse, 'V:')
        nresponse = self.string_service.remove_at_start(nresponse, 'REPLY')
        nresponse = self.string_service.remove_at_start(nresponse, 'span')
        nresponse = self.string_service.remove_at_start(nresponse, 'spanV')
        nresponse = self.string_service.remove_at_start(nresponse, 'spanVspan')
        nresponse = self.string_service.remove_at_start(nresponse, 'spanVspan')
        nresponse = self.string_service.remove_at_start(nresponse, 'INSTRUCTION')             
        nresponse = self.string_service.remove_at_start(nresponse, '|')

        return nresponse

