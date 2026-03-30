import os
import yaml
import logging
from projects.all.services.config_node import ConfigNode
class CharacterOverridesService():
    def __init__(self,project_name, world_data):
        self.project_name = project_name
        self.world_data = world_data
        
    def init_npc_overrides(self):
        logging.info("Initializing npc overrides")
        overrides = os.listdir(os.getcwd()+"/projects/"+self.project_name + "/npc_overrides")
        overrides_res = {}
        for npc_override in overrides:
            npc_override_file = os.getcwd()+"/projects/"+self.project_name +"/npc_overrides/"+npc_override
            with open(npc_override_file, encoding='utf-8') as data:
                config_file = yaml.safe_load(data)
                overrides_res[npc_override] = ConfigNode(config_file)
        return overrides_res
    
    # looks up identifiers inside of look_in
    # so checks if world_data has the identifier
    def npc_override_matches(self, npc_override):
        identifiers = npc_override.identifiers
        found = False

        for identity in npc_override.identifiers:
            if found == True:
                break
            for look_for in npc_override.look_in:
                if found == True:
                    break
                v = getattr(self.world_data, look_for)
                if v == None:
                    continue
                if identity in v:
                    found = True
                    break
        return found