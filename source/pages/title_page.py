# General dependencies
import streamlit as st

# Local dependencies
from source.pages.available_pages import Pages

def _go_to_game_page():
    st.session_state["current_page"] = Pages.GAME

def _go_to_leaderboard():
    st.session_state["current_page"] = Pages.LEADERBOARD

def _go_to_credits():
    st.session_state["current_page"] = Pages.CREDITS

def generate_title_page():
    '''
    Generates the title page.

    Session state outputs:
    ---------------------

    user_name: str
        The name chosen by the user.
    '''

    # Title and its divider
    st.markdown("<h1 style='text-align: center;'>Jogo de Perguntas e Respostas</h1>", unsafe_allow_html=True)
    st.divider()

    # Centered session
    with st.columns(5)[2]:

        # User name selection
        st.session_state["user_name"] = st.text_input("Escolha um nome de usuário:", "Convidado", max_chars=32)

        # Start game button
        st.button("Iniciar novo jogo", use_container_width=True, on_click=_go_to_game_page, type="primary")

        # Go to leaderboard button
        st.button("Placar de líderes", use_container_width=True, on_click=_go_to_leaderboard)

        # Go to credits button
        st.button("Créditos", use_container_width=True, on_click=_go_to_credits)