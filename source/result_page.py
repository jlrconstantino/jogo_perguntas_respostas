# General dependencies
import numpy as np
import streamlit as st

# Local dependencies
from source.available_pages import Pages
from source.answer_checker import check_answer_from_text
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
        "final_questions", 
        "final_answers"
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
    
    final_questions: list[str]
        List of the processed questions.
    
    final_answers: dict[str, list[str]]
        Answers of the agents for every one of the final questions. 
        The names of the agents are "user", "symbolic", "neural" 
        and "expected".
    '''
    # Process the results if not processed yet
    if "generated_results" not in st.session_state:

         # Gets the dataset and the answers
        dataset = st.session_state["dataset"]
        user_textual_answers = st.session_state["user_textual_answers"]
        symbolic_answers_dict, neural_answers_dict = load_outputs("./data/models_answers.csv")

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
            symbolic_answer = symbolic_answers_dict[title_idx, context_idx, question_idx]
            symbolic_answers.append(symbolic_answer)
            symbolic_f1_scores.append(compute_f1(symbolic_answer, ground_truth))
            symbolic_em_scores.append(exact_match(symbolic_answer, ground_truth))
            symbolic_hit_scores.append(check_answer_from_text(symbolic_answer, ground_truth))

            # Computes scores for the neural model
            neural_answer = neural_answers_dict[title_idx, context_idx, question_idx]
            neural_answers.append(neural_answer)
            neural_f1_scores.append(compute_f1(neural_answer, ground_truth))
            neural_em_scores.append(exact_match(neural_answer, ground_truth))
            neural_hit_scores.append(check_answer_from_text(neural_answer, ground_truth))

        # Loading everything to session state
        st.session_state["final_questions"] = questions
        st.session_state["final_answers"] = {
            "user": user_answers, 
            "symbolic": symbolic_answers, 
            "neural": neural_answers, 
            "expected": expected_answers
        }
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
        del dataset
        del user_textual_answers
        del questions
        del expected_answers
        del user_answers
        del symbolic_answers
        del neural_answers
        del user_f1_scores
        del user_em_scores
        del user_hit_scores
        del symbolic_f1_scores
        del symbolic_em_scores
        del symbolic_hit_scores
        del neural_f1_scores
        del neural_em_scores
        del neural_hit_scores
        del symbolic_answers_dict
        del neural_answers_dict

    # Loads everything necessary from session state
    questions = st.session_state["final_questions"]
    answers = st.session_state["final_answers"]
    scores = st.session_state["scores_results"]
    
    # Page structure (first half)
    st.title("**Resultados**")
    st.divider()
    cols = st.columns(3)

    # Symbolic results
    with cols[0]:
        st.markdown("## 🐌 **Modelo Simbólico**")
        st.markdown('''
            > **Pontuação F1:**
            >> {:.2f} ± {:.2f}

            > **Casamento Exato:**
            >> {:.2f} ± {:.2f}

            > **Total de acertos:**
            >> {}'''.format(*scores["f1_symbolic"], *scores["em_symbolic"], np.sum(scores["hit_symbolic"])))
        
    # User results
    with cols[1]:
        st.markdown("## 😄 **Usuário (Você)**")
        st.markdown('''
            > **Pontuação F1:**
            >> {:.2f} ± {:.2f}

            > **Casamento Exato:**
            >> {:.2f} ± {:.2f}

            > **Total de acertos:**
            >> {}'''.format(*scores["f1_user"], *scores["em_user"], np.sum(scores["hit_user"])))

    # Neural results
    with cols[2]:
        st.markdown("## 🦅 **Modelo Neural (Bert)**")
        st.markdown('''
            > **Pontuação F1:**
            >> {:.2f} ± {:.2f}

            > **Casamento Exato:**
            >> {:.2f} ± {:.2f}

            > **Total de acertos:**
            >> {}'''.format(*scores["f1_neural"], *scores["em_neural"], np.sum(scores["hit_neural"])))

    # Page structure (second half)
    st.divider()
    st.markdown("## Comparar respostas")

    # Question selection
    question_idx = st.selectbox(
        "Selecione uma questão:", 
        range(len(questions)), 
        format_func=lambda x: questions[x])
    
    # Expected answer display
    st.selectbox("Resposta esperada:", [answers["expected"][question_idx]])

    # Symbolic answer
    cols = st.columns(3)
    with cols[0]:
        st.markdown("## 🐌 **Modelo Simbólico**")
        _generate_status_message(scores["hit_symbolic"], question_idx)
        answer = answers["symbolic"][question_idx]
        st.write(answer if len(answer) > 0 else "...")
    
    # User answer
    with cols[1]:
        st.markdown("## 😄 **Usuário (Você)**")
        _generate_status_message(scores["hit_user"], question_idx)
        answer = answers["user"][question_idx]
        st.write(answer if len(answer) > 0 else "...")

    # Neural answer
    with cols[2]:
        st.markdown("## 🦅 **Modelo Neural (Bert)**")
        _generate_status_message(scores["hit_neural"], question_idx)
        answer = answers["neural"][question_idx]
        st.write(answer if len(answer) > 0 else "...")

    # Clear game button
    st.divider()
    with st.columns(5)[-1]:
        st.button("Novo jogo", on_click=_clear_game, use_container_width=True)