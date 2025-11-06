"""Gestionnaire de niveaux pour le jeu Pacman.

Ce module gère le chargement des cartes (statiques et procédurales)
et la progression entre les niveaux.
"""
import os
import random
from typing import List, Optional
from game.utils import resource_path, load_map_file
from game.map_generator import generate_map
from game.constants import BASE_WIDTH, BASE_HEIGHT, NUM_GHOSTS


class LevelManager:
    """Gère la progression des niveaux et le chargement des cartes."""
    
    def __init__(self):
        """Initialise le gestionnaire de niveaux."""
        # Liste des niveaux statiques (chemins absolus)
        self.static_levels = [
            resource_path(os.path.join("assets", "maps", "maplv1.map")),
            resource_path(os.path.join("assets", "maps", "maplv2.map")),
            resource_path(os.path.join("assets", "maps", "maplv3.map")),
        ]
        
        # État de la progression
        self.current_level_index = 0
        self.level_number = 1
        self.in_procedural_mode = False
        self.ghost_speed_factor = 1.0
        
    def get_initial_map(self) -> List[str]:
        """Charge la carte initiale (premier niveau).
        
        Returns:
            Liste de lignes représentant la carte
        """
        # Essaie de charger le premier niveau statique
        initial_rows = load_map_file(self.static_levels[0]) if self.static_levels else []
        
        if initial_rows:
            return initial_rows
        else:
            # Fallback si fichiers manquants : génération procédurale
            self.in_procedural_mode = True
            return generate_map(BASE_WIDTH, BASE_HEIGHT, num_ghosts=NUM_GHOSTS)
    
    def get_next_map(self) -> List[str]:
        """Charge la carte du niveau suivant.
        
        Returns:
            Liste de lignes représentant la carte suivante
        """
        # Si on a encore des niveaux statiques à jouer
        if not self.in_procedural_mode and self.current_level_index + 1 < len(self.static_levels):
            self.current_level_index += 1
            self.level_number += 1
            
            next_rows = load_map_file(self.static_levels[self.current_level_index])
            
            if not next_rows:
                # Si le fichier est manquant, bascule en génération procédurale
                self.in_procedural_mode = True
                return self._generate_procedural_map()
            
            return next_rows
        else:
            # Mode procédural (après les 3 cartes statiques)
            self.in_procedural_mode = True
            self.level_number += 1
            return self._generate_procedural_map()
    
    def _generate_procedural_map(self) -> List[str]:
        """Génère une carte procédurale avec variation de taille.
        
        Returns:
            Liste de lignes représentant la carte générée
        """
        # Variation légère de dimensions pour la variété
        jitter_w = random.choice([-2, 0, 2])
        jitter_h = random.choice([-2, 0, 2])
        width_new = max(21, BASE_WIDTH + jitter_w)
        height_new = max(15, BASE_HEIGHT + jitter_h)
        
        # Augmente la vitesse des fantômes à chaque niveau
        from game.constants import GHOST_SPEED_INCREASE
        self.ghost_speed_factor *= GHOST_SPEED_INCREASE
        
        return generate_map(width_new, height_new, num_ghosts=NUM_GHOSTS)
    
    def reset(self) -> List[str]:
        """Réinitialise la progression des niveaux au début.
        
        Returns:
            Liste de lignes représentant la première carte
        """
        self.current_level_index = 0
        self.level_number = 1
        self.in_procedural_mode = False
        self.ghost_speed_factor = 1.0
        
        return self.get_initial_map()

