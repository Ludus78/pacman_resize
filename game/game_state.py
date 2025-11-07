"""État du jeu Pacman.

Ce module encapsule toutes les variables d'état du jeu et fournit
les méthodes pour réinitialiser une manche.
"""
from typing import Dict, List, Tuple, Optional
import pygame
from game.entities import Pacman, Ghost, Pellet, PowerPellet, Position
from game.map import GameMap
from game.score import Score
from game.constants import (
    TILE, UI_OFFSET, RENDER_MARGIN, PACMAN_BASE_SPEED
)


class GameState:
    """Encapsule l'état complet d'une partie de Pacman."""
    
    def __init__(self, width_px: int, height_px: int, existing_screen: Optional[pygame.Surface] = None):
        """Initialise l'état du jeu.
        
        Args:
            width_px: Largeur de la fenêtre en pixels
            height_px: Hauteur de la fenêtre en pixels
            existing_screen: Surface pygame existante à réutiliser (None pour créer une nouvelle)
        """
        # Fenêtre et affichage
        self.width_px = width_px
        self.height_px = height_px
        self.screen: Optional[pygame.Surface] = existing_screen
        self.use_existing_screen = existing_screen is not None
        self.render_surface: Optional[pygame.Surface] = None
        self.render_scale_x: float = 1.0
        self.render_scale_y: float = 1.0
        self.render_offset: Tuple[int, int] = (0, 0)
        
        # Carte et entités
        self.game_map: Optional[GameMap] = None
        self.pacman: Optional[Pacman] = None
        self.ghosts: List[Ghost] = []
        self.dots: Dict[Tuple[int, int], Pellet] = {}
        self.power_dots: Dict[Tuple[int, int], PowerPellet] = {}
        
        # Score
        self.score = Score()
        
        # Timers et accumulateurs
        self.move_accum = 0.0
        self.ghost_accums: List[float] = []
        self.frightened_timer = 0.0
        self.shrink_timer = 0.0
        self.pacman_boost_timer = 0.0
        self.elapsed_time = 0.0
        
        # Champ de vision
        self.fov_tiles = 0.0
        self.fov_target = 0.0  # Cible pour l'animation du FOV
        self.fov_animation_speed = 30.0  # Tuiles par seconde pour l'animation
        
        # Respawn des fantômes (remaining_time, color, speed)
        self.respawn_timers: List[Tuple[float, str, float]] = []
        
        # Position de la cage (pour respawn)
        self.cage_pos: Optional[Tuple[int, int]] = None
        
        # Vitesse originale de Pacman (pour restauration après boost)
        self.pacman_original_speed: Optional[float] = None
        
        # Combo de fantômes mangés
        self.ghost_combo_counter = 0
        
        # État de la partie
        self.game_over = False
        self.victory = False
    
    def reset_round(self, rows: List[str], ghost_speed_factor: float, reset_score: bool = False) -> None:
        """Réinitialise la manche avec une nouvelle carte.
        
        Args:
            rows: Lignes de la carte à charger
            ghost_speed_factor: Facteur de vitesse des fantômes
            reset_score: Si True, remet le score à zéro
        """
        # Recharge la carte
        self.game_map = GameMap(rows)
        
        # Adapte la taille de la fenêtre si nécessaire (mode plein écran)
        self.width_px = max(len(r) for r in self.game_map.rows) * TILE if self.game_map.rows else 28 * TILE
        self.height_px = len(self.game_map.rows) * TILE
        
        # Ne recrée l'écran que si on n'utilise pas un écran existant
        if not self.use_existing_screen:
            self.screen = pygame.display.set_mode((0, 0), pygame.APPACTIVE)

        # Surface de rendu de base avec marges (non mise à l'échelle)
        surface_size = (self.width_px + RENDER_MARGIN * 2, self.height_px + UI_OFFSET + RENDER_MARGIN * 2)
        if (self.render_surface is None or
                self.render_surface.get_size() != surface_size):
            self.render_surface = pygame.Surface(surface_size).convert_alpha()
        self.render_surface.fill((0, 0, 0))
        self.render_scale_x = 1.0
        self.render_scale_y = 1.0
        self.render_offset = (0, 0)
        
        # Recrée les collectibles
        self._create_collectibles()
        
        # Positionne Pacman
        self._setup_pacman()
        
        # Crée les fantômes
        self._setup_ghosts(ghost_speed_factor)
        
        # Réinitialise les timers
        self._reset_timers()
        
        # Champ de vision initial
        self.fov_tiles = float(max(self.width_px, self.height_px) // TILE)
        self.fov_target = self.fov_tiles  # Initialise la cible aussi
        
        # Score
        if reset_score:
            self.score = Score()
        
        # État de la partie
        self.game_over = False
        self.victory = False
    
    def _create_collectibles(self) -> None:
        """Crée les pastilles et super-pastilles depuis la carte."""
        self.dots = {}
        self.power_dots = {}
        self.cage_pos = None
        
        for y, row in enumerate(self.game_map.rows):
            for x, ch in enumerate(row):
                if ch == '.':
                    self.dots[(x, y)] = Pellet(Position(x, y), value=1)
                elif ch in ('o', 'O'):
                    self.power_dots[(x, y)] = PowerPellet(Position(x, y))
                elif ch == 'C':
                    self.cage_pos = (x, y)
    
    def _setup_pacman(self) -> None:
        """Positionne Pacman au point de départ."""
        start = self.game_map.find_char('P')
        
        if start is None:
            # Position par défaut si pas de 'P' dans la carte
            start_pos = (1, 1)
            if self.game_map.is_blocked(*start_pos):
                start_pos = (0, 0)
        else:
            start_pos = start
            self.game_map.clear_char('P')
        
        self.pacman = Pacman(Position(x=start_pos[0], y=start_pos[1]), speed=PACMAN_BASE_SPEED)
    
    def _setup_ghosts(self, ghost_speed_factor: float) -> None:
        """Crée les fantômes depuis la carte.
        
        Args:
            ghost_speed_factor: Facteur multiplicatif de vitesse
        """
        self.ghosts = []
        colors_local = ["red", "blue", "pink", "orange"]
        
        while True:
            gpos = self.game_map.find_char('G')
            if gpos is None:
                break
            
            gx, gy = gpos
            self.game_map.clear_char('G')
            
            # Applique le scaling de vitesse selon le niveau
            ghost_speed = max(1.0, self.pacman.speed * ghost_speed_factor)
            ghost = Ghost(
                Position(x=gx, y=gy),
                speed=ghost_speed,
                direction=(0, 0),
                color=colors_local[len(self.ghosts) % len(colors_local)]
            )
            self.ghosts.append(ghost)
        
        self.ghost_accums = [0.0 for _ in self.ghosts]
    
    def _reset_timers(self) -> None:
        """Réinitialise tous les timers et compteurs."""
        self.move_accum = 0.0
        self.frightened_timer = 0.0
        self.shrink_timer = 0.0
        self.pacman_boost_timer = 0.0
        self.pacman_original_speed = None
        self.elapsed_time = 0.0
        self.ghost_combo_counter = 0
        self.respawn_timers = []
    
    def check_victory(self) -> bool:
        """Vérifie si le joueur a gagné (tous les points mangés).
        
        Returns:
            True si victoire, False sinon
        """
        # Victoire = tous les dots ET power_dots ont été mangés
        return len(self.dots) == 0 and len(self.power_dots) == 0

    def to_screen_rect(self, rect: pygame.Rect) -> pygame.Rect:
        """Convertit un rectangle de la surface de rendu vers l'écran.

        Args:
            rect: Rectangle dans les coordonnées de la surface de rendu

        Returns:
            Rectangle converti dans les coordonnées de l'écran
        """
        scale_x = self.render_scale_x
        scale_y = self.render_scale_y
        offset_x, offset_y = self.render_offset
        new_rect = rect.copy()
        new_rect.x = int(rect.x * scale_x + offset_x)
        new_rect.y = int(rect.y * scale_y + offset_y)
        new_rect.width = int(rect.width * scale_x)
        new_rect.height = int(rect.height * scale_y)
        return new_rect

