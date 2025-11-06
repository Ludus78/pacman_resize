"""Gestionnaire de collisions pour le jeu Pacman.

Ce module gère toutes les collisions entre Pacman et les éléments du jeu
(pastilles, fantômes, etc.).
"""
from typing import TYPE_CHECKING, List
from game import settings, hardcore
from game.utils import get_ghost_points
from game.constants import (
    FOV_BOOST, BASE_FRIGHTENED_DURATION, 
    MIN_FRIGHTENED_DURATION, PACMAN_BASE_SPEED,
    PACMAN_BOOST_MULTIPLIER
)

if TYPE_CHECKING:
    from game.game_state import GameState


class CollisionManager:
    """Gère les collisions et interactions du jeu."""
    
    @staticmethod
    def check_pellet_collision(state: 'GameState') -> None:
        """Vérifie si Pacman mange une pastille.
        
        Args:
            state: État du jeu
        """
        ppos = (state.pacman.position.x, state.pacman.position.y)
        
        # Pastille normale
        if ppos in state.dots:
            state.score.add(state.dots[ppos].value)
            del state.dots[ppos]
            
            if settings.hardcore_mode:
                hardcore.decrease()
    
    @staticmethod
    def check_power_pellet_collision(state: 'GameState', level_number: int) -> None:
        """Vérifie si Pacman mange une super-pastille.
        
        Args:
            state: État du jeu
            level_number: Numéro du niveau actuel
        """
        ppos = (state.pacman.position.x, state.pacman.position.y)
        
        # Super-pastille
        if ppos in state.power_dots:
            state.score.add(state.power_dots[ppos].value)
            del state.power_dots[ppos]
            
            if settings.hardcore_mode:
                hardcore.decrease()
            
            # Élargit le champ de vision (avec animation)
            state.fov_target = state.fov_tiles + FOV_BOOST
            
            # Active le pouvoir : durée dépend du niveau
            duration = max(
                MIN_FRIGHTENED_DURATION, 
                BASE_FRIGHTENED_DURATION / max(1, level_number)
            )
            state.frightened_timer = duration
            
            # Boost de vitesse pour Pacman : 1.5x plus rapide que les fantômes (mode attaque)
            max_ghost_speed = max((ghost.speed for ghost in state.ghosts), default=PACMAN_BASE_SPEED)
            target_speed = max_ghost_speed * PACMAN_BOOST_MULTIPLIER

            if state.pacman_boost_timer <= 0.0:
                state.pacman_original_speed = state.pacman.speed

            # Assure la vitesse cible (au moins le boost de base)
            min_boost_speed = PACMAN_BASE_SPEED * PACMAN_BOOST_MULTIPLIER
            state.pacman.speed = max(target_speed, min_boost_speed)
            state.pacman_boost_timer = duration
            
            # Réinitialise le compteur de combo
            state.ghost_combo_counter = 0
    
    @staticmethod
    def check_ghost_collision(state: 'GameState') -> bool:
        """Vérifie les collisions entre Pacman et les fantômes.
        
        Args:
            state: État du jeu
            
        Returns:
            True si Pacman meurt (Game Over), False sinon
        """
        eaten_indexes: List[int] = []
        
        for idx, ghost in enumerate(state.ghosts):
            if (ghost.position.x == state.pacman.position.x and 
                ghost.position.y == state.pacman.position.y):
                
                if state.frightened_timer > 0.0:
                    # Pacman mange le fantôme
                    eaten_indexes.append(idx)
                else:
                    # Fantôme tue Pacman
                    return True
        
        # Retire les fantômes mangés (en ordre inverse pour préserver les indices)
        if eaten_indexes:
            for idx in reversed(eaten_indexes):
                CollisionManager._eat_ghost(state, idx)
        
        return False
    
    @staticmethod
    def _eat_ghost(state: 'GameState', idx: int) -> None:
        """Mange un fantôme et le met en respawn.
        
        Args:
            state: État du jeu
            idx: Index du fantôme à manger
        """
        # Ajoute les points selon le combo
        ghost_points = get_ghost_points(state.ghost_combo_counter)
        state.score.add(ghost_points)
        state.ghost_combo_counter += 1
        
        # Retire le fantôme et le met en file de respawn
        g = state.ghosts.pop(idx)
        state.ghost_accums.pop(idx)
        
        color = g.color if isinstance(g.color, str) else "red"
        from game.constants import GHOST_RESPAWN_TIME
        state.respawn_timers.append((GHOST_RESPAWN_TIME, color, g.speed))

