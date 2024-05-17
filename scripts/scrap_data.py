"""
Module de scraping pour récupérer des articles à partir de liens URL.

Ce module contient des fonctions pour lire des URL à partir d'un fichier,
scraper des liens et des articles, et écrire les résultats dans un fichier JSON.
"""

import requests
import time
import os
import json
from bs4 import BeautifulSoup

def lire_urls(chemin_fichier):
    """
    Lire les URL à partir d'un fichier texte.

    Args:
        chemin_fichier (str): Chemin du fichier contenant les URL.

    Returns:
        list: Liste des URL lues à partir du fichier.
    """
    with open(chemin_fichier, 'r') as fichier:
        return [ligne.strip() for ligne in fichier if ligne.strip()]

def scraper_links(url, niveau=0):
    """
    Récupérer tous les liens d'une page.

    Args:
        url (str): URL de la page à scraper.
        niveau (int, optional): Niveau de récursion pour l'affichage. Par défaut à 0.

    Returns:
        list: Liste des URL trouvées sur la page.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        reponse = requests.get(url, headers=headers)
        reponse.raise_for_status()

        soupe = BeautifulSoup(reponse.text, 'html.parser')
        liens = soupe.find_all('a')
        urls = [lien['href'] for lien in liens]

        for url in urls:
            print(f"{niveau * '--'}{url}")

        return urls
    except Exception as e:
        print(f"Échec du scraping pour {url} : {str(e)}")
        return []

def scraper_article(url):
    """
    Récupérer le titre, le contenu d'un article complet et la description.

    Args:
        url (str): URL de l'article à scraper.

    Returns:
        dict: Dictionnaire contenant l'URL, l'article complet et la description.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        reponse = requests.get(url, headers=headers)
        reponse.raise_for_status()

        soupe = BeautifulSoup(reponse.text, 'html.parser')
        balise_titre = soupe.find('title')
        titre = balise_titre.get_text(strip=True) if balise_titre else 'Titre non trouvé'

        balise_article = soupe.find('article')
        if balise_article:
            for meta in balise_article.find_all('meta', attrs={'name': 'description'}):
                meta.decompose()
            contenu = '\n'.join([p.get_text(strip=True) for p in balise_article.find_all(['p', 'h2', 'h3', 'h4'])])
        else:
            contenu = 'Contenu de l\'article non trouvé'

        article_complet = f"{titre}\n\n{contenu}"
        balise_description = soupe.find('meta', attrs={'name': 'description'})
        description = balise_description['content'] if balise_description else 'Aucune description trouvée'

        return {"id": url, "article": article_complet, "description": description}
    except Exception as e:
        print(f"Échec du scraping pour {url} : {str(e)}")
        return None

def ecrire_json(donnees, fichier_json):
    """
    Écrire la liste de dictionnaires dans un fichier JSON.

    Args:
        donnees (list): Liste de dictionnaires à écrire dans le fichier JSON.
        fichier_json (str): Chemin du fichier JSON de sortie.
    """
    repertoire_sortie = os.path.dirname(fichier_json)
    if not os.path.exists(repertoire_sortie):
        os.makedirs(repertoire_sortie)

    with open(fichier_json, 'w', encoding='utf-8') as fichier:
        json.dump(donnees, fichier, ensure_ascii=False, indent=4)

def principal():
    """
    Fonction principale pour scraper les articles et enregistrer les données dans un fichier JSON.

    Lit les URL à partir d'un fichier texte, scrape les articles et les liens, 
    et écrit les résultats dans un fichier JSON. Affiche également les URL échouées.
    """
    chemin_fichier = '../data/raw/url_leparisien.txt'
    fichier_json = '../data/clean/donnees_scrapees.json'

    urls = lire_urls(chemin_fichier)
    articles = []
    failed_urls = []
    valid_urls = 0

    for url in urls:
        if valid_urls >= 1000:
            break
        links = scraper_links(url, niveau=1)
        for link in links:
            article = scraper_article(link)
            if article and len(article['article']) > len(article['description']):
                articles.append(article)
                valid_urls += 1
            else:
                failed_urls.append(link)
            time.sleep(0.1)

    for url in failed_urls:
        if valid_urls >= 1000:
            break
        article = scraper_article(url)
        if article and len(article['article']) > len(article['description']):
            articles.append(article)
            failed_urls.remove(url)
            valid_urls += 1
        time.sleep(0.1)

    ecrire_json(articles, fichier_json)

    with open(fichier_json, 'r', encoding='utf-8') as fichier:
        donnees = json.load(fichier)
        print(json.dumps(donnees, ensure_ascii=False, indent=4))

    if failed_urls:
        print("Les URL suivantes ont échoué après deux tentatives :")
        for url in failed_urls:
            print(url)

if __name__ == "__main__":
    principal()
