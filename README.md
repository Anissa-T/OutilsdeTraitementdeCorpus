# 🌻 Outils de Traitement de Corpus 🌻 
👩🏾‍💻 Anissa Thezenas 👩🏾‍💻

📄 Je souhaites réaliser la tâche suivante : Natural Language Processing : Summarization 📄
# Dataset CNN/Daily Mail

Le dataset CNN/Daily Mail est une collection de grande envergure conçue pour la synthèse de texte et les tâches de questions-réponses, introduite à l'origine pour soutenir la compréhension de la lecture automatisée et la synthèse de texte. Il contient plus de 313 000 articles uniques issus des sites CNN et Daily Mail, avec des résumés ou des questions correspondantes pour tester la capacité des modèles.

## Caractéristiques principales

- **Structure** : Chaque donnée comprend un article et ses points forts ou un résumé correspondant, rédigé par des journalistes. Les premières versions anonymisaient les entités nommées, tandis que la version actuelle fournit les données brutes, non anonymisées.
  
- **Taille** : Le dataset offre 287 113 exemples d'entraînement, 13 368 paires de validation et 11 490 paires de test.

- **Objectif** : Conçu initialement pour des questions de type Cloze (les entités sont cachées dans les résumés et doivent être devinées par les modèles), il prend désormais en charge principalement la recherche en synthèse de texte.

## Considérations

- Le dataset contient des biais reflétant les perspectives américaines et britanniques en raison de ses origines médiatiques. Cependant, il est considéré comme moins biaisé que d'autres datasets similaires.
  
- Des difficultés d'évaluation manuelle, telles que les erreurs de coréférence, affectent la compréhension, nécessitant des modèles sophistiqués de synthèse.

## Ressources

- **Dataset sur Kaggle** : Accédez aux données et au code sur [Kaggle](https://www.kaggle.com/datasets/gowrishankarp/newspaper-text-summarization-cnn-dailymail).

- **Document original** : Pour plus d'informations sur sa conception et son utilisation, consultez le document de Nallapati et al. &#8203;``【oaicite:1】``&#8203;&#8203;``【oaicite:0】``&#8203;.

- ** → D'autres corpus existent dans d'autres langues, lesquels ?**
    Gigaword en français

##Le corpus## 
Il comporte les informations suivantes : id, title, article, highlights, summary
id : Un champ unique pour distinguer une suite d'information
title : Le titre de l'article de laquelle est extrait le contexte
article : Le texte complet de l'article
highlights : Les phrases importantes de l'article
summary : Le résumé de l'article généré à partir des phrases importantes
