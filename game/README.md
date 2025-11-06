# Architecture du module `game`

Ce dossier contient tous les modules du jeu Pacman, organisés de manière modulaire et maintenable.

## Structure des modules

### 📋 `constants.py` (54 lignes)
Contient toutes les constantes du jeu :
- Dimensions et affichage (TILE, FPS, UI_OFFSET)
- Configuration gameplay (vitesses, durées des pouvoirs)
- Valeurs de points
- Couleurs RGB pour tous les éléments visuels

### 🔧 `utils.py` (94 lignes)
Fonctions utilitaires réutilisables :
- `resource_path()` : Gestion des chemins pour PyInstaller
- `get_ghost_points()` : Calcul des points selon les combos
- `wait_for_enter()` : Attente d'entrée utilisateur
- `wait_for_button_or_enter()` : Interaction avec les boutons
- `load_map_file()` : Chargement des cartes
- `format_time()` : Formatage du temps en MM:SS

### 🗺️ `level_manager.py` (96 lignes)
Gestion des niveaux et progression :
- `LevelManager` : Classe principale de gestion des niveaux
  - Charge les 3 niveaux statiques
  - Génère les niveaux procéduraux après
  - Gère la progression et la difficulté croissante
  - Augmente la vitesse des fantômes progressivement

### 📦 `game_state.py` (166 lignes)
État complet du jeu :
- `GameState` : Encapsule toutes les variables d'état
  - Carte et entités (Pacman, fantômes, pastilles)
  - Score et timers
  - Champ de vision
  - Méthodes de réinitialisation (`reset_round()`)
  - **Vérification de victoire corrigée** (`check_victory()`)

### 🎨 `renderer.py` (200 lignes)
Rendu visuel du jeu :
- `Renderer` : Classe de rendu avec toutes les polices
  - Dessine la carte et les murs
  - Affiche les collectibles (pastilles, super-pastilles)
  - Rend Pacman et les fantômes avec interpolation fluide
  - Applique le masque de champ de vision
  - Dessine l'interface utilisateur (niveau, score, temps)
  - Écrans de Game Over et Victoire

### 💥 `collision_manager.py` (85 lignes)
Gestion des collisions :
- `CollisionManager` : Méthodes statiques pour les collisions
  - Collision avec pastilles normales
  - Collision avec super-pastilles (activation des pouvoirs)
  - Collision avec fantômes (mort ou capture)
  - Système de combo pour les points

### 🔁 `game_loop.py` (266 lignes)
Boucle principale du jeu :
- `GameLoop` : Orchestre tous les composants
  - Initialisation de pygame et de tous les gestionnaires
  - Boucle principale à 60 FPS
  - Gestion des événements (touches, fermeture)
  - Mise à jour de Pacman (mouvement fluide)
  - Mise à jour des fantômes (IA)
  - Mise à jour des timers (pouvoirs, respawn)
  - Rétrécissement du champ de vision
  - Gestion des écrans de fin (Game Over, Victoire)

## Modules existants (non modifiés)

### `entities.py`
Classes des entités du jeu (Position, Pacman, Ghost, Pellet, PowerPellet)

### `map.py`
Gestion de la carte (GameMap, chargement, détection de murs)

### `score.py`
Gestion du score (classe Score)

### `map_generator.py`
Génération procédurale des cartes

### `menu.py`
Menu principal du jeu

### `settings.py`
Paramètres du jeu

### `hardcore.py`
Mode hardcore

## Point d'entrée

### `../main.py` (25 lignes)
Point d'entrée simplifié :
- Affiche le menu principal
- Lance la boucle de jeu (`GameLoop`)
- Gère le choix de l'utilisateur

## Améliorations apportées

✅ **Réparation du système de victoire** : La victoire est maintenant détectée correctement quand tous les points sont mangés (dots ET power_dots).

✅ **Modularité** : Chaque fichier a une responsabilité unique et claire.

✅ **Maintenabilité** : Maximum ~200 lignes par fichier (hors commentaires).

✅ **Commentaires préservés** : Tous les commentaires du code original ont été conservés et améliorés.

✅ **Séparation des responsabilités** :
- État du jeu séparé de la logique
- Rendu séparé de la boucle principale
- Collisions gérées dans un module dédié
- Niveaux gérés indépendamment

✅ **Code plus lisible** : Chaque module peut être compris indépendamment.

## Utilisation

```python
# Lancer le jeu
python3 main.py

# Le jeu se lance via le menu, puis :
# - GameLoop initialise tous les composants
# - LevelManager charge les niveaux
# - GameState maintient l'état
# - Renderer affiche tout
# - CollisionManager gère les interactions
```

## Raccourcis de débogage

- **P** : Force la victoire (vide toutes les pastilles)
- **ESC** : Quitter le jeu
- **Entrée** : Relancer après Game Over ou passer au niveau suivant

