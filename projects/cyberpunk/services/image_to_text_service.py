import logging
import base64
import pathlib
import sys
import uuid
from PIL import Image
from io import BytesIO

OLLAMA_INTERNAL_INSTR_BEGIN="<INSTRUCTION>"
OLLAMA_INTERNAL_INSTR_END="</INSTRUCTION>"
# LLAVA_DESCRIBE_IMAGE= OLLAMA_INTERNAL_INSTR_BEGIN + "The following image was made in the world of " + OLLAMA_WORLD_NAME + ". Describe environment, objects, buildings and persons you see only with keywords. Put an emphasis on the objects, buildings or persons set at the center of the image.<IMPORTANT-PROMPT-INSTRUCTIONS>Ignore any UI Elements</IMPORTANT-PROMPT-INSTRUCTIONS>"
# LLAVA_MAKE_LOCATION_TITLE_DESCRIPTION= OLLAMA_INTERNAL_INSTR_BEGIN + "You are a keyword generator. Focus at the most centered building or location aspects and give me a list of keywords (separated by \"-\") of the most centered object with less words as possible. If there are any signs, take the text content one and give me the title. If it is a building and the building has no sign, focus on the colors, architecture. Select the most prominent building in this image. Keep it brief and short<IMPORTANT-PROMPT-INSTRUCTIONS>Ignore any UI Elements. Do not give any explanations and any introductory sentences. As a bad example: \"' The image title should be:\". </IMPORTANT-PROMPT-INSTRUCTIONS>"
# LLAVA_MAKE_LOCATION_TITLE= OLLAMA_INTERNAL_INSTR_BEGIN + "You are an image title generator. Focus at the most centered building and give me a title that describes the most centered object with less words as possible. If there are any signs, take the text content one and give me the title. If it is a building and the building has no sign, focus on the colors, architecture. Select the most prominent building in this image. Keep it brief and short<IMPORTANT-PROMPT-INSTRUCTIONS>Ignore any UI Elements. Do not give any explanations and any introductory sentences. As a bad example: \"' The image title should be:\". </IMPORTANT-PROMPT-INSTRUCTIONS>"
IMAGE_OUTPUT_PATH='screenshot.png'

class ImageToTextService:
    def __init__(self, config, basic_prompt_service, ollama_service, screenshot_service, cleaner_service, sqlite3_cache_service):
        self.config = config
        self.basic_prompt_service = basic_prompt_service
        self.ollama_service = ollama_service
        self.screenshot_service = screenshot_service
        self.cleaner_service = cleaner_service
        self.sqlite3_cache_service = sqlite3_cache_service
    
    def set_llava_describe_image(self):
        self.llava_describe_image = self.basic_prompt_service.prompt_instruction(\
            ". ".join([
                "The following image was made in the world of " + self.config.world.world_name,
                "Describe environment, objects, buildings and persons you see only with keywords",
                "Put an emphasis on the objects, buildings or persons set at the center of the image",
            ])+\
            self.basic_prompt_service.tagged(\
                'IMPORTANT-PROMPT-INSTRUCTIONS',\
                'Ignore any UI Elements')
        )

    def set_llava_make_location_title(self):
        self.llava_make_location_title = self.basic_prompt_service.prompt_instruction(
            self.basic_prompt_service.prompt_impersonate("title generator")+\
            ". ".join([
                "Focus at the most centered building and give me a title that describes the most centered object with less words as possible"
                "If there are any signs, take the text content one and give me the title",
                "If it is a building and the building has no sign, focus on the colors, architecture",
                "Select the most prominent building in this image",
                OLLAMA_INTERNAL_INSTR_BRIEF_AND_SHORT,\
            ])+\
            self.basic_prompt_service.tagged(\
                'IMPORTANT-PROMPT-INSTRUCTIONS',\
                ". ".join([\
                    "Ignore any UI Elements. ",
                    "Do not give any explanations and any introductory sentences",
                    "As a bad example: \"' The image title should be:\"",
                ])
            )
        )

    def set_llava_make_location_title_description(self):
        self.llava_make_location_title_description = self.basic_prompt_service.prompt_instruction(
            self.basic_prompt_service.prompt_impersonate("keyword generator")+\
            ". ".join([
                "Focus at the most centered building or location aspects and give me a list of keywords (separated by \"-\") of the most centered object with less words as possible",
                "If there are any signs, take the text content one and give me the title",
                "If it is a building and the building has no sign, focus on the colors, architecture",
                "Select the most prominent building in this image",
                OLLAMA_INTERNAL_INSTR_BRIEF_AND_SHORT,
            ])+\
            self.basic_prompt_service.tagged(\
                'IMPORTANT-PROMPT-INSTRUCTIONS',\
                ". ".join([
                    "Ignore any UI Elements",
                    "Do not give any explanations and any introductory sentences",
                    "As a bad example: \"' The image title should be:\"",
                ])
            )
        )

    def describe_image(self, district, sub_district, x, y, z):
        # in the except secion, there could be like a map of known spots like for example:
        # being near a vendor stand (by mapping either coordinates or by checking the npc if he/she is a vendor)
        # so it would be something like vendor + district + sub district => something something
        # other thing could be like caching the x,y,z + llava description for location descriptions
        # 
        response = ''
        try:
            self.screenshot_service.take_screenshot(IMAGE_OUTPUT_PATH)
            path = str(pathlib.Path(__file__).parent.resolve())
            file_path = path + "/" + IMAGE_OUTPUT_PATH
            file64 = self.screenshot_service.jpeg_to_base64(Image.open(file_path))
            logging.debug(f"Describing media {file_path}")
            response = self.ollama_service.to_ollama_internal(
                self.llava_describe_image,
                'You are standing facing the following in this image.',
                model=self.config.ollama.image,
                images=[file64])
        except Exception as e:
            response = ''
        
        cleaned_t = self.cleaner_service.clean_text(response)
        self.sqlite3_cache_service.cache_db_add_location_description(uuid.uuid4(), district, sub_district, x, y, z, cleaned_t)
        return cleaned_t

    def make_location_title(self):        
        # in the except secion, there could be like a map of known spots like for example:
        # being near a vendor stand (by mapping either coordinates or by checking the npc if he/she is a vendor)
        # so it would be something like vendor + district + sub district => something something
        # other thing could be like caching the x,y,z + llava description for location descriptions
        # 
        response = ''
        cleaned_t = ''
        try:
            self.screenshot_service.take_screenshot(IMAGE_OUTPUT_PATH)
            path = str(pathlib.Path(__file__).parent.resolve())
            file_path = path + "/" + IMAGE_OUTPUT_PATH
            file64 = self.screenshot_service.jpeg_to_base64(Image.open(file_path))
            logging.debug(f"Describing media {file_path}")
            self.ollama_service.to_ollama_internal(self.llava_make_location_title, 
                'You are facing the following structure / object in this image.',
                model=self.config.ollama.image,
                images=[file64])
            cleaned_t = self.cleaner_service.clean_text(response)\
                .replace(self.config.world.world_name, "")\
                .replace(self.config.world.world_name.lower(), "")\
                .replace("Neon", "")
            self.ollama_service.to_ollama_internal(self.llava_make_location_title, 
                'Summarize this description as a short title for a location. Emphasize on the details and description mentioned. Give me just the title',)
            cleaned_t = self.cleaner_service.clean_text(response)\
                .replace(self.config.world.world_name, "")\
                .replace(self.config.world.world_name.lower(), "")\
                .replace("Neon", "")
            if (len(cleaned_t) == 0):
                response2 = self.ollama_service.to_ollama_internal(
                    self.llava_make_location_title_description, 
                    'You are facing the following structure / object in this image.',
                    model=self.config.ollama.image,
                    images=[file64]).split("-")
                t = []
                for r in response2:
                    t.append(self.clean_text(r)\
                    .replace(self.config.world.world_name, "")\
                    .replace(self.config.world.world_name.lower(), "")\
                    .replace("Neon", ""))
                cleaned_t = ",".join(t)
            return cleaned_t
        except Exception as e:
            response = ''
            response2 = ''
        logging.debug(response)
        return cleaned_t