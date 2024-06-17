# General dependencies
import streamlit as st

# Local dependencies
from source.available_pages import Pages

def _go_to_game_page():
    st.session_state["current_page"] = Pages.GAME

def generate_title_page():
    '''
    Generates the title page.
    '''
    st.markdown("<h1 style='text-align: center;'>Jogo de Perguntas e Respostas</h1>", unsafe_allow_html=True)
    st.divider()
    with st.columns(5)[2]:
        st.button("Iniciar novo jogo", use_container_width=True, on_click=_go_to_game_page)