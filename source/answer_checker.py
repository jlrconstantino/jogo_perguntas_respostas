def check_answer(user_selections: list[dict], question_answers: list[dict]) -> bool:
    ''' Checks if an answer is correct. '''
    for answer in question_answers:
        answer_start = answer["answer_start"]
        for user_selection in user_selections:
            if answer_start >= user_selection["start"] and answer_start <= user_selection["end"]:
                return True
    return False