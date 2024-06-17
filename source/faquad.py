# General dependencies
import os
import json

class FaquadDataset:
    '''
    Dataset Manager for the FaQuAD.

    Parameters:
    ----------

    file_path: str
        The path to the .json file containing 
        the FaQuAD dataset.
    '''
    def __init__(self, file_path: str) -> None:

        # Verifies if file exists
        if os.path.isfile(file_path):

            # Loads the json
            with open(file_path, "r", encoding="utf-8") as fp:
                self._data: list[dict] = json.load(fp)["data"]
            
            # Transforms it into a proper dict for data handling
            self._data: dict = {elem["title"]: elem for elem in self._data}
            for elem in self._data.values():
                del elem["title"]

        # If file does not exist
        else:
            raise ValueError("expected {} to be a file path".format(file_path))
    
    @property
    def titles(self) -> list[str]:
        ''' The titles of the contexts for question-answering. '''
        return list(self._data.keys())

    def get_num_paragraphs(self, title: str) -> int:
        ''' Returns the number of paragraphs of a given title. '''
        return len(self._data[title]["paragraphs"])

    def get_paragraph_previews(self, title: str) -> list[str]:
        ''' Returns the previews (first fours words) of every paragraph from a given title '''
        return [
            " ".join(par["context"].split(" ")[:4]) + "..."
            for par in self._data[title]["paragraphs"]
        ]

    def get_context(self, title: str, paragraph: int) -> str:
        ''' Returns the context for a given paragraph of a title. '''
        return self._data[title]["paragraphs"][paragraph]["context"]
    
    def get_question_previews(self, title: str, paragraph: int) -> list[str]:
        ''' Returns the previews of all questions for a given paragraph. '''
        return [ 
            " ".join(par["question"].split(" ")[:4]) + "..." 
            for par in self._data[title]["paragraphs"][paragraph]["qas"]
        ]
    
    def get_question(self, title: str, paragraph: int, question: int) -> str:
        ''' Returns the question for the given title, paragraph index and question index.'''
        return self._data[title]["paragraphs"][paragraph]["qas"][question]["question"]

    def get_answers(self, title: str, paragraph: int, question: int) -> list[dict]:
        '''
        Returns all answers for given title, paragraph index and question index. 
        Every answer has two attributes: "answer_start" and "text".
        '''
        return self._data[title]["paragraphs"][paragraph]["qas"][question]["answers"]
    
    def get_next_question_indexes(self, title: str, paragraph: int, question: int) -> tuple[int, int, int]:
        '''
        Returns the indexes for the topic, paragraph and question for the next 
        available question given the provided current one.
        '''
        # Gets the sorted titles
        sorted_titles = sorted(self._data.keys())
        title_idx = sorted_titles.index(title)

        # Tries next question first
        num_questions = len(self._data[title]["paragraphs"][paragraph]["qas"])
        if question < num_questions - 1:
            return title_idx, paragraph, question + 1
        
        # Tries next paragraph if not possible
        num_paragraphs = len(self._data[title]["paragraphs"])
        if paragraph < num_paragraphs - 1:
            return title_idx, paragraph + 1, 0
        
        # Finally, uses topic if none of the above worked
        num_titles = len(sorted_titles)
        if title_idx < num_titles - 1:
            return title_idx + 1, 0, 0
        return 0, 0, 0

    def get_previous_question_indexes(self, title: str, paragraph: int, question: int) -> tuple[int, int, int]:
        '''
        Returns the indexes for the topic, paragraph and question for the previous 
        available question given the provided current one.
        '''
        # Gets the sorted titles
        sorted_titles = sorted(self._data.keys())
        title_idx = sorted_titles.index(title)

        # Tries next question first
        num_questions = len(self._data[title]["paragraphs"][paragraph]["qas"])
        if question > 0:
            return title_idx, paragraph, question - 1
        
        # Tries next paragraph if not possible
        if paragraph > 0:
            num_questions = len(self._data[title]["paragraphs"][paragraph-1]["qas"])
            return title_idx, paragraph-1, num_questions-1
        
        # Finally, uses topic if none of the above worked
        if title_idx > 0:
            num_paragraphs = len(self._data[sorted_titles[title_idx-1]]["paragraphs"])
            num_questions = len(self._data[sorted_titles[title_idx-1]]["paragraphs"][paragraph-1]["qas"])
            return title_idx-1, num_paragraphs-1, num_questions-1
        
        # Last question
        num_titles = len(sorted_titles)
        num_paragraphs = len(self._data[sorted_titles[title_idx-1]]["paragraphs"])
        num_questions = len(self._data[sorted_titles[title_idx-1]]["paragraphs"][paragraph-1]["qas"])
        return num_titles-1, num_paragraphs-1, num_questions-1
