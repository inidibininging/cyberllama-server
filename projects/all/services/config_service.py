import logging
import yaml
import os
from projects.all.services.config_node import ConfigNode

class ConfigService:
    def __init__(self, project_name):
        self.project_name = project_name

    def init_config(self):
        logging.info("Initializing configuration")
        with open(os.getcwd()+"/projects/"+ self.project_name + "/config.yaml", encoding='utf-8') as data:
            config_file = yaml.safe_load(data)
        config = ConfigNode(config_file)
        return config