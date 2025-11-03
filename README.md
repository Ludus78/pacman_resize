# Pacman (Terminal, Python)

Projet de jeu Pacman en terminal avec Python et curses. Ce dépôt ne contient pour l'instant que la structure du projet et la documentation (aucun code d'implémentation).

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

## Structure de projet recommandée

```
pacman_terminal/
├── main.py                 # Point d'entrée (à implémenter)
├── game/
│   ├── __init__.py
│   ├── menu.py             # Menu principal (JOUER, PARAMÈTRES)
│   ├── pacman.py           # Boucle de jeu et logique principale
│   ├── entities.py         # Pacman, fantômes, objets
│   ├── map.py              # Cartes et collisions
│   └── effects.py          # Effets spéciaux (jetons)
├── assets/
│   └── maps/               # Cartes de jeu (fichiers texte)
├── requirements.txt
├── .gitignore
└── README.md
```

La bibliothèque `curses` est adaptée à:
- Gestion du clavier et de l'affichage en temps réel
- Redimensionnement de fenêtre
- Couleurs et fenêtres (`curses.newwin()`)

## Fonctionnalités ciblées

### Mode Normal
- Pacman classique (déplacements 4 directions, collisions murs/objets)
- Fenêtre qui se rétrécit progressivement avec le temps
- Fenêtre qui s'agrandit quand un fantôme est mangé
- Jetons spéciaux aux effets aléatoires
- Score basé sur les points collectés

### Mode Extrême
- Barre de RAM (0-100%) toujours affichée
- La RAM augmente automatiquement avec le temps
- La RAM diminue en gagnant des points
- Objectif: finir avec le % de RAM le plus bas possible (Game Over à 100%)

## Implémentation (pistes techniques, sans code)
- Utiliser `curses.newwin(h, w, y, x)` pour créer la zone de jeu à dimensions variables
- Centrage automatique: calculer `y, x` d'ancrage selon la taille du terminal
- Gestion du temps: `time.time()` pour cadencer rétrécissement/agrandissement et la durée des effets
- Boucle de jeu: lecture non bloquante du clavier, update logique, rendu, délai (`win.timeout(33)` ≈ 30 FPS)

Exemple d'API interne (idée) pour le redimensionnement:
```
update_window_size(action):
  shrink: height -= 1, width -= 1 (min 10x10)
  expand: height += 2, width += 2 (max = taille terminal - marges)
  recalcule la zone de jeu centrée
```

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
