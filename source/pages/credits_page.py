# General dependencies
import streamlit as st

# Local dependencies
from source.pages.available_pages import Pages

def _go_to_home_page():
    st.session_state["current_page"] = Pages.HOME

def generate_credits_page() -> None:

    # Title
    st.title("Créditos")
    st.divider()

    # Credits
    cols = st.columns(3)
    with cols[0]:
        st.markdown("## **Gian Lucca Albolea Basso**")
        st.write("Usando exércitos de Stanford, fez do Caracol nosso opositor.")
        st.image("./img/caracol.jfif")
    with cols[1]:
        st.markdown("## **João Lucas Rodrigues Constantino**")
        st.write("Das bibliotecas de Streamlit, elaborou este Jogo dos Tronos.")
        st.image("./img/bibliotecario.jfif")
    with cols[2]:
        st.markdown("## **Davi Alves Bezerra**")
        st.write("Em nome de BERTimbau, deu vida ao nosso Rei e ao seu legado.")
        st.image("./img/bert.jfif")

    # Return to title button
    st.divider()
    cols = st.columns(5)
    with cols[0]: st.write("Fonte das imagens: geradas pela inteligência artificial do Copilot Designer. Por sua vez, os prompts foram criados por João Lucas.")
    with cols[-1]: st.button("Voltar à tela inicial", use_container_width=True, on_click=_go_to_home_page)