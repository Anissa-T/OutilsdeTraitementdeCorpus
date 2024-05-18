"""
Module de chargement et de conversion des données d'articles JSON en DataFrame. 

Ce module charge les données JSON générées par un script de scraping, vérifie leur structure,
les convertit en DataFrame, et enregistre les données dans un fichier CSV. Il charge également
un jeu de données de référence à l'aide de la librairie datasets de Huggingface.
pour finir le script permet de split le data set en train dev et test. 
"""

import pandas as pd
import json
from datasets import load_dataset
from sklearn.model_selection import train_test_split

# Chemin vers le fichier JSON
file_path = '../data/clean/donnees_scrapees.json'

# Charger les données JSON générées par le script scrap_data.py
with open(file_path, 'r', encoding='utf-8') as file:
    try:
        data = json.load(file)
    except json.JSONDecodeError as e:
        print(f"Erreur de décodage JSON: {e}")
        data = []

# Vérifier la structure des données JSON
if data and isinstance(data, list):
    df = pd.DataFrame(data)
    df["id"] = df.index
else:
    print("Les données JSON ne sont pas au format attendu.")
    df = pd.DataFrame()

# Afficher les premières lignes du DataFrame pour vérification
print(df.head(10))

# Enregistrer les données extraites dans un fichier CSV
output_path_json = '../data/clean/donnees_scrapees.csv'
df.to_csv(output_path_json, index=False, encoding='utf-8')
print(f"Données JSON enregistrées dans {output_path_json}")

# Charger un jeu de données de référence avec la librairie datasets de huggingface
dataset = load_dataset("cnn_dailymail", "3.0.0")
train_df = dataset['train'].to_pandas()

# Afficher les premières lignes du jeu de données de référence
print(train_df.head())

def load_articles_data(filepath):
    """
    Charge les données des articles à partir d'un fichier CSV.
    
    Parameters:
    filepath (str): Chemin vers le fichier CSV contenant les données des articles.
    
    Returns:
    DataFrame: Données des articles chargées.
    """
    return pd.read_csv(filepath)

def load_descriptions_data(filepath):
    """
    Charge les données des descriptions à partir d'un fichier CSV.
    
    Parameters:
    filepath (str): Chemin vers le fichier CSV contenant les données des descriptions.
    
    Returns:
    DataFrame: Données des descriptions chargées.
    """
    return pd.read_csv(filepath)

def split_dataset(df, test_size=0.2, dev_size=0.1, random_state=42):
    """
    Divise le dataset en ensembles d'entraînement, de test et de développement.
    
    Parameters:
    df (DataFrame): Le dataset à diviser.
    test_size (float): Proportion du dataset à inclure dans le jeu de test.
    dev_size (float): Proportion du dataset à inclure dans le jeu de développement (à partir des données d'entraînement).
    random_state (int): Graine aléatoire pour la reproductibilité.
    
    Returns:
    tuple: DataFrames pour les ensembles d'entraînement, de test et de développement.
    """
    train_df, test_df = train_test_split(df, test_size=test_size, random_state=random_state)
    train_df, dev_df = train_test_split(train_df, test_size=dev_size/(1-test_size), random_state=random_state)
    return train_df, test_df, dev_df

# Exemple d'utilisation de la fonction split_dataset
train_set, test_set, dev_set = split_dataset(df)

# Enregistrer les ensembles train, test et dev dans des fichiers CSV
train_set.to_csv('../data/clean/train_set.csv', index=False, encoding='utf-8')
test_set.to_csv('../data/clean/test_set.csv', index=False, encoding='utf-8')
dev_set.to_csv('../data/clean/dev_set.csv', index=False, encoding='utf-8')
print("Ensembles train, test et dev enregistrés dans les fichiers correspondants.")
