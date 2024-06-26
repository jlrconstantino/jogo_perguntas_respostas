# General dependencies
import streamlit as st

# Local dependencies
from source.pages.available_pages import Pages

def clear_game():
    ''' Clears the game '''

    # All states to clear
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
        "user_name", 
        "initial_time", 
        "end_time"
    ]

    # Clear every state
    for state in states_to_clear:
        if state in st.session_state:
            del st.session_state[state]

    # Go to home page
    st.session_state["current_page"] = Pages.HOME