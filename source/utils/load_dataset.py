# General dependencies
import streamlit as st

# Local dependencies
from source.faquad import FaquadDataset

# Path for the FaQuAD dataset .json files
FAQUAD_DATASET_PATH = "./data/dataset.json"
FAQUAD_TRAIN_PATH = "./data/train.json"
FAQUAD_TEST_PATH = "./data/dev.json"

def load_dataset(path: str) -> FaquadDataset:
    '''
    Function to load the dataset for the QA Game.

    Parameters:
    ----------

    path: str
        The path to the .json file to be loaded.

    Session state outputs:
    ---------------------

    dataset: FaquadDataset
        Entry of the dataset itself.
    '''
    if "dataset" in st.session_state:
        dataset = st.session_state["dataset"]
    else:
        dataset = FaquadDataset(path)
        st.session_state["dataset"] = dataset