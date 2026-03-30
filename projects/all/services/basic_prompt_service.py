
OLLAMA_INTERNAL_INSTR_STR="INSTRUCTION"
OLLAMA_INTERNAL_ADDENDUM_STR="ADDENDUM"
OLLAMA_INTERNAL_RESPONSE_STR="RESPONSE"
OLLAMA_INTERNAL_IMPORTANT_STR="IMPORTANT"

OLLAMA_INTERNAL_INSTR_BEGIN="<INSTRUCTION>"
OLLAMA_INTERNAL_INSTR_END="</INSTRUCTION>"

OLLAMA_INTERNAL_ADDENDUM_START='<ADDENDUM>'
OLLAMA_INTERNAL_ADDENDUM_END='</ADDENDUM>'

OLLAMA_INTERNAL_RESPONSE_START='<RESPONSE>'
OLLAMA_INTERNAL_RESPONSE_END='</RESPONSE>'

OLLAMA_INTERNAL_IMPORTANT_START='<IMPORTANT>'
OLLAMA_INTERNAL_IMPORTANT_END='</IMPORTANT>'
OLLAMA_CR="\n"

OLLAMA_INTERNAL_INSTR_BRIEF="Keep it brief"
OLLAMA_INTERNAL_INSTR_BRIEF_AND_SHORT="Keep it brief and short"
OLLAMA_INTERNAL_INSTR_NO_EXPLANATIONS="Give me no explanations"
OLLAMA_INTERNAL_INSTR_LIST_ONLY="Give me ONLY the list"
OLLAMA_INTERNAL_INSTR_NO_TELL_CHARACTER="Do not say who you are going to be"
OLLAMA_INTERNAL_INSTR_ADD_PREVIOUS_LINES="Take the previous lines into account"
OLLAMA_INTERNAL_INSTR_DRY="Do not repeat yourself"
OLLAMA_INTERNAL_INSTR_DO_NOT_ENUMERATE="DO NOT ENUMERATE"
OLLAMA_INTERNAL_INSTR_DO_NOT_NARRATE_STORYTELL="DO NOT NARRATE or storytell"
OLLAMA_INTERNAL_INSTR_FOLLOW_EXACT_INSTRUCTIONS="You follow my instructions to the letter"
OLLAMA_INTERNAL_INSTR_AVOID_NARRATION="AVOID any storytelling, monologues, narrator monologues / explanations or responses"
OLLAMA_INTERNAL_INSTR_RESPONSE_NO_EXPLANATION="Give me only the responses without any explanation"

OLLAMA_INTERNAL_INSTR_RESPONSE_TO_LINE_INTRO="Generate a response to the following line"

OLLAMA_INTERNAL_GEN_LIST_OF="Generate a list of "
# OLLAMA_INTERNAL_INSTR_IMPERSONATE_BEGIN="You are "
# OLLAMA_INTERNAL_INSTR_CR_LIST_DELIMITER="Use only carriage return for every new item"

# old
# OLLAMA_INTERNAL_GEN_LIST_CLEAN_FIX="Do not use anything related to a certain place or situation. Give me ONLY the list and do not enumerate. " + OLLAMA_INTERNAL_INSTR_CR_LIST_DELIMITER

class BasicPromptService:
    def __init__(self, project_name):
        self.project_name = project_name
    
    def prompt_dont_use_anything_related(self, items):
        return "Do not use anything related to " + ",".join(items)

    def prompt_avoid_any(self, items):
        return "AVOID any " + ",".join(items)

    def tagged(self, tag, content):
        return "<"+tag+">"+\
            content+\
            "</"+tag+">"

    def prompt_delimiter_item(self, delimiter):        
        return "Use only " + delimiter + " for every new item"

    def prompt_avoid_any(self, items):
        return "AVOID any " + ",".join(items)    

    def prompt_important(self, content):
        return self.tagged(OLLAMA_INTERNAL_IMPORTANT_STR, content)
    
    def prompt_instruction(self, content):
        return self.tagged(OLLAMA_INTERNAL_INSTR_STR, content)
    
    def prompt_addendum(self, content):
        return self.tagged(OLLAMA_INTERNAL_ADDENDUM_STR, content)

    def prompt_addendum(self, content):
        return self.tagged(OLLAMA_INTERNAL_ADDENDUM_STR, content)

    def prompt_list_of(self, list_type, item_count, delimiter='-'):
        return self.prompt_instruction(
            OLLAMA_INTERNAL_GEN_LIST_OF + str(item_count) + text +\
            OLLAMA_CR +\
            self.prompt_dont_use_anything_related(['a certain place' , 'situation'])+\
            OLLAMA_INTERNAL_INSTR_LIST_ONLY,
            OLLAMA_INTERNAL_INSTR_DO_NOT_ENUMERATE,
        )+\
        OLLAMA_CR+\
        self.prompt_important(
            ".".join(
                OLLAMA_INTERNAL_INSTR_AVOID_NARRATION,
                OLLAMA_INTERNAL_INSTR_RESPONSE_NO_EXPLANATION
            )
        )

    def prompt_opposite_list_of(self, list_type, item_count):
        return self.prompt_list_of(
            item_count,
            " that are the opposite of " + list_type
        )

    def prompt_expand_list_of(self, list_type, item_count):
        return self.prompt_list_of(
            item_count,
            " that are the same as " + list_type + "." +\
            " AND " + OLLAMA_INTERNAL_INSTR_DRY
        )
    
    def prompt_impersonate(self, role_in_singular):
        # stuff to try: impersonate the following role:
        # stuff to try: impersonate ...:
        # stuff to try: take the role of:
        return "You are a " + role_in_singular

    def prompt_role(self, role):
        # stuff to try: impersonate the following role:
        # stuff to try: impersonate ...:
        # stuff to try: take the role of:
        return "Take the following role: " + role

    def prompt_take_role(self, role):
        return "Take the following role: " + role
