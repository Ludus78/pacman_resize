# 🎮 Pacman - Version Refactorisée

Projet de jeu Pacman avec Python et Pygame. **Entièrement refactorisé** avec une architecture modulaire professionnelle.

> ✨ **Dernière mise à jour** : Refactorisation complète (Nov 2025)  
> 📦 **Version** : 2.0 - Architecture modulaire  
> 🐛 **Bugs connus** : Aucun !

## Installation et setup

- Prérequis: Python 3.8+
- Windows: `pip install windows-curses`
- Linux/macOS: `curses` est inclus avec Python

```bash
python -m venv .venv
# Windows
. .venv\\Scripts\\activate
pip install -r requirements.txt
# Linux/macOS
source .venv/bin/activate
pip install -r requirements.txt
```

## 🚀 Démarrage Rapide

```bash
# Lancer le jeu
python3 main.py
```

Pour plus de détails, consultez le **[Guide de Démarrage](GUIDE_DEMARRAGE.md)**.

## 📖 Documentation

- **[GUIDE_DEMARRAGE.md](GUIDE_DEMARRAGE.md)** - Comment jouer (contrôles, règles, stratégies)
- **[REFACTORING.md](REFACTORING.md)** - Vue d'ensemble de la refactorisation
- **[RESUME_MODIFICATIONS.md](RESUME_MODIFICATIONS.md)** - Résumé des modifications
- **[game/README.md](game/README.md)** - Architecture détaillée des modules

## ✨ Nouveautés (Version 2.0)

### 🎯 Refactorisation Complète

Le projet a été **entièrement refactorisé** pour une meilleure maintenabilité :

- ✅ **main.py réduit de 95%** : 648 → 29 lignes
- ✅ **8 modules spécialisés** créés dans `game/`
- ✅ **Architecture modulaire** avec séparation des responsabilités
- ✅ **Bug de victoire corrigé** et validé par tests
- ✅ **Tests unitaires** ajoutés
- ✅ **Documentation complète** (4 fichiers markdown)

### 🐛 Corrections

- ✅ **Système de victoire** : Détecte correctement quand tous les points sont mangés
- ✅ **Performance** : Rendu optimisé (tuiles visibles uniquement)
- ✅ **Fluidité** : Interpolation sous-tuile améliorée

## Builder et distribuer le jeu

### Prérequis pour le build
```bash
pip install pyinstaller
```

### Builder sur Linux
```bash
# Nettoyer les anciens builds
rm -rf build/ dist/

# Créer l'exécutable
pyinstaller pacman_game.spec --clean -y

# L'exécutable se trouve dans dist/pacman_game/
./dist/pacman_game/pacman_game
```

### Builder sur Windows
```bash
# Nettoyer les anciens builds
rmdir /S /Q build dist

# Créer l'exécutable
pyinstaller pacman_game.spec --clean -y

# L'exécutable se trouve dans dist\pacman_game\
dist\pacman_game\pacman_game.exe
```

### Builder sur macOS
```bash
# Nettoyer les anciens builds
rm -rf build/ dist/

# Créer l'exécutable
pyinstaller pacman_game.spec --clean -y

# L'exécutable se trouve dans dist/pacman_game/
./dist/pacman_game/pacman_game
```

### Distribution
Le dossier `dist/pacman_game/` contient tout le nécessaire pour exécuter le jeu :
- L'exécutable principal (`pacman_game` ou `pacman_game.exe`)
- Le dossier `_internal/` avec toutes les dépendances (Python, pygame, etc.)
- Les assets du jeu (cartes, sons, etc.)

Pour distribuer le jeu, compressez simplement le dossier `dist/pacman_game/` en ZIP et partagez-le. Les utilisateurs n'auront pas besoin d'installer Python ou les dépendances.

## 🏗️ Architecture du Projet

```
pacman_resize/
├── 📄 main.py                      (29 lignes) - Point d'entrée
├── 📄 test_victory.py              - Tests unitaires
├── 📖 GUIDE_DEMARRAGE.md           - Guide utilisateur
├── 📖 REFACTORING.md               - Vue d'ensemble
├── 📖 RESUME_MODIFICATIONS.md      - Résumé des modifs
│
├── 📁 game/                        - Modules du jeu
│   ├── 📄 __init__.py
│   ├── 📄 constants.py             (54 lignes) - Constantes
│   ├── 📄 utils.py                 (127 lignes) - Utilitaires
│   ├── 📄 level_manager.py         (103 lignes) - Gestion niveaux
│   ├── 📄 game_state.py            (185 lignes) - État du jeu
│   ├── 📄 renderer.py              (316 lignes) - Rendu visuel
│   ├── 📄 collision_manager.py     (126 lignes) - Collisions
│   ├── 📄 game_loop.py             (349 lignes) - Boucle principale
│   ├── 📄 entities.py              - Entités (Pacman, Ghost, etc.)
│   ├── 📄 map.py                   - Gestion des cartes
│   ├── 📄 score.py                 - Système de score
│   ├── 📄 map_generator.py         - Génération procédurale
│   ├── 📄 menu.py                  - Menu principal
│   ├── 📄 settings.py              - Paramètres
│   ├── 📄 hardcore.py              - Mode hardcore
│   └── 📖 README.md                - Doc des modules
│
└── 📁 assets/
    └── 📁 maps/                    - Cartes statiques
        ├── maplv1.map
        ├── maplv2.map
        └── maplv3.map
```

### Séparation des Responsabilités

Chaque module a un rôle unique :

- **constants.py** : Configuration centralisée
- **utils.py** : Fonctions réutilisables
- **level_manager.py** : Progression des niveaux
- **game_state.py** : État du jeu + **vérification de victoire**
- **renderer.py** : Affichage pur (aucune logique de gameplay)
- **collision_manager.py** : Toutes les collisions
- **game_loop.py** : Orchestre tous les modules

## 🎮 Fonctionnalités

### Gameplay Classique Amélioré

- 🟡 **Pacman** : Contrôle fluide avec interpolation sous-tuile
- 👻 **Fantômes intelligents** : IA qui poursuit activement le joueur
- 🎯 **Système de combo** : Points croissants (10 → 20 → 40 → 80)
- ⚡ **Super-pastilles** : Boost de vitesse + vision élargie + fantômes mangeables
- 📊 **Score en temps réel** : Niveau, score, temps, boost restant

### Progression des Niveaux

- 🗺️ **Niveaux 1-3** : Cartes statiques prédéfinies
- 🎲 **Niveaux 4+** : Génération procédurale infinie
- 📈 **Difficulté croissante** : Fantômes +10% plus rapides par niveau
- ⏱️ **Pouvoirs dégressifs** : Durée des pouvoirs diminue avec les niveaux

### Mécanique Unique : Champ de Vision

- 👁️ **Vision limitée** autour de Pacman
- 📉 **Rétrécissement progressif** au fil du temps
- 🔦 **Élargissement** avec les super-pastilles (+5 tuiles)
- ⚠️ **Challenge croissant** : Rétrécit plus vite à chaque niveau

### Mode Hardcore (Optionnel)

- Barre de RAM qui monte avec le temps
- Objectif : finir avec RAM minimale
- Activable dans les paramètres

## 🧪 Tests

Le projet inclut des tests unitaires pour valider les fonctionnalités critiques :

```bash
# Lancer les tests
python3 test_victory.py
```

**Tests inclus** :
- ✅ Détection de victoire (dots restants)
- ✅ Détection de victoire (power_dots restants)
- ✅ Détection de victoire (les deux restants)
- ✅ Victoire correcte (tous les points mangés)

## 🎯 Qualité du Code

- ✅ **Aucune erreur de linter**
- ✅ **Tests unitaires** qui passent
- ✅ **Architecture modulaire** avec séparation des responsabilités
- ✅ **Type hints** pour la clarté du code
- ✅ **Documentation complète** (docstrings + markdown)
- ✅ **Performance optimisée** (60 FPS constants)

## Cahier des charges (CDC)

### 1. Architecture générale
- Menu principal
  - JOUER: lance le mode sélectionné (Normal/Extrême)
  - PARAMÈTRES: activer/désactiver le mode extrême et options
  - Navigation: flèches, validation: Entrée, retour: Échap
- Modes de jeu
  - Pacman classique + mécaniques innovantes
  - Fenêtre dynamique: se rétrécit avec le temps, s'agrandit en mangeant des fantômes
  - Jetons spéciaux avec effets aléatoires
  - Score basé sur objets collectés
  - Mode Extrême: barre RAM, montée auto, baisse via points, objectif RAM finale minimale

### 2. Spécifications techniques
- Fenêtre dynamique
  - Rétrécissement: −1 ligne/colonne toutes les X secondes
  - Agrandissement: +2 lignes/colonnes par fantôme mangé
  - Limites: min 10x10, max: taille terminal
  - Centrage automatique de la zone de jeu
- Entités
  - Pacman: caractère `●` (ou `@`), 4 directions, collisions, orientation visuelle
  - Fantômes: `▲ ▼ ◄ ►` (4 couleurs: Rouge, Bleu, Rose, Orange), IA aléatoire avec évitement murs
  - Objets:
    - Points `.` (1 pt)
    - Gros points `○` (10 pts)
    - Jetons `★` (50 pts + effet)
- Effets de jetons (durée gérée par timestamp de fin):
  1) Téléportation: position aléatoire
  2) Inversion des points: `.` ↔ `○`
  3) Fantômes lents: vitesse ÷2 pendant 10s
  4) Vision: révèle temporairement les objets cachés
  5) Multiplicateur: points ×2 pendant 15s
  6) Bouclier: invincibilité 5s
- Système de RAM (Mode Extrême)
  - Augmentation: +2% toutes les 3s
  - Diminution: −1% par tranche de 50 points gagnés
  - Affichage: `RAM: [████░░░░░░] 40%` en haut
  - Game Over: à 100%
  - Score final affiché: `Score: 2500pts | RAM finale: 15%`

### 3. Interface utilisateur
- Affichage en trois zones: barre d'état (haut), zone de jeu (centre), infos (bas)
- Couleurs:
  - Pacman: jaune
  ️- Fantômes: rouge, bleu, rose, orange
  - Murs: blanc/gris
  - Points: blanc
  - Jetons spéciaux: jaune clignotant
  - Interface: cyan/vert

### 4. Algorithmes clés (concepts)
- Redimensionnement dynamique: minuterie pour shrink/expand, respect des bornes, recentrage
- Gestion des effets: table des effets actifs avec `end_time`, désactivation automatique

### 5. Étapes de développement (phases)
1) Menu + structure de base
2) Pacman + carte statique
3) Fantômes + IA basique
4) Fenêtre dynamique
5) Jetons spéciaux + effets
6) Mode RAM extrême
7) Finition + optimisations

### 6. Contraintes techniques
- Performance: 30 FPS cible (`win.timeout(33)`)
- Compatibilité: Windows/Linux/macOS via curses
- Résolution minimum: 80x24
- Sauvegarde: meilleurs scores en fichier local
- Contrôles: flèches, ESC (quitter), P (pause)

## Partage via Git
```bash
git init
git add .
git commit -m "Scaffold: structure Pacman terminal + README/CDC"
git branch -M main
git remote add origin <URL_DU_DEPOT>
git push -u origin main
```

## Références utiles
- Docs curses: `https://docs.python.org/3/howto/curses.html`
- Exemple Snake temps réel: `https://www.python-engineer.com/posts/snake-game-in-python/`
- Intro ncurses: `https://hackaday.com/2025/06/17/a-gentle-introduction-to-ncurses-for-the-terminally-impatient/`
