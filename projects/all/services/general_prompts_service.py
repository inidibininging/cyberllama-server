class GeneralPromptsService:
    def __init__(self, config):
        self.config = config
        self.ollama_service = ollama_service        

    def topic_generator(self, prompt):
        return self.ollama_service.to_ollama_internal(
            'You are a topic prompt generator extender. you extend a topic into a dialog line', prompt).strip()

    def reverse_prompt(self, prompt):
        return self.ollama_service.to_ollama_internal('You are prompt generator. you generate a possible prompt that outputs the given result', prompt).strip()
    
    