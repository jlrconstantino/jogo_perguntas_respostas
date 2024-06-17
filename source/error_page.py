# General dependencies
import streamlit as st

# Local dependencies
from source.available_pages import Pages

def _go_to_home_page():
    st.session_state["current_page"] = Pages.HOME

def generate_error_page():
    st.markdown("<h1 style='text-align: center;'>Algo deu errado (;-;)</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>Sentimos muito pelo inconveniente.</h2>", unsafe_allow_html=True)
    st.divider()
    with st.columns(5)[2]:
        st.button("Voltar à página principal", use_container_width=True, on_click=_go_to_home_page)