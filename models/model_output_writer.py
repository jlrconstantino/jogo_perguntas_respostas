# General dependencies
import os
from tqdm import tqdm
from csv import writer
from sentence_splitter import SentenceSplitter

# Local dependencies
from source.faquad import FaquadDataset
from models.symbolic_model import symbolic_model
from models.neural_model import get_prediction as neural_model

def write_model_outputs(csv_path: str, dataset: FaquadDataset) -> None:
    '''
    Writes an CSV for the outputs of both models, symbolic and 
    neural. The columns are the following: "topic_idx", "context_idx", 
    "question_idx", "symbolic_answer" and "neural_answer".

    Parameters:
    ----------

    csv_path: str
        The path for the CSV file to be written.

    dataset: FaquadDataset
        The dataset to retrieve the inputs from.
    '''

    # File path verification
    _, file_extension = os.path.splitext(csv_path)
    if file_extension != ".csv":
        csv_path = csv_path + ".csv"

    # Sentence splitter for the symbolic model
    splitter = SentenceSplitter(language="pt")
    
    # Target .csv file opening
    with open(csv_path, "w", newline="", encoding="utf-8") as target_file:

        # CSV writer and registry header
        csv_writer = writer(target_file)
        header = [
            "topic_idx", "context_idx", "question_idx", 
            "symbolic_answer", "neural_answer"
        ]
        csv_writer.writerow(header)
    
        # Iterates through every topic, context and question
        for topic_idx, topic in tqdm(enumerate(dataset.sorted_titles), desc="topic", total=len(dataset.sorted_titles)):
            num_contexts = dataset.get_num_paragraphs(topic)
            for context_idx in tqdm(range(num_contexts), desc="context", total=num_contexts):
                context = dataset.get_context(topic, context_idx)
                num_questions = dataset.get_num_questions(topic, context_idx)
                for question_idx in tqdm(range(num_questions), desc="question", total=num_questions):
                    question = dataset.get_question(topic, context_idx, question_idx)

                    # Gets the outputs of the models
                    symbolic_answer = symbolic_model(context, question, splitter)
                    neural_answer = neural_model(context, question)

                    # Writes the current row
                    csv_writer.writerow([
                        topic_idx, context_idx, question_idx, 
                        symbolic_answer, neural_answer
                    ])