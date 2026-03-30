import os
import logging
import sys
import re

class PromptTemplateService:    
    def __init__(self, project_name):
        self.project_name = project_name
    
    def get_prompts(self):
        logging.info("Initializing prompts")
        prompts = {}
        prompt_files = os.listdir(os.getcwd()+"/projects/"+ self.project_name + "/prompts")
        for prompt_file in prompt_files:
            prompt_file_path = os.getcwd()+"/projects/"+ self.project_name + "/prompts/" + prompt_file
            with open(prompt_file_path, encoding='utf-8') as data:
                prompts[os.path.basename(prompt_file_path).replace(".txt", "")] = PromptTemplate(data.read().replace('', ''))
        return prompts

    def init_prompts(self):
        self.prompts = self.get_prompts()

    def get_placeholders(self, prompt_template):
        return re.findall(r'%([^%]+)%', prompt_template)
    
class PromptTemplate:
    def __init__(self, prompt_template):
        self.template_vars = {}
        self.prompt_template = prompt_template

    def bind_var(self, var_name, value_expr):
        self.template_vars[var_name] = value_expr
        return self
    
    def as_string(self):
        text = self.prompt_template
        for template_var, template_expr in self.prompt_template.items():
            text = text.replace('%'+template_var+'%', template_expr())
        return text
