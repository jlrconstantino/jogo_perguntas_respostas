#!/usr/bin/env python
# coding: utf-8

#Importing libs
import os
import re
import json
import nltk
import numpy as np
from nltk.tree import ParentedTree
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sentence_splitter import SentenceSplitter

from source.models.metrics import compute_f1, exact_match

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')


## Funções auxiliares
def read_data(path):
    with open(path, 'rb') as f:
        faquad = json.load(f)

    contexts = []
    questions = []
    answers = []

    for group in faquad['data']:
        for passage in group['paragraphs']:
            context = passage['context']
            for qa in passage['qas']:
                question = qa['question']
            for answer in qa['answers']:
                contexts.append(context)
                questions.append(question)
                answers.append(answer)

    return contexts, questions, answers


def save_as_txt(text, path):
    """
    Save a text(format: string) in .txt file in path(format:string) required.
    """
    f = open(path, "w", encoding='utf-8')
    f.write(text)
    f.close()


def extract_sentences(tree_list):
    sentences = []

    for tree_string in tree_list:
        # Crie uma árvore sintática a partir da string
        tree = ParentedTree.fromstring(tree_string)
        # Percorre cada sentença (S) da árvore
        for subtree in tree.subtrees():
            if subtree.label() == 'S':
                # Percorre os filhos diretos da sentença
                for child in subtree:
                    test_sentence = subtree
                    if (isinstance(child, nltk.Tree)) & (child.label() != "S") & (test_sentence not in sentences): #Se o filho do nó é uma arvore
                        sentences.append(test_sentence)
    return sentences


def extract_phrases(tree):
    phrases = {'S': [' '.join(tree.leaves())], 'NP': [], 'PP': [], 'VP': []}

    # Percorre cada sentença (S) da árvore
    for subtree in tree.subtrees():
        if subtree.label() == 'S':
            # Percorre os filhos diretos da sentença
            for child in subtree:
                if isinstance(child, nltk.Tree):
                    if child.label() in phrases.keys():
                        phrases[child.label()].append(' '.join(child.leaves()))    
    return phrases


def tokenize_text(text):
    # 1. Converter texto para minúsculas
    text = text.lower()
    
    # 2. Remover caracteres não alfanuméricos (exceto espaço)
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    
    # 3. Tokenização: Dividir texto em palavras (tokens)
    tokens = word_tokenize(text)
    
    # 4. Remoção de stopwords (palavras comuns que não agregam muito significado)
    stop_words = set(stopwords.words('portuguese'))
    tokens = [word for word in tokens if word not in stop_words]
    
    # 5. Lematização ou Stemming (redução de palavras às suas formas básicas)
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    
    return tokens

def preprocess_context(text, splitter):
    
    # Pre tokenizando em frases
    text_splitted = splitter.split(text=text.replace("(", "").replace(")", ""))
    
    if text_splitted == text:
        context = "\n".join(text.split(','))
    else:
        context = "\n".join(text_splitted)
    path = "text_sentences.txt"
    save_as_txt(context, path)
    
    # Fazendo analise sintatica
    os.system(f"java -Xmx500m -cp stanford-parser-2010-11-30/stanford-parser.jar edu.stanford.nlp.parser.lexparser.LexicalizedParser -tokenized -sentences newline -outputFormat oneline -uwModel edu.stanford.nlp.parser.lexparser.BaseUnknownWordModel cintil.ser/cintil.ser text_sentences.txt > text_sintax_.txt;")
    f = open('text_sintax_.txt', "r")
    tree_context = f.read()
    f.close()
    tree_list = tree_context.split("\n")
    tree_list = [tree for tree in tree_list if tree != '']
    
    # Utilizando a separacao sintatica para extrair as frases finais
    sentences = extract_sentences(tree_list)

    # Extraindo os sintagmas das frases finais
    final = {}
    for sentence in range(len(sentences)):
        final[sentence] = extract_phrases(sentences[sentence])
    
    # Removendo arquivos temporarios
    os.remove("text_sentences.txt")
    os.remove("text_sintax_.txt")
    
    return final

def symbolic_model(text, question, splitter):
    response = ""
    try:
        # Preprocessando dados
        preprocess_question = tokenize_text(question)
        final_sentences = preprocess_context(text, splitter=splitter)

        max_contador = 0
        for num_sentence in final_sentences:
            if len(final_sentences[num_sentence]['S']) == 1:
                sentence = final_sentences[num_sentence]['S'][0]
                contexto = tokenize_text(sentence)
                contador = 0
                for token in preprocess_question:
                    if token in contexto:
                        contador += 1
                if contador >= max_contador:
                    max_contador = contador
                    response = sentence
        return response
    except Exception as e:
        print(e)
        return response


def question_answer(context, question, answer, splitter):
    try:
        prediction = symbolic_model(context, question, splitter=splitter)
    except:
        prediction = ""
    em_score = exact_match(prediction, answer)
    f1_score = compute_f1(prediction, answer)
    return em_score, f1_score


if __name__ == "__main__":
    ### Download FAQUAD
    with open('data/train.json', 'rb') as f:
        faquad = json.load(f)

    ## Separação dos dados para treino e validação
    train_contexts, train_questions, train_answers = read_data('data/train.json')
    valid_contexts, valid_questions, valid_answers = read_data('data/dev.json')

    train_length = len(train_contexts)
    valid_length = len(valid_questions)   

    print(f'Há {train_length} perguntas no treino')
    print(f'Há {valid_length} perguntas na validação')

    splitter = SentenceSplitter(language='pt')

    # for train_q_num in range(train_length):
    #     context = train_contexts[train_q_num]
    #     question = train_questions[train_q_num]
    #     answer = train_answers[train_q_num]['text']
    #     model_response = Simbolic_model(context, question, splitter=splitter)
        
    #     print("\nContexto: ", context)
    #     print("\nPergunta: ", question)
    #     print("\nResposta: ", answer)
    #     print("\nResposta do modelo: ", model_response)


    answers = [i['text'] for i in valid_answers]

    em_score_results = []
    f1_score_results = []
    for context, question, answer in zip(valid_contexts, valid_questions, answers):
        em_score, f1_score = question_answer(context, question, answer, splitter=splitter)
        em_score_results.append(em_score)
        f1_score_results.append(f1_score)

    print(f"Exact match: {np.asarray(em_score_results).mean()}")
    print(f"F1 score: {np.asarray(f1_score_results).mean()}")
