"""
Module d'analyse textuelle et de visualisation des données d'articles.

Ce module effectue diverses analyses textuelles et visualisations sur des articles et leurs descriptions.
Il inclut des fonctions pour charger les données, compter les tokens, catégoriser les différences de tokens,
extraire les termes fréquents, et comparer les similarités cosines.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import nltk
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords

# Télécharger manuellement les stop words français
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('stopwords')

# Charger les données JSON
with open('../data/clean/donnees_scrapees.json', 'r', encoding='utf-8') as f:
    data = pd.read_json(f)

def count_tokens(text):
    """
    Compter les tokens (mots) dans un texte.

    Args:
        text (str): Texte à analyser.

    Returns:
        int: Nombre de tokens dans le texte.
    """
    return len(text.split())

# Ajouter des colonnes pour le nombre de tokens dans l'article et la description
data['article_tokens'] = data['article'].apply(count_tokens)
data['description_tokens'] = data['description'].apply(count_tokens)

# Calculer la différence de tokens
data['token_difference'] = data['article_tokens'] - data['description_tokens']

def categorize_difference(diff):
    """
    Catégoriser les articles selon la différence de tokens.

    Args:
        diff (int): Différence de tokens entre l'article et la description.

    Returns:
        str: Catégorie de la différence de tokens.
    """
    if diff > 50:
        return 'Grande différence'
    elif diff < -50:
        return 'Grande description'
    else:
        return 'Similaire'

data['category'] = data['token_difference'].apply(categorize_difference)

# Créer l'histogramme coloré avec annotations
plt.figure(figsize=(10, 6))
ax = sns.histplot(data=data, x='category', hue='category', palette={'Grande différence': 'red', 'Similaire': 'green', 'Grande description': 'blue'}, edgecolor='black', legend=False)

# Ajouter des annotations
for p in ax.patches:
    ax.annotate(f'{p.get_height()}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='baseline')

plt.title('Distribution des articles par différence de tokens')
plt.xlabel('Catégorie')
plt.ylabel('Nombre d\'articles')
plt.show()

# Calculer les moyennes des tokens pour les articles et les descriptions
mean_article_tokens = data['article_tokens'].mean()
mean_description_tokens = data['description_tokens'].mean()

# Créer un graphique en barres pour comparer les moyennes
plt.figure(figsize=(8, 6))
categories = ['Articles', 'Descriptions']
means = [mean_article_tokens, mean_description_tokens]
sns.barplot(x=categories, y=means, palette=['blue', 'orange'], legend=False)

# Ajouter des annotations pour les valeurs moyennes
for i, mean in enumerate(means):
    plt.text(i, mean + 10, f'{mean:.1f}', ha='center', va='bottom')

plt.title('Comparaison des moyennes de tokens entre articles et descriptions')
plt.xlabel('Catégorie')
plt.ylabel('Nombre moyen de tokens')
plt.ylim(0, max(means) + 50)
plt.show()

def get_top_n_words(corpus, n=None):
    """
    Extraire les termes fréquents d'un corpus.

    Args:
        corpus (list): Liste de textes à analyser.
        n (int, optional): Nombre de termes à retourner. Par défaut None.

    Returns:
        list: Liste de tuples contenant les termes et leur fréquence.
    """
    vec = CountVectorizer().fit(corpus)
    bag_of_words = vec.transform(corpus)
    sum_words = bag_of_words.sum(axis=0)
    words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
    words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
    return words_freq[:n]

# Top termes dans les articles et les descriptions
top_n = 20
top_words_article = get_top_n_words(data['article'], top_n)
top_words_description = get_top_n_words(data['description'], top_n)

# Filtrer les stop words français
stop_words_fr = set(stopwords.words('french'))
top_words_article_filtered = [(word, freq) for word, freq in top_words_article if word not in stop_words_fr]
top_words_description_filtered = [(word, freq) for word, freq in top_words_description if word not in stop_words_fr]

def ensure_min_words(filtered_words, original_words, min_words=10):
    """
    S'assurer qu'il y a au moins un certain nombre de mots dans la liste filtrée.

    Args:
        filtered_words (list): Liste de mots filtrés.
        original_words (list): Liste de mots originaux.
        min_words (int, optional): Nombre minimum de mots requis. Par défaut à 10.

    Returns:
        list: Liste de mots filtrés avec au moins min_words mots.
    """
    additional_words = [(word, freq) for word, freq in original_words if word not in stop_words_fr and word not in dict(filtered_words)]
    if len(filtered_words) < min_words:
        filtered_words.extend(additional_words[:min_words - len(filtered_words)])
    return filtered_words

top_words_article_filtered = ensure_min_words(top_words_article_filtered, top_words_article)
top_words_description_filtered = ensure_min_words(top_words_description_filtered, top_words_description)

# S'assurer que les deux listes sont de la même longueur
min_len = min(len(top_words_article_filtered), len(top_words_description_filtered))
top_words_article_filtered = top_words_article_filtered[:min_len]
top_words_description_filtered = top_words_description_filtered[:min_len]

# Créer un DataFrame pour les termes
df_top_words = pd.DataFrame({
    'Article': [word for word, freq in top_words_article_filtered],
    'Article_Freq': [freq for word, freq in top_words_article_filtered],
    'Description': [word for word, freq in top_words_description_filtered],
    'Description_Freq': [freq for word, freq in top_words_description_filtered]
})

# Créer un graphique en barres pour comparer les termes clés
plt.figure(figsize=(14, 8))

# Articles
plt.subplot(1, 2, 1)
sns.barplot(x='Article_Freq', y='Article', data=df_top_words, palette='Blues_d', hue='Article', dodge=False, legend=False)
plt.title('Top termes dans les articles')
plt.xlabel('Fréquence')

# Descriptions
plt.subplot(1, 2, 2)
sns.barplot(x='Description_Freq', y='Description', data=df_top_words, palette='Oranges_d', hue='Description', dodge=False, legend=False)
plt.title('Top termes dans les descriptions')
plt.xlabel('Fréquence')

plt.tight_layout()
plt.show()

# Niveau de réduction : Scatter Plot des longueurs des articles par rapport aux descriptions
plt.figure(figsize=(8, 6))
plt.scatter(data['article_tokens'], data['description_tokens'], alpha=0.5)
plt.xlabel('Nombre de tokens des articles')
plt.ylabel('Nombre de tokens des descriptions')
plt.title('Relation entre les longueurs des articles et des descriptions')
plt.show()

# Comparaison de Similarité
# Scatter Plot de Similarité Cosine
vectorizer = TfidfVectorizer().fit_transform(data['article'].tolist() + data['description'].tolist())
vectors = vectorizer[:len(data)], vectorizer[len(data):]
cosine_similarities = cosine_similarity(vectors[0], vectors[1])
cosine_similarities_diag = cosine_similarities.diagonal()

plt.figure(figsize=(8, 6))
sns.histplot(cosine_similarities_diag, kde=True, color='purple')
plt.title('Distribution des similarités cosines entre articles et descriptions')
plt.xlabel('Similarité Cosine')
plt.ylabel('Nombre d\'articles')
plt.show()

# Ajouter les similarités cosines au DataFrame
data['cosine_similarity'] = cosine_similarities_diag
