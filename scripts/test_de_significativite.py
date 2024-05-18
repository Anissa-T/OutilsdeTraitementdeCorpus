import os
import spacy
import pandas as pd
import matplotlib.pyplot as plt

# Charger le modèle SpaCy pour le français
def load_spacy_model():
    try:
        nlp = spacy.load("fr_core_news_sm")
    except OSError:
        print("Le modèle SpaCy pour le français n'a pas pu être chargé.")
        nlp = None
    return nlp

# Tokenisation du texte en fonction de la langue (ici, uniquement en français)
def tokenize(nlp, text):
    if nlp:
        doc = nlp(text)
        return [token.text for token in doc]
    else:
        return []

# Charger le modèle SpaCy
nlp = load_spacy_model()

# Calculer la longueur moyenne des phrases par article
def average_sentence_length(data, nlp):
    avg_lengths = {}
    for _, row in data.iterrows():
        article_id = row["id"]
        text = row["article"]
        doc = nlp(text)
        total_sentences = len(list(doc.sents))
        total_words = len(text.split())
        avg_lengths[article_id] = total_words / total_sentences if total_sentences > 0 else 0
    return avg_lengths

# Vérifier et créer les répertoires s'ils n'existent pas
resultats_dirs = ["./results/CSV", "./results/IMAGES"]
for directory in resultats_dirs:
    if not os.path.exists(directory):
        os.makedirs(directory)
    else:
        print(f"Le répertoire '{directory}' existe déjà.")

# Charger les données
data = pd.read_csv("/Users/anissa/Documents/Anissa2/Master_TAL/OTC/OutilsdeTraitementdeCorpus/data/clean/donnees_scrapees.csv")  # Remplacer par le chemin correct vers votre fichier CSV
print("Les données ont été chargées avec succès.")

# Calculer et sauvegarder la longueur moyenne des phrases par article
avg_sentence_lengths = average_sentence_length(data, nlp)
avg_sentence_lengths_df = pd.DataFrame(avg_sentence_lengths.items(), columns=["Article ID", "Average Sentence Length"])
print(avg_sentence_lengths_df)  # Affichage des longueurs moyennes des phrases
avg_sentence_lengths_df.to_csv("./results/CSV/avg_sentence_lengths.csv", index=False)
print("La longueur moyenne des phrases par article a été calculée et enregistrée avec succès.")

# Tracer la distribution des longueurs moyennes des phrases par article
plt.hist(avg_sentence_lengths_df["Average Sentence Length"], bins=20, alpha=0.75)
plt.xlabel("Average Sentence Length")
plt.ylabel("Frequency")
plt.title("Distribution of Average Sentence Lengths per Article")
plt.savefig("./results/IMAGES/avg_sentence_lengths_distribution.png", facecolor="white", dpi=300)
plt.show()

print("La distribution des longueurs moyennes des phrases par article a été calculée et enregistrée avec succès.")
