# General dependencies
import numpy as np
import pandas as pd
import streamlit as st

# Local dependencies
from source.available_pages import Pages
from source.faquad import FaquadDataset
from models.model_output_loader import load_outputs
from models.metrics import compute_f1, exact_match


def _clear_game():
    states_to_clear = [
        "selected_topic",
        "selected_topic_idx",
        "selected_paragraph_idx",
        "selected_question_idx",
        "user_answered",
        "user_correct_answers",
        "user_textual_answers", 
        "user_answered_topics_indexes", 
        "user_answered_paragraphs_indexes", 
        "user_answered_questions_indexes", 
        "generated_results", 
        "scores_results", 
    ]
    for state in states_to_clear:
        if state in st.session_state:
            del st.session_state[state]
    st.session_state["current_page"] = Pages.HOME


def _generate_status_message(hits, question_idx):
    if hits[question_idx] == True:
        st.success("Correto")
    else:
        st.error("Incorreto")


def _preprocess_user_answer(user_selections) -> str:
    answer = ""
    for selection in sorted(user_selections, key=lambda x: x["start"]):
        answer += selection["text"]
    return answer


def _get_ground_truth(dataset, title, context_idx, question_idx) -> list[str]:
    ground_truth = dataset.get_answers(title, context_idx, question_idx)
    ground_truth = [answer["text"] for answer in ground_truth]
    return ground_truth


def generate_results_page():
    '''
    Generates the page of the user results.


    Session state dependencies:
    --------------------------

    dataset: FaquadDataset
        The dataset for the QA Game.

    user_correct_answers: dict[tuple[int,int,int], bool]
        Indicates, for a tuple of indexes of a topic, a paragraph and 
        a question, if the user correctly answered the question.
    
    user_textual_answers: dict[tuple[int,int,int], list[str]]
        Indicates, for a tuple of indexes of a topic, a paragraph and 
        a question, the textual answer of the user.


    Session state outputs:
    ---------------------

    generated_results: bool
        Indicates if the results are already generated.
    
    scores_results: dict[str, tuple[float, float]]
        Results of the scores; every value is a tuple containing 
        the mean and the standard deviation of their respective 
        score in this order. The keys are composed by the name 
        of the metric ("f1", "em" and "hit"), followed by an 
        underline ("_") and the name of the agent ("user", 
        "symbolic" and "neural"). Except "hit": this contains 
        boolean masks as values.
    '''
    # Loads the dataset and the answers
    dataset: FaquadDataset = st.session_state["dataset"]
    user_correct_answers = st.session_state["user_correct_answers"]
    user_textual_answers = st.session_state["user_textual_answers"]
    symbolic_answers_dict, neural_answers_dict = load_outputs("./data/models_answers.csv")

    # Process the results if not processed yet
    if "generated_results" not in st.session_state:

        # To hold the scores
        user_f1_scores = []
        user_em_scores = []
        user_hit_scores = []
        symbolic_f1_scores = []
        symbolic_em_scores = []
        symbolic_hit_scores = []
        neural_f1_scores = []
        neural_em_scores = []
        neural_hit_scores = []

        # Computes scores
        for (title_idx, context_idx, question_idx), user_selections in user_textual_answers.items():

            # Pre-process the answer of the user
            user_answer = _preprocess_user_answer(user_selections)
            user_is_correct = user_correct_answers[title_idx, context_idx, question_idx]

            # Answer of the symbolic model
            symbolic_answer, symbolic_is_correct = symbolic_answers_dict[title_idx, context_idx, question_idx]
            if not isinstance(symbolic_answer, str):
                symbolic_answer = ""

            # Answer of the neural model
            neural_answer, neural_is_correct = neural_answers_dict[title_idx, context_idx, question_idx]
            if not isinstance(neural_answer, str):
                neural_answer = ""

            # Title (topic)
            title = dataset.sorted_titles[title_idx]

            # Gets answers as the ground-truth
            ground_truth = _get_ground_truth(dataset, title, context_idx, question_idx)

            # Temporary score holders in order to get the max score among the different expected answers
            temp_user_f1_scores = []
            temp_user_em_scores = []
            temp_symbolic_f1_scores = []
            temp_symbolic_em_scores = []
            temp_neural_f1_scores = []
            temp_neural_em_scores = []

            # Computes the different scores for different expected answers
            for expected_answer in ground_truth:

                # Computes scores for the user
                temp_user_f1_scores.append(compute_f1(user_answer, expected_answer))
                temp_user_em_scores.append(exact_match(user_answer, expected_answer))

                # Computes scores for the sybolic model
                temp_symbolic_f1_scores.append(compute_f1(symbolic_answer, expected_answer))
                temp_symbolic_em_scores.append(exact_match(symbolic_answer, expected_answer))

                # Computes scores for the neural model
                temp_neural_f1_scores.append(compute_f1(neural_answer, expected_answer))
                temp_neural_em_scores.append(exact_match(neural_answer, expected_answer))
            
            # Saves the max scores
            user_f1_scores.append(max(temp_user_f1_scores))
            user_em_scores.append(max(temp_user_em_scores))
            user_hit_scores.append(user_is_correct)
            symbolic_f1_scores.append(max(temp_symbolic_f1_scores))
            symbolic_em_scores.append(max(temp_symbolic_em_scores))
            symbolic_hit_scores.append(symbolic_is_correct)
            neural_f1_scores.append(max(temp_neural_f1_scores))
            neural_em_scores.append(max(temp_neural_em_scores))
            neural_hit_scores.append(neural_is_correct)

        # Loading everything to session state
        st.session_state["scores_results"] = {
            "f1_user": (np.mean(user_f1_scores), np.std(user_f1_scores)), 
            "f1_symbolic": (np.mean(symbolic_f1_scores), np.std(symbolic_f1_scores)), 
            "f1_neural": (np.mean(neural_f1_scores), np.std(neural_f1_scores)), 
            "em_user": (np.mean(user_em_scores), np.std(user_em_scores)), 
            "em_symbolic": (np.mean(symbolic_em_scores), np.std(symbolic_em_scores)), 
            "em_neural": (np.mean(neural_em_scores), np.std(neural_em_scores)), 
            "hit_user": user_hit_scores, 
            "hit_symbolic": symbolic_hit_scores, 
            "hit_neural": neural_hit_scores, 
        }
        st.session_state["generated_results"] = True

        # Freeing memory
        del user_f1_scores
        del user_em_scores
        del user_hit_scores
        del symbolic_f1_scores
        del symbolic_em_scores
        del symbolic_hit_scores
        del neural_f1_scores
        del neural_em_scores
        del neural_hit_scores

    # Loads everything necessary from session state
    scores = st.session_state["scores_results"]
    
    # Page structure (first half)
    st.title("**Resultados**")
    st.divider()

    # Results data
    df_results = pd.DataFrame(np.array([
            [np.sum(scores["hit_symbolic"]), "{:.2f} ± {:.2f}".format(*scores["f1_symbolic"]), "{:.2f} ± {:.2f}".format(*scores["em_symbolic"])], 
            [np.sum(scores["hit_user"]), "{:.2f} ± {:.2f}".format(*scores["f1_user"]), "{:.2f} ± {:.2f}".format(*scores["em_user"])], 
            [np.sum(scores["hit_neural"]), "{:.2f} ± {:.2f}".format(*scores["f1_neural"]), "{:.2f} ± {:.2f}".format(*scores["em_neural"])], 
        ]).T, 
        columns=["🐌 O Caracol", "😄 Usuário (Você)", "👑 Bert"],
        index=["Total de Acertos", "Pontuação F1", "Casamento Exato"])
    
    # Writes the results
    st.dataframe(df_results, use_container_width=True)

    # Page structure (second half)
    st.divider()
    st.markdown("## Comparar respostas")

    # Gets the questions
    questions = [
        (
            tidx, cidx, qidx, 
            dataset.get_question(dataset.sorted_titles[tidx], cidx, qidx) 
        )
        for tidx, cidx, qidx in user_textual_answers.keys()]

    # Question selection
    question_idx = st.selectbox(
        "Selecione uma questão:", 
        range(len(questions)), 
        format_func=lambda x: questions[x][-1])
    
    # Gets the answers
    tidx, cidx, qidx, _ = questions[question_idx]
    title = dataset.sorted_titles[tidx]
    expected_answers = [answer["text"] for answer in dataset.get_answers(title, cidx, qidx)]
    user_answer = _preprocess_user_answer(user_textual_answers[tidx, cidx, qidx])
    symbolic_answer, _ = symbolic_answers_dict[tidx, cidx, qidx]
    neural_answer, _ = neural_answers_dict[tidx, cidx, qidx]
    
    # Expected answer display
    st.selectbox("Respostas possíveis esperadas:", expected_answers)

    # Symbolic answer
    cols = st.columns(3)
    with cols[0]:
        st.markdown("## 🐌 **O Caracol**")
        _generate_status_message(scores["hit_symbolic"], question_idx)
        st.write(symbolic_answer if len(symbolic_answer) > 0 else "...")
    
    # User answer
    with cols[1]:
        st.markdown("## 😄 **Usuário (Você)**")
        _generate_status_message(scores["hit_user"], question_idx)
        st.write(user_answer if len(user_answer) > 0 else "...")

    # Neural answer
    with cols[2]:
        st.markdown("## 👑 **Bert**")
        _generate_status_message(scores["hit_neural"], question_idx)
        st.write(neural_answer if len(neural_answer) > 0 else "...")

    # Clear game button
    st.divider()
    with st.columns(5)[-1]:
        st.button("Novo jogo", on_click=_clear_game, use_container_width=True)