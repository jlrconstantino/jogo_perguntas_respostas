# General dependencies
import pandas as pd

def load_outputs(csv_path: str) -> tuple[dict[tuple[int,int,int], tuple[str, bool]], dict[tuple[int,int,int], tuple[str, bool]]]:
    '''
    Loads the outputs from CSV file as a dictionary.

    Parameters:
    ----------

    csv_path: str
        The path for the file containing the outputs for the models.

    Returns:
    -------

    symbolic_answers: dict[tuple[int,int,int], tuple[str, bool]]
        The answers for the symbolic model. Each key is a tuple containing 
        the indexes, in this order, for the topic, the context and the 
        question. Each value is the textual answer of the model, followed 
        by a boolean indicating if this answer is correct.

    neural_answers: dict[tuple[int,int,int], tuple[str, bool]]
        Same as the first output, but for the neural model. 
    '''
    # Loads the data
    df_outputs = pd.read_csv(csv_path)

    # Creates the holders for the outputs
    symbolic_answers = {}
    neural_answers = {}

    # Fetchs the data
    for _, (
        topic_idx, context_idx, question_idx, 
        symbolic_answer, neural_answer, 
        symbolic_is_correct, neural_is_correct
    ) in df_outputs.iterrows():
        symbolic_answers[(topic_idx, context_idx, question_idx)] = (symbolic_answer, symbolic_is_correct)
        neural_answers[(topic_idx, context_idx, question_idx)] = (neural_answer, neural_is_correct)

    return symbolic_answers, neural_answers