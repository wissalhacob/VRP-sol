le résultat est visualiser dans le lien suivant :
https://wissalhacob.github.io/VRP-sol/VRP/Aide.html

# Moroccan TSP Competition

## Description
Dans le cadre de notre mission humanitaire à Al Haouz, touchée par un récent tremblement de terre, nous utilisons le problème de tournée de véhicules (VRP) pour concevoir des stratégies de distribution d'aide efficaces. Notre objectif est de répondre de manière optimale aux besoins uniques de chaque communauté touchée, en planifiant des itinéraires de livraison qui maximisent l'utilisation des ressources disponibles et respectent les délais critiques.

## Problématique
- Amélioration de l'accessibilité et de la couverture de la distribution d'aide dans les zones touchées.
- Conception d'itinéraires de distribution d'aide efficaces.
- Adaptation des stratégies de distribution en fonction des besoins spécifiques de chaque communauté affectée et des différentes contraintes des ressources.

## Objectifs
- Planifier des itinéraires de livraison pour plus de 360 villages de la province d'Al Haouz.
- Maximiser l'utilisation des ressources disponibles.
- Respecter les délais critiques et tenir compte des contraintes logistiques telles que les capacités des véhicules, les fenêtres de temps, l'horizon de planification, le nombre de dépôts, et les prévisions météorologiques.

## Méthodes et Outils Utilisés
- **API Google Maps** : Récupération de données cartographiques.
- **Geopy** : Calcul des distances.
- **Folium** : Visualisation cartographique.
- **Google Colab et VS Code** : Environnements de développement.
- **OR-Tools (Bibliothèque Python)** : Résolution d’une solution initiale.
- **Méthode 2-opt** : Amélioration de la solution initiale.

## Résultats
- Villages : 360
- Dépôts : 3
- Véhicules : 3 hélicoptères par dépôt avec des capacités et vitesses différentes
- Temps max de distribution : 3 jours
- Temps max de voyage : 2,5 heures

## Installation
Pour installer et configurer le projet localement, suivez ces étapes :

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/votre-utilisateur/nom-du-projet.git
   cd nom-du-projet
2.Installez les dépendances :

pip install -r requirements.txt
3.Configurez les variables d'environnement : Créez un fichier .env à la racine du projet et ajoutez les variables nécessaires :

GOOGLE_MAPS_API_KEY=your_api_key
4.Démarrez l'application :

python main.py
Utilisation
Pour utiliser le projet après l'installation :

1.Ouvrez votre navigateur et accédez à http://localhost:5000.
2.Configurez les paramètres de la mission humanitaire.
3.Visualisez et optimisez les itinéraires de distribution.

Contribution

Pour contribuer au projet :
1.Forkez le dépôt.
2.Créez une branche pour votre fonctionnalité (git checkout -b feature/ma-fonctionnalité).
3.Commitez vos modifications (git commit -m 'Ajout de ma fonctionnalité').
4.Poussez votre branche (git push origin feature/ma-fonctionnalité).
5.Ouvrez une Pull Request.
