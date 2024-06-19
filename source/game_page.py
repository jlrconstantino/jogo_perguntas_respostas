# General dependencies
import streamlit as st
from text_highlighter import text_highlighter

# Local dependencies
from source.answer_checker import check_answer_from_user_selections
from source.game_sidebar import generate_game_sidebar
from source.available_pages import Pages


def _go_to_previous_question():
    st.session_state["selected_topic_idx"], st.session_state["selected_paragraph_idx"], st.session_state["selected_question_idx"] = st.session_state["dataset"].get_previous_question_indexes(
        st.session_state["selected_topic"], 
        st.session_state["selected_paragraph_idx"], 
        st.session_state["selected_question_idx"])


def _go_to_next_question():
    st.session_state["selected_topic_idx"], st.session_state["selected_paragraph_idx"], st.session_state["selected_question_idx"] = st.session_state["dataset"].get_next_question_indexes(
        st.session_state["selected_topic"], 
        st.session_state["selected_paragraph_idx"], 
        st.session_state["selected_question_idx"])


def _finish_game():
    if len(st.session_state.user_answered) > 0:
        states_to_clear = [
            "selected_topic",
            "selected_topic_idx",
            "selected_paragraph_idx",
            "selected_question_idx",
        ]
        for state in states_to_clear:
            del st.session_state[state]
        st.session_state["current_page"] = Pages.RESULTS
    else:
        st.error("Nenhuma resposta foi submetida.")


def generate_game_page():
    '''
    Generates the page of the main game.

    Session state dependencies:
    --------------------------

    dataset: FaquadDataset
        The dataset for the QA Game.

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
    # Sidebar
    generate_game_sidebar()

    # Gets the variables from the session state
    dataset = st.session_state["dataset"]
    selected_topic = st.session_state["selected_topic"]
    selected_topic_idx = st.session_state["selected_topic_idx"]
    selected_paragraph_idx = st.session_state["selected_paragraph_idx"]
    selected_question_idx = st.session_state["selected_question_idx"]

    # Control flags
    user_answered: bool = st.session_state.user_answered[(
        selected_topic_idx, selected_paragraph_idx, selected_question_idx)]
    answer_submitted: bool = False

    # Title
    st.header("**Jogo de Perguntas e Respostas**")
    st.divider()

    # Body columns
    col1, col2 = st.columns([3, 2], gap="large")

    # First column
    with col1:

        # Context display
        st.write("Faça seleções no texto abaixo para gerar sua resposta.")
        st.text("")
        st.text("")
        st.write("**Contexto:**")
        user_selections = text_highlighter (
            dataset.get_context(selected_topic, selected_paragraph_idx), 
            labels = [("", "#b84e42")]
        )

    # Second column
    with col2:

        # Question display
        st.write("**Pergunta:**")
        st.write(dataset.get_question(selected_topic, selected_paragraph_idx, selected_question_idx))
        st.divider()
        
        # Answer display
        st.write("**Sua resposta:**")

        # If the user didn't answered yet
        if user_answered is False:
            if len(user_selections) > 0:
                for answer in sorted(user_selections, key=lambda x: x["start"]):
                    st.write(answer["text"])
            else:
                st.write("...")
        
        # If the user already answered
        else:
            user_selections = st.session_state.user_textual_answers[(
                selected_topic_idx, selected_paragraph_idx, selected_question_idx)]
            if len(user_selections) > 0:
                for answer in sorted(user_selections, key=lambda x: x["start"]):
                    st.write(answer["text"])
            else:
                st.write("...")

        # Visual divider between the answer and the buttons
        st.divider()

        # Columns for the two aligned buttons
        bcol1, bcol2, bcol3 = st.columns(3)

        # Button for going to previous question
        with bcol1: st.button("Questão anterior", on_click=_go_to_previous_question)

        # Button for answer checking
        with bcol2: answer_submitted = st.button("Submeter resposta", disabled=user_answered, type="primary")

        # Button for going to next question
        with bcol3: st.button("Próxima questão", on_click=_go_to_next_question)

    # Divider between sections
    st.divider()

    # Show only if given a new answer
    if answer_submitted is True and st.session_state.user_answered[(
            selected_topic_idx, selected_paragraph_idx, selected_question_idx
        )] is False:

        # Updates the answer control flag
        st.session_state.user_answered[(
            selected_topic_idx, selected_paragraph_idx, selected_question_idx
        )] = True

        # Updates the user textual answer
        st.session_state.user_textual_answers[(
            selected_topic_idx, selected_paragraph_idx, selected_question_idx
        )] = user_selections

        # Gets all available answers for the question
        question_answers = dataset.get_answers(selected_topic, selected_paragraph_idx, selected_question_idx)

        # Checks the current_answer
        correct = check_answer_from_user_selections(user_selections, question_answers)
        if correct is True:
            st.balloons()
            st.success("Respondido corretamente!")
            st.session_state.user_correct_answers[(
                selected_topic_idx, selected_paragraph_idx, selected_question_idx
            )] = True
        else:
            st.error("Respondido incorretamente (;-;)")
            st.session_state.user_correct_answers[(
                selected_topic_idx, selected_paragraph_idx, selected_question_idx
            )] = False
    
    # Show instead if already answered
    elif user_answered is True:
        if st.session_state.user_correct_answers[(
            selected_topic_idx, selected_paragraph_idx, selected_question_idx
        )] is True:
            st.success("Respondido corretamente!")
        else:
            st.error("Respondido incorretamente (;-;)")
    
    # Finish button
    st.write("###")
    with st.columns(5)[-1]: st.button("Finalizar Jogo", use_container_width=True, on_click=_finish_game)