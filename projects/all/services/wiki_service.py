import os
import yaml
import logging

class WikiService:
    def __init__(self, project_name):
        self.project_name = project_name
    
    def load_wiki(self):
        wiki_files = os.listdir(os.getcwd()+"/projects/"+self.project_name+"/wiki")
        self.wiki = []
        for wf in wiki_files:
            print(wf)
            with open(os.getcwd()+"/projects/"+self.project_name+"/wiki/"+wf, 'r', encoding='utf-8') as wfc:
                self.wiki.append({
                    "file" : wf,
                    "content": wfc.read()
                })

    def rephrase_wiki(self):
        wiki_files = os.listdir(os.getcwd()+"/projects/"+self.project_name+"/wiki")
        self.wiki = []
        for wf in wiki_files:
            wf_path = os.getcwd()+"/projects/"+self.project_name+"/wiki/"+wf
            with open(wf_path, 'r', encoding='utf-8') as wfc:
                content = wfc.read()
                with open(wf_path, 'w', encoding='utf-8') as wfc2:
                    if len(content) == 0:
                        pass
                    else:
                        content = self.to_ollama_internal(
                            ".".join([
                                "you are a text rephraser",
                                "you rephrase any text given without giving explanations like 'here is the text rephrased...' or 'here is a rephrased ...'",
                                "evade writing sentences explaining what was done",
                            ]), "rephrase the following text:" + content)
                    wfc2.write(content)
    
    # used in conjuction with a keyword like "arasaka" inside of companies
    def lookup_wiki(self, keyword):
        k = keyword.lower().strip()
        for f in self.wiki:
            if k in f["file"].lower():
                return f["content"]
            if k+"_full" in f["file"].lower():
                return f["content"]
        return '(none available)'

    def lookup_info(self, context):
        cwd = os.getcwd() + "/wiki"
        dir_files = os.listdir(cwd)
        ctx =  context.lower()
        if ' ' in ctx:
            ctx = ctx.split(' ')
        else:
            ctx = [ctx]
        info = set()
        for f in dir_files:
            # just in case??
            if '_' in f:
                subfs = f.split('_')
                for subf in subfs:                    
                    if subfs in ctx:
                        info.add(f)
                        break            
            for w in ctx:
                if w in f:
                    info.add(f)
        info = list(info)  
        if len(info) > 0:
            contents = []
            for f in info:
                with open(f, 'r', encoding='utf-8') as file:
                    content = file.read()
                    contents.append({
                        "file": f,
                        "content" : content
                    })
            return contents
        return info