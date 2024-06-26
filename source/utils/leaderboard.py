# Dependencies
import os
import pandas as pd

# Constants
ORIGINAL_LEADERBOARD_PATH = "./data/original_leaderboard.csv"
GAME_LEADERBOARD_PATH = "./data/game_leaderboard.csv"

def load_leaderboard() -> pd.DataFrame:
    ''' Loads and returns the leaderboard. '''

    # Reads the game leaderboard
    if os.path.exists(GAME_LEADERBOARD_PATH):
        df = pd.read_csv(GAME_LEADERBOARD_PATH)

    # Reads the original leaderboard
    else:
        df = pd.read_csv(ORIGINAL_LEADERBOARD_PATH)
    
    # Sorts the values
    df = df.sort_values([
        "Total de Respostas", 
        "Total de Acertos", 
        "Pontuação F1 Média", 
        "Casamento Exato Médio", 
        "Tempo Gasto (segundos)"], ascending=False).reset_index().drop(axis=1, labels="index")

    # Returns the DataFrame
    return df

def save_leaderboard(df: pd.DataFrame) -> None:
    ''' Saves the given leaderboard. '''
    df.to_csv(GAME_LEADERBOARD_PATH, index=False)

def add_row_to_leaderboard(df: pd.DataFrame, user: str, tr: int, ta: int, f1: float, em: float, time: float) -> pd.DataFrame:
    ''' Adds a row to the leaderboard '''
    df.loc[len(df)] = [user, tr, ta, "{:.2f}".format(f1), "{:.2f}".format(em), time]
    return df