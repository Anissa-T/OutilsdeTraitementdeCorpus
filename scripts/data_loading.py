"""
Module de chargement et de conversion des données d'articles JSON en DataFrame.

Ce module charge les données JSON générées par un script de scraping, vérifie leur structure,
les convertit en DataFrame, et enregistre les données dans un fichier CSV. Il charge également
un jeu de données de référence à l'aide de la librairie datasets de Huggingface.
"""

import pandas as pd
import json
from datasets import load_dataset

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
    Load articles data from a CSV file.
    
    Parameters:
    filepath (str): Path to the CSV file containing articles data.
    
    Returns:
    DataFrame: Loaded articles data.
    """
    return pd.read_csv(filepath)

def load_descriptions_data(filepath):
    """
    Load descriptions data from a CSV file.
    
    Parameters:
    filepath (str): Path to the CSV file containing descriptions data.
    
    Returns:
    DataFrame: Loaded descriptions data.
    """
    return pd.read_csv(filepath)