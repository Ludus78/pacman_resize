"""Constantes du jeu Pacman.

Ce module regroupe toutes les constantes utilisées dans le jeu
pour faciliter la configuration et la maintenance.
"""

# Dimensions et affichage
TILE = 16  # Taille d'une tuile en pixels
FPS = 60  # Images par seconde
UI_OFFSET = 28  # Espace réservé pour l'interface en haut

# Niveaux statiques
BASE_WIDTH = 28  # Largeur de base des cartes générées
BASE_HEIGHT = 24  # Hauteur de base des cartes générées
NUM_GHOSTS = 4  # Nombre de fantômes par défaut
MIN_SAFE_SPAWN_DISTANCE = 8  # Distance minimale entre Pacman et les fantômes au spawn

# Gameplay
PACMAN_BASE_SPEED = 4  # Vitesse de base de Pacman
PACMAN_BOOST_MULTIPLIER = 1.5  # Multiplicateur de vitesse lors du boost
GHOST_SPEED_INCREASE = 1.10  # Augmentation de vitesse des fantômes par niveau
MIN_FOV = 5.0  # Champ de vision minimum (en tuiles)
FOV_SHRINK_RATE = 1.8  # Vitesse de rétrécissement du FOV (secondes par tuile)
FOV_BOOST = 7  # Tuiles ajoutées au FOV lors d'un power pellet
GHOST_RESPAWN_TIME = 4.0  # Temps de respawn des fantômes (secondes)

# Durées des pouvoirs
BASE_FRIGHTENED_DURATION = 10.0  # Durée de base du mode frightened (niveau 1)
MIN_FRIGHTENED_DURATION = 3.0  # Durée minimale du mode frightened

# Points
PELLET_VALUE = 10  # Points pour une pastille normale
POWER_PELLET_VALUE = 50  # Points pour une super pastille
GHOST_POINTS = [100, 200, 400, 800]  # Points selon le combo de fantômes mangés

# Score maximum (9 chiffres)
MAX_SCORE = 999999999 

# Couleurs (RGB)
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_PACMAN = (255, 215, 0)
COLOR_PELLET = (230, 230, 230)
COLOR_POWER_PELLET = (255, 255, 255)
COLOR_WALL = (0, 0, 200)
COLOR_FRIGHTENED_GHOST = (170, 80, 255)
COLOR_UI_BAR = (20, 24, 60)
COLOR_UI_LINE = (255, 160, 60)
COLOR_UI_SEPARATOR = (90, 100, 160)

# Couleurs des fantômes
GHOST_COLORS = {
    "red": (200, 30, 30),
    "blue": (60, 120, 255),
    "pink": (255, 100, 180),
    "orange": (255, 150, 24),
}

