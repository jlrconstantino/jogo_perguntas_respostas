# General dependencies
import numpy as np
import streamlit as st
from collections import defaultdict

def _reset_question_and_paragraph():
    st.session_state["selected_paragraph_idx"] = 0
    st.session_state["selected_question_idx"] = 0

def _reset_question():
    st.session_state["selected_question_idx"] = 0

def generate_game_sidebar():
    ''' 
    Generates the sidebar for the QA Game.

    Session state dependencies:
    --------------------------

    dataset: FaquadDataset
        The dataset for the QA Game.
    
    Session state outputs:
    ---------------------

    selected_topic: str
        The name of the topic selected by the user.
    
    selected_topic_idx: int
        The index of the topic being selected.
    
    selected_paragraph_idx: int
        The index of the paragraph selected by the user.
    
    selected_question_idx: int
        The index of the question selected by the user.
    
    user_answered: dict[tuple[int,int,int], bool]
        Indicates, for a tuple of indexes of a topic, a paragraph and 
        a question, if the user already answered the question.
    
    user_correct_answers: dict[tuple[int,int,int], bool]
        Indicates, for a tuple of indexes of a topic, a paragraph and 
        a question, if the user correctly answered the question.
    
    user_textual_answers: dict[tuple[int,int,int], list[str]]
        Indicates, for a tuple of indexes of a topic, a paragraph and 
        a question, the textual answer of the user.
    '''
    # Gets the dataset stored in the session state
    dataset = st.session_state.dataset

    # Generates the dict of answers if it does not exist yey
    if "user_answered" not in st.session_state:
        st.session_state["user_answered"] = defaultdict(bool)
    if "user_correct_answers" not in st.session_state:
        st.session_state["user_correct_answers"] = defaultdict(bool)
    if "user_textual_answers" not in st.session_state:
        st.session_state["user_textual_answers"] = defaultdict(list)
    
    # Sidebar: title
    st.sidebar.title("Seleção de Sessão")

    # Topics
    topics = dataset.titles
    topics_indexes = list(range(len(topics)))
    if "selected_topic" not in st.session_state: st.session_state["selected_topic"] = topics[0]
    if "selected_topic_idx" not in st.session_state: st.session_state["selected_topic_idx"] = 0

    # Sidebar: topic selection
    st.session_state["selected_topic_idx"] = st.sidebar.selectbox (
        "Selecione um tópico:", 
        topics_indexes, 
        format_func=lambda x: topics[x], 
        index=st.session_state["selected_topic_idx"], 
        on_change=_reset_question_and_paragraph)
    
    # Name of the topic
    st.session_state["selected_topic"] = topics[st.session_state["selected_topic_idx"]]

    # Paragraphs (contexts)
    paragraph_previews: list[str] = dataset.get_paragraphs_previews(st.session_state["selected_topic"])
    paragraph_indexes = list(range(len(paragraph_previews)))
    if "selected_paragraph_idx" not in st.session_state: st.session_state["selected_paragraph_idx"] = 0

    # Sidebar: context selection
    st.session_state["selected_paragraph_idx"] = st.sidebar.selectbox (
        "Selecione um contexto:", 
        paragraph_indexes, 
        format_func=lambda x: paragraph_previews[x], 
        index=st.session_state["selected_paragraph_idx"], 
        on_change=_reset_question)
    
    # Questions
    questions_previews: list[str] = dataset.get_questions_previews(st.session_state["selected_topic"], st.session_state["selected_paragraph_idx"])
    questions_indexes = list(range(len(questions_previews)))
    if "selected_question_idx" not in st.session_state: st.session_state["selected_question_idx"] = 0

    # Sidebar: question selection
    st.session_state["selected_question_idx"] = st.sidebar.selectbox (
        "Selecione uma pergunta:", 
        questions_indexes, 
        format_func=lambda x: questions_previews[x], 
        index=st.session_state["selected_question_idx"])
    
    # User performance data
    user_answers = np.array(list(st.session_state["user_correct_answers"].values()))
    num_correct_answers = user_answers.sum()
    num_incorrect_answers = len(user_answers) - num_correct_answers

    # User performance display
    if len(user_answers) > 0:
        with st.sidebar:
            st.divider()
            st.title("Pontuação Atual")
            st.write("Acertos: {}".format(num_correct_answers))
            st.write("Erros: {}".format(num_incorrect_answers))