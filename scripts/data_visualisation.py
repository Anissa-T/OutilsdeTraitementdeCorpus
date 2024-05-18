"""
Module d'analyse et de visualisation des données textuelles.

Ce module effectue diverses analyses et visualisations sur des articles et leurs descriptions.
Il inclut des fonctions pour compter les tokens, catégoriser les différences de tokens, 
extraire les termes fréquents, et comparer les similarités cosines.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import nltk
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from sklearn.metrics import precision_score, recall_score, f1_score

# Télécharger les stop words français
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('stopwords')

# Charger les données JSON
data = pd.read_json('../data/clean/donnees_scrapees.json')

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

# Ajouter des colonnes pour la taille des textes
data['article_length'] = data['article'].str.len()
data['description_length'] = data['description'].str.len()

# Calculer le ratio de compression
data['compression_ratio'] = data['description_length'] / data['article_length']

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

# Distribution des articles par différence de tokens
plt.figure(figsize=(10, 6))
ax = sns.histplot(data=data, x='category', hue='category', palette={'Grande différence': 'red', 'Similaire': 'green', 'Grande description': 'blue'}, edgecolor='black', legend=False)

for p in ax.patches:
    ax.annotate(f'{p.get_height()}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='baseline')

plt.title('Distribution des articles par différence de tokens')
plt.xlabel('Catégorie')
plt.ylabel('Nombre d\'articles')
plt.show()

# Comparaison des moyennes de tokens entre articles et descriptions
mean_article_tokens = data['article_tokens'].mean()
mean_description_tokens = data['description_tokens'].mean()

plt.figure(figsize=(8, 6))
categories = ['Articles', 'Descriptions']
means = [mean_article_tokens, mean_description_tokens]
sns.barplot(x=categories, y=means, palette=['blue', 'orange'], legend=False)

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

# Comparaison des termes clés
plt.figure(figsize=(14, 8))

plt.subplot(1, 2, 1)
sns.barplot(x='Article_Freq', y='Article', data=df_top_words, palette='Blues_d', hue='Article', dodge=False, legend=False)
plt.title('Top termes dans les articles')
plt.xlabel('Fréquence')

plt.subplot(1, 2, 2)
sns.barplot(x='Description_Freq', y='Description', data=df_top_words, palette='Oranges_d', hue='Description', dodge=False, legend=False)
plt.title('Top termes dans les descriptions')
plt.xlabel('Fréquence')

plt.tight_layout()
plt.show()

# Relation entre les longueurs des articles et des descriptions
plt.figure(figsize=(8, 6))
plt.scatter(data['article_tokens'], data['description_tokens'], alpha=0.5)
plt.xlabel('Nombre de tokens des articles')
plt.ylabel('Nombre de tokens des descriptions')
plt.title('Relation entre les longueurs des articles et des descriptions')
plt.show()

# Comparaison de Similarité Cosine
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

# Scatter Plot des similarités cosines par rapport aux différences de tokens
plt.figure(figsize=(8, 6))
plt.scatter(data['token_difference'], data['cosine_similarity'], alpha=0.5)
plt.xlabel('Différence de tokens')
plt.ylabel('Similarité Cosine')
plt.title('Similarité Cosine vs Différence de Tokens')
plt.show()

# Heatmap de corrélation
plt.figure(figsize=(10, 8))
corr_matrix = data[['article_tokens', 'description_tokens', 'token_difference', 'cosine_similarity', 'article_length', 'description_length', 'compression_ratio']].corr()
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
plt.title('Heatmap des corrélations')
plt.show()

# Sauvegarder le DataFrame avec les nouvelles colonnes
data.to_csv('../data/clean/donnees_analysees.csv', index=False)

def get_word_frequencies(corpus):
    """
    Calculer les fréquences des mots dans un corpus.

    Args:
        corpus (list): Liste de textes à analyser.

    Returns:
        dict: Dictionnaire des fréquences des mots.
    """
    vec = CountVectorizer().fit(corpus)
    bag_of_words = vec.transform(corpus)
    sum_words = bag_of_words.sum(axis=0)
    words_freq = {word: sum_words[0, idx] for word, idx in vec.vocabulary_.items()}
    words_freq = sorted(words_freq.items(), key=lambda x: x[1], reverse=True)
    return words_freq

# Calculer les fréquences des mots dans les articles
word_frequencies_article = get_word_frequencies(data['article'])

# Calculer le rang de chaque mot
ranks = {word: i for i, (word, _) in enumerate(word_frequencies_article, 1)}

# Tracer la loi de Zipf
plt.figure(figsize=(10, 6))
plt.loglog(
    list(ranks.values()),
    [freq for word, freq in word_frequencies_article if word in ranks],
    alpha=.5,
)
plt.title('Loi de Zipf')
plt.xlabel('Rang du mot')
plt.ylabel('Fréquence du mot')
plt.show()

# Définir le seuil de similarité cosine
threshold = 0.5

# Créer une liste de prédictions binaires (1 si la similarité cosine est supérieure au seuil, 0 sinon)
predictions = [1 if cosine_similarity > threshold else 0 for cosine_similarity in data['cosine_similarity']]

# Créer une liste de valeurs binaires réelles (1 si la catégorie est 'Similaire', 0 sinon)
real_values = [1 if category == 'Similaire' else 0 for category in data['category']]

# Calculer la précision
precision = precision_score(real_values, predictions)
print(f'Précision : {precision:.2f}')

# Calculer le rappel
recall = recall_score(real_values, predictions)
print(f'Rappel : {recall:.2f}')

# Calculer la F-mesure
f1 = f1_score(real_values, predictions)
print(f'F-mesure : {f1:.2f}')
