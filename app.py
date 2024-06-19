# General dependencies
import streamlit as st

# Local dependencies
from source.load_dataset import load_dataset, FAQUAD_TEST_PATH
from source.title_page import generate_title_page
from source.game_page import generate_game_page
from source.result_page import generate_results_page
from source.error_page import generate_error_page
from source.available_pages import Pages

# Page config
st.set_page_config(
    page_title="Perguntas e Respostas",
    page_icon="🦜",
    layout="wide"
)

# Loads the dataset
load_dataset(FAQUAD_TEST_PATH)

# Defines the current page as the title page if needed
if "current_page" not in st.session_state:
    st.session_state["current_page"] = Pages.HOME

# Loads the title page
if st.session_state["current_page"] == Pages.HOME: 
    with st.spinner("Aguarde por favor..."): generate_title_page()

# Loads the page of the main game
elif st.session_state["current_page"] == Pages.GAME: 
    with st.spinner("Aguarde por favor..."): generate_game_page()

# Loads the page of results
elif st.session_state["current_page"] == Pages.RESULTS:
    with st.spinner("Aguarde por favor..."): generate_results_page()

# Loads the error page
else: generate_error_page()