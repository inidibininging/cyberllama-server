import os
import yaml
import logging
import random
from projects.all.services.config_node import ConfigNode

class OceanService:
    def __init__(self, project_name):        
        self.project_name = project_name
        
    def init_ocean_expr(self):
        logging.info("Initializing ocean expression mapping")
        ocean_expr_obj = {}
        
        ocean_expr_file = os.getcwd()+"/projects/"+self.project_name + "/ocean_expr.yaml"
        with open(ocean_expr_file, encoding='utf-8') as data:
            config_file = yaml.safe_load(data)
            ocean_expr_obj = ConfigNode(config_file)
        return ocean_expr_obj

    def gen_ocean(self):
        openness = random.randrange(0, 10)
        conscientiousness = random.randrange(0, 10)
        extraversion = random.randrange(0, 10)
        agreeableness = random.randrange(0, 10)
        neuroticism = random.randrange(0, 10)

        return {
            "openness" : openness,
            "conscientiousness" : conscientiousness,
            "extraversion" : extraversion,
            "agreeableness" : agreeableness,
            "neuroticism" : neuroticism,
        }
    def gen_ocean_personality(self, ocean):
        openness = ocean.openness
        conscientiousness = ocean.conscientiousness
        extraversion = ocean.extraversion
        agreeableness = ocean.agreeableness
        neuroticism = ocean.neuroticism

        ocean_personality = { 
            "openness": "",
            "conscientiousness": "",
            "extraversion": "",
            "agreeableness": "",
            "neuroticism": "",
        }

        if openness < 3:
            ocean_personality["openness"] = 'Low curiosity, traditional'
        elif openness < 5:
            ocean_personality["openness"] = 'Moderate curiosity, open to new experiences'
        elif openness < 7:
            ocean_personality["openness"] = 'High curiosity, imaginative, adventurous'
        
        if conscientiousness < 3:
            ocean_personality["conscientiousness"] = 'Disorganized, careless'
        elif conscientiousness < 5:
            ocean_personality["consci_ventiousness"] = 'Somewhat organized, reliable'
        elif conscientiousness < 7:
            ocean_personality["conscientiousness"] = 'Highly organized, disciplined, goal-oriented'

        if extraversion < 3:
            ocean_personality["conscientiousness"] ='Reserved, introverted'
        elif extraversion < 5:
            ocean_personality["conscientiousness"] ='Moderately social, enjoys some interaction'
        elif extraversion < 7:
            ocean_personality["conscientiousness"] ='Outgoing, energetic, thrives in social settings'

        if agreeableness < 3:
            ocean_personality["agreeableness"] = 'Competitive, critical'            
        elif agreeableness < 5:
            ocean_personality["agreeableness"] = 'Cooperative, empathetic'
        elif agreeableness < 7:
            ocean_personality["agreeableness"] = 'Highly compassionate, trusting, altruistic'
        
        if neuroticism < 3:
            ocean_personality["neuroticism"] = 'Emotionally stable, calm'
        elif neuroticism < 5:
            ocean_personality["neuroticism"] = 'Somewhat anxious, mood swings'
        elif neuroticism < 7:
            ocean_personality["neuroticism"] = 'Highly anxious, sensitive, prone to stress'

        return  "openness:" + ocean_personality["openness"] + "\n" + \
                "conscientiousness:" + ocean_personality["conscientiousness"] + "\n"  + \
                "extraversion:" + ocean_personality["extraversion"] + "\n"  + \
                "agreeableness:" + ocean_personality["agreeableness"] + "\n"  + \
                "neuroticism:" + ocean_personality["neuroticism"]
        