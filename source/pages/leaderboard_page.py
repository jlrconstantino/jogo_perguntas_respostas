# General dependencies
import streamlit as st

# Local dependencies
from source.pages.available_pages import Pages
from source.utils.leaderboard import load_leaderboard

def _go_to_home_page():
    st.session_state["current_page"] = Pages.HOME

def generate_leaderboard_page() -> None:

    # Title
    st.title("Placar de Líderes")
    st.divider()

    # Prints data
    data = load_leaderboard()
    st.dataframe(data, use_container_width=True)
    st.divider()

    # Return to title button
    with st.columns(5)[-1]: 
        st.button("Voltar à tela inicial", use_container_width=True, on_click=_go_to_home_page)