
OLLAMA_REST_HEADERS = {'Content-Type': 'application/json'}
import requests
import json
import logging
from openai import OpenAI
# internal ollama for images
from langchain_community.llms import Ollama


class OllamaService:
    def __init__(self, config, string_service):
        self.config = config
        self.string_service = string_service


    def llava(self, prompt, timeout=30):
        logging.info("llava")
        used_model = self.config.ollama.image
        jsonParam = {
            "model": used_model,
            "stream": True,
            "context": self.context,
            "role": "user",
            "content": "Please describe this image",
            "images": [prompt]
        }
        try:            
            response = requests.post(self.config.ollama.url,
                                    json=jsonParam,
                                    headers=OLLAMA_REST_HEADERS,
                                    stream=True,
                                    timeout=timeout)  # Increase the timeout value
            response.raise_for_status()

            full_response = ""
            for line in response.iter_lines():
                body = json.loads(line)
                token = body.get('response', '')
                full_response += token.replace('*', '').replace('"', '').replace(',\'','')

                if 'error' in body:
                    logging.error(f"Error from OLLaMa: {body['error']}")
                    responseCallback("Error: " + body['error'])
                    return

                if body.get('done', False) and 'context' in body:
                    self.context = body['context']
                    logging.info(full_response)
                    break

        except requests.exceptions.ReadTimeout as e:
            logging.error(f"ReadTimeout occurred while asking OLLaMa: {str(e)}")
        except requests.exceptions.RequestException as e:
            logging.error(f"An error occurred while asking OLLaMa: {str(e)}")

    def to_ollama_internal(self, system_prompt, prompt, model='', images=[], thinking=False):
        return self.to_ollama(system_prompt, prompt, model, images)

    def to_ollama(self, system_prompt, prompt, model='', images=[], thinking=False):
        logging.info("Asking OLLaMa internally")
        used_model = self.config.ollama.model
        if(len(model) > 0):
            used_model = model
        full_prompt = " <PROMPT>,\"" + prompt + ",\"</PROMPT>"
        logging.info("full_prompt:" + full_prompt)
        client = OpenAI(base_url=self.config.ollama.url, api_key="sk-xxx")
        full_response = ''
        if len(images) == 0: 
            full_response = client.chat.completions.create(
                model=used_model,
                messages= [{
                        "role":"system",
                        "content": [
                            {
                                "type": "text",
                                "text": system_prompt
                            }
                        ],
                    },
                    {
                        "role":"user",
                        "content": [
                            {
                                "type": "text",
                                "text": full_prompt
                            }
                        ],
                    }
                ],)
        else:
            full_response = client.chat.completions.create(
            model=used_model,
            messages= [{
                    "role":"system",
                    "content": [
                        {
                            "type": "text",
                            "text": system_prompt
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": full_prompt,
                        },
                        {
                            "type": "image_url",
                            "image_url": { "url": f"data:image/jpeg;base64,{images[0]}"}
                        }
                    ],
                }
            ],)
        
        print(full_response.choices[0].message.content)

        

        full_response = full_response.choices[0].message.content \
                .replace("<RESPONSE>", '') \
                .replace("</RESPONSE>", '') \
                .replace("<PROMPT>", '') \
                .replace("</PROMPT>", '') \
                .replace("<response>", '') \
                .replace("</response>", '') \
                .replace("<prompt>", '') \
                .replace("</prompt>", '') \
                .replace('*', '') \
                .replace('"', '') \
                .replace(',\'','')

        # found it using llamacpp
        full_response = self.string_service.remove_at_start(full_response, 'RESPONSE')
        full_response = self.string_service.remove_at_start(full_response, 'response')
        full_response = self.string_service.remove_at_start(full_response, 'V:')
        full_response = self.string_service.remove_at_start(full_response, 'span')
        full_response = self.string_service.remove_at_start(full_response, 'spanV')        
        full_response = self.string_service.remove_at_start(full_response, 'spanVspan')
        
        full_response_check = full_response.strip().lower()
        if full_response_check.startswith("here is a") or \
            full_response_check.startswith("here's a"):
            removed_start_sentence = full_response.split(":")
            if len(removed_start_sentence) > 1:
                full_response = ":".join(removed_start_sentence[1:])

        thinking_models = ['deepseek', 'deepscaler', 'qwen']
        for m in thinking_models:
            if m in used_model:
                thinking = True
                
        if thinking:
            try:                
                return full_response.split("</think>")[1]
            except ValueError:
                pass

        # if self.contains_html(full_response):
        #     return ''

        return full_response

    def is_prompt_llava(self, prompt):
        if prompt == "what do you see?" or \
            prompt == "what's this?" or \
            prompt == "what's that?" or \
            prompt == "what is this?" or \
            prompt == "what is that?" or \
            prompt == "what is that?" or \
            prompt == "report" or \
            "what do you see?" in prompt or \
            "what's this?" in prompt or \
            "what's that?" in prompt or \
            "what is this?" in prompt or \
            "what is that?" in prompt or \
            "what is that?" in prompt:
            #self.to_ollama_internal(OLLAMA_INTERNAL_IMAGE_YES_NO, prompt.replace('', '').strip().lower()).replace('', '').strip().lower() == 'yes':
            return True
        else:
            return False