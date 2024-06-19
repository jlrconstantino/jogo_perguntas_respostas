# General dependencies
import numpy as np
import streamlit as st
from sentence_splitter import SentenceSplitter

# Local dependencies
from source.available_pages import Pages
from source.answer_checker import check_answer_from_text
from models.symbolic_model import compute_f1, exact_match, symbolic_model
#from models.neural_model import get_prediction as neural_model


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
        "user_answered_questions_indexes"
    ]
    for state in states_to_clear:
        if state in st.session_state:
            del st.session_state[state]
    st.session_state["current_page"] = Pages.HOME


def generate_results_page():
    '''
    Generates the page of the user results.

    Session state dependencies:
    --------------------------

    dataset: FaquadDataset
        The dataset for the QA Game.
    
    user_textual_answers: dict[tuple[int,int,int], list[str]]
        Indicates, for a tuple of indexes of a topic, a paragraph and 
        a question, the textual answer of the user.
    '''
    # Gets the dataset and the answers
    dataset = st.session_state["dataset"]
    user_textual_answers = st.session_state["user_textual_answers"]

    # Sentence splitter
    splitter = SentenceSplitter(language="pt")

    # To store the questions
    questions = []

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

    # To hold the answers of the models
    expected_answers = []
    user_answers = []
    symbolic_answers = []
    neural_answers = []

    # Computes scores
    for (title_idx, context_idx, question_idx), user_selections in user_textual_answers.items():

        # Pre-process the answer
        answer = ""
        for selection in sorted(user_selections, key=lambda x: x["start"]):
            answer  += selection["text"]

        # Title (topic)
        title = dataset.sorted_titles[title_idx]

        # Gets first answer as the ground-truth
        ground_truth = dataset.get_answers(title, context_idx, question_idx)[0]["text"]
        expected_answers.append(ground_truth)

        # Computes scores for the user
        user_answers.append(answer)
        user_f1_scores.append(compute_f1(answer, ground_truth))
        user_em_scores.append(exact_match(answer, ground_truth))
        user_hit_scores.append(check_answer_from_text(answer, ground_truth))

        # Gets both context and question
        context = dataset.get_context(title, context_idx)
        question = dataset.get_question(title, context_idx, question_idx)
        questions.append(question)

        # Computes scores for the sybolic model
        symbolic_answer = symbolic_model(context, question, splitter)
        symbolic_answers.append(symbolic_answer)
        symbolic_f1_scores.append(compute_f1(symbolic_answer, ground_truth))
        symbolic_em_scores.append(exact_match(symbolic_answer, ground_truth))
        symbolic_hit_scores.append(check_answer_from_text(symbolic_answer, ground_truth))

        # Computes scores for the neural model
        neural_answer = symbolic_answer#neural_model(context, question)
        neural_answers.append(neural_answer)
        neural_f1_scores.append(compute_f1(neural_answer, ground_truth))
        neural_em_scores.append(exact_match(neural_answer, ground_truth))
        neural_hit_scores.append(check_answer_from_text(neural_answer, ground_truth))
    
    # Page structure (first half)
    st.title("Resultados")
    st.divider()
    cols = st.columns(3)
    with cols[0]:
        st.markdown("## **Modelo Simbólico**")
        st.write("")
        st.markdown("**Pontuação F1:**")
        st.write("{:.2f} ± {:.2f}\n".format(np.mean(symbolic_f1_scores), np.std(symbolic_f1_scores)))
        st.write("")
        st.write("**Casamento Exato:**")
        st.write("{:.2f} ± {:.2f}\n".format(np.mean(symbolic_em_scores), np.std(symbolic_em_scores)))
        st.write("")
        st.write("**Total de acertos:** {}".format(np.sum(symbolic_hit_scores)))
    with cols[1]:
        st.markdown("## **Usuário (Você)**")
        st.write("")
        st.markdown("**Pontuação F1:**")
        st.write("{:.2f} ± {:.2f}\n".format(np.mean(user_f1_scores), np.std(user_f1_scores)))
        st.write("")
        st.write("**Casamento Exato:**")
        st.write("{:.2f} ± {:.2f}\n".format(np.mean(user_em_scores), np.std(user_em_scores)))
        st.write("")
        st.write("**Total de acertos:** {}".format(np.sum(user_hit_scores)))
    with cols[2]:
        st.markdown("## **Modelo Neural (Bert)**")
        st.write("")
        st.markdown("**Pontuação F1:**")
        st.write("{:.2f} ± {:.2f}\n".format(np.mean(neural_f1_scores), np.std(neural_f1_scores)))
        st.write("")
        st.write("**Casamento Exato:**")
        st.write("{:.2f} ± {:.2f}\n".format(np.mean(neural_em_scores), np.std(neural_em_scores)))
        st.write("")
        st.write("**Total de acertos:** {}".format(np.sum(neural_hit_scores)))
    st.divider()

    # Page structure (second half)
    st.markdown("## Comparar respostas")
    for idx, question in enumerate(questions):
        st.markdown('### "{}"'.format(question))
        st.write("###")
        cols = st.columns(3)
        with cols[0]:
            st.markdown("## **Modelo Simbólico**")
            st.write(symbolic_answers[idx])
        with cols[1]:
            st.markdown("## **Usuário (Você)**")
            st.write(user_answers[idx])
        with cols[2]:
            st.markdown("## **Modelo Neural (Bert)**")
            st.write(neural_answers[idx])
        st.divider()

    # Clear game button
    with st.columns(5)[-1]:
        st.button("Novo jogo", on_click=_clear_game, use_container_width=True)