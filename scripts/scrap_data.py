import requests
import time
import os
import json
from bs4 import BeautifulSoup

def lire_urls(chemin_fichier):
    """Lire les URL à partir d'un fichier texte."""
    with open(chemin_fichier, 'r') as fichier:
        # Retourne une liste des URL en supprimant les lignes vides
        return [ligne.strip() for ligne in fichier if ligne.strip()]

def scraper_links(url, niveau=0):
    """Récupérer tous les liens d'une page."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        # Effectue une requête HTTP pour obtenir le contenu de la page
        reponse = requests.get(url, headers=headers)
        reponse.raise_for_status()

        # Analyse le HTML de la page
        soupe = BeautifulSoup(reponse.text, 'html.parser')

        # Trouve tous les liens dans la page
        liens = soupe.find_all('a')

        # Extrait les URL complètes des liens
        urls = [lien['href'] for lien in liens]

        # Affiche les URLs récupérées avec leur niveau de récursion
        for url in urls:
            print(f"{niveau * '--'}{url}")

        # Retourne une liste d'URLs
        return urls
    except Exception as e:
        print(f"Échec du scraping pour {url} : {str(e)}")
        return []


def scraper_article(url):
    """Récupérer le titre, le contenu d'un article complet et la description."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        # Effectue une requête HTTP pour obtenir le contenu de la page
        reponse = requests.get(url, headers=headers)
        reponse.raise_for_status()

        # Analyse le HTML de la page
        soupe = BeautifulSoup(reponse.text, 'html.parser')

        # Trouve le titre de l'article
        balise_titre = soupe.find('title')
        titre = balise_titre.get_text(strip=True) if balise_titre else 'Titre non trouvé'

        # Trouve le contenu de l'article, en excluant la description
        balise_article = soupe.find('article')
        if balise_article:
            # Supprime les éléments de description potentiels du contenu de l'article
            for meta in balise_article.find_all('meta', attrs={'name': 'description'}):
                meta.decompose()

            # Collecte tous les paragraphes et les balises de titre dans le tag article
            contenu = '\n'.join([p.get_text(strip=True) for p in balise_article.find_all(['p', 'h2', 'h3', 'h4'])])
        else:
            contenu = 'Contenu de l\'article non trouvé'

        # Combine le titre et le contenu en un article complet
        article_complet = f"{titre}\n\n{contenu}"

        # Extrait la description séparément
        balise_description = soupe.find('meta', attrs={'name': 'description'})
        description = balise_description['content'] if balise_description else 'Aucune description trouvée'

        # Retourne un dictionnaire contenant l'URL, l'article complet et la description
        return {"id": url, "article": article_complet, "description": description}
    except Exception as e:
        print(f"Échec du scraping pour {url} : {str(e)}")
        return None

def ecrire_json(donnees, fichier_json):
    """Écrire la liste de dictionnaires dans un fichier JSON."""
    repertoire_sortie = os.path.dirname(fichier_json)
    # Crée le répertoire de sortie s'il n'existe pas
    if not os.path.exists(repertoire_sortie):
        os.makedirs(repertoire_sortie)

    # Ouvre le fichier JSON en mode écriture
    with open(fichier_json, 'w', encoding='utf-8') as fichier:
        json.dump(donnees, fichier, ensure_ascii=False, indent=4)

def principal():
    """Fonction principale pour scraper les articles et enregistrer les données dans un fichier JSON."""
    chemin_fichier = '../data/raw/url_leparisien.txt'  # Chemin vers le fichier contenant les URL
    fichier_json = '../data/clean/donnees_scrapees.json'  # Nom du fichier JSON de sortie

    urls = lire_urls(chemin_fichier)  # Lecture des URL depuis le fichier
    articles = []  # Liste pour stocker les articles
    failed_urls = []  # Liste pour stocker les URL échouées
    valid_urls = 0  # Compteur pour les URLs valides

    # Scraping de chaque URL
    for url in urls:
        if valid_urls >= 1000:  # Arrête le scraping une fois que nous avons 1000 URLs valides
            break
        links = scraper_links(url, niveau=1)  # Scraping des liens avec un niveau de récursion de 1
        for link in links:
            article = scraper_article(link)  # Scraping de l'article
            if article and len(article['article']) > len(article['description']):  # Vérifie si l'article est plus long que la description
                articles.append(article)  # Ajoute l'article à la liste
                valid_urls += 1  # Incrémente le compteur de URLs valides
            else:
                failed_urls.append(link)  # Ajoute l'URL à la liste des échecs
            time.sleep(0.1)  # Pause pour éviter de surcharger le serveur

    # Réessayer les URL échouées
    for url in failed_urls:
        if valid_urls >= 1000:  # Arrête le scraping une fois que nous avons 1000 URLs valides
            break
        article = scraper_article(url)  # Scraping de l'article
        if article and len(article['article']) > len(article['description']):  # Vérifie si l'article est plus long que la description
            articles.append(article)  # Ajoute l'article à la liste
            failed_urls.remove(url)  # Retire l'URL de la liste des échecs
            valid_urls += 1  # Incrémente le compteur de URLs valides
        time.sleep(0.1)  # Pause pour éviter de surcharger le serveur

    ecrire_json(articles, fichier_json)  # Écriture des articles dans un fichier JSON

    # Affichage des résultats
    with open(fichier_json, 'r', encoding='utf-8') as fichier:
        donnees = json.load(fichier)
        print(json.dumps(donnees, ensure_ascii=False, indent=4))

    # Affichage des URL échouées s'il y en a
    if failed_urls:
        print("Les URL suivantes ont échoué après deux tentatives :")
        for url in failed_urls:
            print(url)

# Exécution de la fonction principale si le script est exécuté directement
if __name__ == "__main__":
    principal()