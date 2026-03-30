import os
import yaml
import random
import logging

class KeywordsService:
    def __init__(self, project_name):
        self.project_name = project_name
    
    def init_keywords(self):
        logging.info("Initializing keywords")
        wiki = {}
        keyword_files = os.listdir(os.getcwd()+"/projects/"+ self.project_name + "/keywords")
        for wiki_file in keyword_files:
            wiki_file_path = os.getcwd()+"/projects/"+ self.project_name + "/keywords/" + wiki_file
            with open(wiki_file_path, encoding='utf-8') as data:
                wiki[os.path.basename(wiki_file_path).replace(".yaml", "")] = yaml.safe_load(data)["data"]
        return wiki

    def keyword_matches_text(self, text, keywords):
        text_low = text.lower()
        for keyword in keywords:
            if text_low in keyword.lower():
                return True
        return False

    def keyword_in_text(self, text, keywords):
        text_low = text.lower()
        for keyword in keywords:
            if keyword.lower() in text_low:
                return True
        return False
    
    def matches_keyword(self, text, container_name):
        text_low = text.lower()
        kcontainer = self.keywords[container_name]
        for intention in kcontainer:
            if text_low in intention.lower():
                return True
        return False

    
    def keywords_get_random(self, keyword, count):
        bucket = []
        keywords = len(self.keywords[keyword])
        keyword_index = count
        if keywords == 0:
            return bucket
        while keyword_index > 0:
            i = random.randrange(0, keywords - 1)
            next = self.keywords[keyword][i]
            if next in bucket:
                continue
            keyword_index = keyword_index - 1
            bucket.append(next)
        return bucket
    
    def matches_exact_keyword(self, text, keywords):
        text_low = text.lower()
        for keyword in keywords:
            if keyword.lower() == text_low:
                return True
        return False