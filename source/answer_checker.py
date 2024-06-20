# General dependencies
import re
import itertools

# Local dependencies
from models.metrics import normalize_text
 

def remove_white_spaces(string):
    ''' Removes white spaces from strings '''
    pattern = re.compile(r'\s+')
    string = re.sub(pattern, '', string)
    resList = list(itertools.filterfalse(lambda x: x == ' ', string))
    return ''.join(resList)


def check_answer_from_user_selections(user_selections: list[dict], question_answers: list[dict]) -> bool:
    ''' Checks if an answer is correct. '''
    for answer in question_answers:
        answer_start = answer["answer_start"]
        answer_end = answer_start + len(answer["text"])
        for user_selection in user_selections:
            if answer_start >= user_selection["start"] and answer_end <= user_selection["end"]:
                return True
    return False


def check_answer_from_text(answer: str, truth: str) -> bool:
    ''' Checks if an answer is correct. '''
    return re.search(truth, answer) is not None