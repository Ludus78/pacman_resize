"""Gestionnaire de rendu pour le jeu Pacman.

Ce module gère tout l'affichage du jeu : carte, entités, UI, écrans de fin.
"""
import pygame
import math
from typing import TYPE_CHECKING
from game.constants import (
    TILE, UI_OFFSET, COLOR_BLACK, COLOR_WHITE, COLOR_PACMAN,
    COLOR_PELLET, COLOR_POWER_PELLET, COLOR_WALL, COLOR_FRIGHTENED_GHOST,
    COLOR_UI_BAR, COLOR_UI_LINE, COLOR_UI_SEPARATOR, GHOST_COLORS
)
from game.utils import format_time

if TYPE_CHECKING:
    from game.game_state import GameState


class Renderer:
    """Gère l'affichage du jeu."""
    
    def __init__(self):
        """Initialise le renderer avec les polices."""
        self.font = pygame.font.SysFont(None, 18)
        self.title_font = pygame.font.SysFont(None, 72)
        self.score_big_font = pygame.font.SysFont(None, 48)
        self.ui_title_font = pygame.font.SysFont(None, 22)
    
    def render(self, state: 'GameState', level_number: int) -> None:
        """Effectue le rendu complet de la frame.
        
        Args:
            state: État actuel du jeu
            level_number: Numéro du niveau actuel
        """
        # Fond noir
        state.screen.fill(COLOR_BLACK)
        
        # Calcule la position de Pacman avec interpolation
        px, py = self._get_pacman_position(state)
        
        # Calcule la caméra centrée sur Pacman
        cam_x, cam_y = self._calculate_camera(state, px, py)
        
        # Dessine les éléments du jeu
        self._draw_map(state, cam_x, cam_y)
        self._draw_collectibles(state, cam_x, cam_y)
        self._draw_pacman(state, px, py, cam_x, cam_y)
        self._draw_ghosts(state, cam_x, cam_y)
        
        # Applique le masque de champ de vision
        self._draw_fov_mask(state, px, py, cam_x, cam_y)
        
        # Dessine l'interface utilisateur
        self._draw_ui(state, level_number)
        
        # Écrans de fin si nécessaire
        if state.game_over:
            self._draw_game_over(state)
        elif state.victory:
            self._draw_victory(state)
        
        # Met à jour l'affichage
        pygame.display.flip()
    
    def _get_pacman_position(self, state: 'GameState') -> tuple[int, int]:
        """Calcule la position de Pacman avec interpolation.
        
        Args:
            state: État du jeu
            
        Returns:
            Position (px, py) en pixels
        """
        px = state.pacman.position.x * TILE + TILE // 2
        py = state.pacman.position.y * TILE + TILE // 2
        
        # Interpolation sous-tuile si en mouvement
        if state.pacman.direction != (0, 0) and state.move_accum > 0.0:
            npx = state.pacman.position.x + state.pacman.direction[0]
            npy = state.pacman.position.y + state.pacman.direction[1]
            
            if state.pacman.can_move_to(npx, npy, state.game_map):
                off_x = state.pacman.direction[0] * int(state.move_accum * TILE)
                off_y = state.pacman.direction[1] * int(state.move_accum * TILE)
                px += off_x
                py += off_y
        
        return px, py
    
    def _calculate_camera(self, state: 'GameState', px: int, py: int) -> tuple[int, int]:
        """Calcule la position de la caméra centrée sur Pacman.
        
        Args:
            state: État du jeu
            px, py: Position de Pacman en pixels
            
        Returns:
            Position (cam_x, cam_y) de la caméra
        """
        map_w_px = state.game_map.width * TILE
        map_h_px = state.game_map.height * TILE
        
        target_sx = state.width_px // 2
        target_sy = UI_OFFSET + state.height_px // 2
        
        cam_x = int(max(0, min(map_w_px - state.width_px, px - target_sx)))
        cam_y = int(max(0, min(map_h_px - state.height_px, py - (target_sy - UI_OFFSET))))
        
        return cam_x, cam_y
    
    def _draw_map(self, state: 'GameState', cam_x: int, cam_y: int) -> None:
        """Dessine la carte (murs).
        
        Args:
            state: État du jeu
            cam_x, cam_y: Position de la caméra
        """
        # Optimisation : ne dessine que les tuiles visibles
        x0 = max(0, cam_x // TILE)
        y0 = max(0, cam_y // TILE)
        x1 = min(state.game_map.width, (cam_x + state.width_px) // TILE + 1)
        y1 = min(state.game_map.height, (cam_y + state.height_px) // TILE + 1)
        
        for y in range(y0, y1):
            row = state.game_map.rows[y]
            for x in range(x0, x1):
                if x >= len(row):
                    continue
                ch = row[x]
                if ch == '#':
                    sx = x * TILE - cam_x
                    sy = y * TILE - cam_y + UI_OFFSET
                    pygame.draw.rect(state.screen, COLOR_WALL, (sx, sy, TILE, TILE))
    
    def _draw_collectibles(self, state: 'GameState', cam_x: int, cam_y: int) -> None:
        """Dessine les pastilles et super-pastilles.
        
        Args:
            state: État du jeu
            cam_x, cam_y: Position de la caméra
        """
        # Pastilles normales
        for (cx, cy) in state.dots.keys():
            sx = cx * TILE + TILE // 2 - cam_x
            sy = cy * TILE + TILE // 2 - cam_y + UI_OFFSET
            pygame.draw.circle(state.screen, COLOR_PELLET, (sx, sy), max(2, TILE // 8))
        
        # Super-pastilles
        for (cx, cy) in state.power_dots.keys():
            sx = cx * TILE + TILE // 2 - cam_x
            sy = cy * TILE + TILE // 2 - cam_y + UI_OFFSET
            pygame.draw.circle(state.screen, COLOR_POWER_PELLET, (sx, sy), max(4, TILE // 4))
    
    def _draw_pacman(self, state: 'GameState', px: int, py: int, cam_x: int, cam_y: int) -> None:
        """Dessine Pacman.
        
        Args:
            state: État du jeu
            px, py: Position de Pacman
            cam_x, cam_y: Position de la caméra
        """
        # Animation bouche (0 à 1) en fonction du temps écoulé
        open_ratio = 0.25 + 0.25 * math.sin(state.elapsed_time * 10)
        mouth_angle = open_ratio * math.pi

        # Direction de Pacman
        dx, dy = state.pacman.direction
        if (dx, dy) == (0, 0):
            dx, dy = state.pacman.desired_direction
        if (dx, dy) == (0, 0):
            dx = 1  # bouche vers la droite par défaut

        if dx > 0:  # droite
            start_ang = -mouth_angle / 2
            end_ang = mouth_angle / 2
        elif dx < 0:  # gauche
            start_ang = math.pi - mouth_angle / 2
            end_ang = math.pi + mouth_angle / 2
        elif dy < 0:  # haut
            start_ang = -math.pi / 2 - mouth_angle / 2
            end_ang = -math.pi / 2 + mouth_angle / 2
        else:  # bas
            start_ang = math.pi / 2 - mouth_angle / 2
            end_ang = math.pi / 2 + mouth_angle / 2

        # Corps de Pacman (cercle plein)
        pygame.draw.circle(
            state.screen,
            COLOR_PACMAN,
            (px - cam_x, py - cam_y + UI_OFFSET),
            TILE // 2
        )
        # Coupe la bouche en dessinant un secteur transparent (fond)
        mouth_radius = TILE // 2 + 1
        mouth_points = [(px - cam_x, py - cam_y + UI_OFFSET)]
        for ang in (start_ang, end_ang):
            mouth_points.append((
                px - cam_x + mouth_radius * math.cos(ang),
                py - cam_y + UI_OFFSET + mouth_radius * math.sin(ang)
            ))
        pygame.draw.polygon(state.screen, COLOR_BLACK, mouth_points)

    
    def _draw_ghosts(self, state: 'GameState', cam_x: int, cam_y: int) -> None:
        """Dessine les fantômes.
        
        Args:
            state: État du jeu
            cam_x, cam_y: Position de la caméra
        """
        for i, ghost in enumerate(state.ghosts):
            # Couleur selon le mode
            if state.frightened_timer > 0.0:
                col = COLOR_FRIGHTENED_GHOST
            else:
                col = ghost.color
                if isinstance(col, str):
                    col = GHOST_COLORS.get(col.lower(), GHOST_COLORS["red"])
                elif not isinstance(col, (tuple, list)):
                    col = GHOST_COLORS["red"]
            
            # Position avec interpolation
            gx = ghost.position.x * TILE + TILE // 2
            gy = ghost.position.y * TILE + TILE // 2
            
            if (ghost.direction != (0, 0) and 0 <= i < len(state.ghost_accums) 
                and state.ghost_accums[i] > 0.0):
                ngx = ghost.position.x + ghost.direction[0]
                ngy = ghost.position.y + ghost.direction[1]
                
                if ghost.can_move_to(ngx, ngy, state.game_map):
                    goff_x = ghost.direction[0] * int(state.ghost_accums[i] * TILE)
                    goff_y = ghost.direction[1] * int(state.ghost_accums[i] * TILE)
                    gx += goff_x
                    gy += goff_y
            
            # Dessin fantôme: tête ronde + bas ondulé
            body_x = gx - cam_x
            body_y = gy - cam_y + UI_OFFSET
            radius = TILE // 2
            # Tête (cercle)
            pygame.draw.circle(state.screen, col, (body_x, body_y - radius // 3), radius)
            # Corps rectangulaire
            pygame.draw.rect(state.screen, col, (body_x - radius, body_y - radius // 3, radius * 2, radius))
            # Bas ondulé (3 demi-cercles animés)
            for k in range(-1, 2):
                cx = body_x + k * radius
                # Animation sinusoïdale des tentacules
                phase = state.elapsed_time * 6 + k
                dy_wave = int((math.sin(phase) + 1) * radius * 0.15)
                cy = body_y + radius // 2 + dy_wave
                pygame.draw.circle(state.screen, col, (cx, cy), radius // 2)
            # Yeux
            eye_offset_x = radius // 2
            eye_offset_y = radius // 3
            eye_r = radius // 3
            for ex in (-eye_offset_x, eye_offset_x):
                pygame.draw.circle(state.screen, COLOR_WHITE, (body_x + ex, body_y - eye_offset_y), eye_r)
                # Pupille
                pygame.draw.circle(state.screen, (0, 0, 0), (body_x + ex, body_y - eye_offset_y), eye_r // 2)
    
    def _draw_fov_mask(self, state: 'GameState', px: int, py: int, cam_x: int, cam_y: int) -> None:
        """Applique le masque de champ de vision.
        
        Args:
            state: État du jeu
            px, py: Position de Pacman
            cam_x, cam_y: Position de la caméra
        """
        overlay = pygame.Surface((state.width_px, state.height_px + UI_OFFSET), pygame.SRCALPHA)
        overlay.fill(COLOR_BLACK)
        
        radius = int(max(0.0, state.fov_tiles) * TILE + TILE // 2)
        pygame.draw.circle(overlay, (0, 0, 0, 0), (px - cam_x, py - cam_y + UI_OFFSET), radius)
        
        state.screen.blit(overlay, (0, 0))
    
    def _draw_ui(self, state: 'GameState', level_number: int) -> None:
        """Dessine l'interface utilisateur (barre supérieure).
        
        Args:
            state: État du jeu
            level_number: Numéro du niveau actuel
        """
        # Ligne colorée en haut
        pygame.draw.line(state.screen, COLOR_UI_LINE, (0, 0), (state.width_px, 0), 2)
        
        # Barre d'interface
        bar_h = 24
        pygame.draw.rect(state.screen, COLOR_UI_BAR, (0, 2, state.width_px, bar_h))
        
        # Titre centré
        title_s = self.ui_title_font.render("PACMAN", True, COLOR_WHITE)
        state.screen.blit(title_s, (state.width_px // 2 - title_s.get_width() // 2, 4))
        
        # Niveau et Score à gauche
        level_surf = self.font.render(f"Level {level_number}", True, (0, 200, 255))
        x_left = 6
        state.screen.blit(level_surf, (x_left, 4))
        
        score_surf = self.font.render(f"Score {state.score}", True, (255, 230, 80))
        x_left += level_surf.get_width() + 12
        state.screen.blit(score_surf, (x_left, 4))
        
        # Temps à droite
        time_text = format_time(state.elapsed_time)
        time_surf = self.font.render(time_text, True, (255, 200, 200))
        state.screen.blit(time_surf, (state.width_px - time_surf.get_width() - 6, 4))
        
        # Timer du boost si actif
        if state.pacman_boost_timer > 0.0:
            remaining = int(math.ceil(state.pacman_boost_timer))
            boost_text = f"Boost: {remaining}s"
            boost_surf = self.font.render(boost_text, True, (255, 200, 60))
            bx = state.width_px - time_surf.get_width() - 12 - boost_surf.get_width()
            state.screen.blit(boost_surf, (bx, 4))
        
        # Ligne de séparation
        pygame.draw.line(state.screen, COLOR_UI_SEPARATOR, (0, 2 + bar_h), (state.width_px, 2 + bar_h), 2)
    
    def _draw_game_over(self, state: 'GameState') -> None:
        """Dessine l'écran de Game Over.
        
        Args:
            state: État du jeu
        """
        title_surf = self.title_font.render("GAME OVER", True, (255, 50, 50))
        score_surf = self.score_big_font.render(f"Score: {state.score}", True, COLOR_WHITE)
        
        title_rect = title_surf.get_rect(
            center=(state.width_px // 2, state.height_px // 2 + UI_OFFSET // 2 - 24)
        )
        score_rect = score_surf.get_rect(
            center=(state.width_px // 2, state.height_px // 2 + UI_OFFSET // 2 + 24)
        )
        
        state.screen.blit(title_surf, title_rect)
        state.screen.blit(score_surf, score_rect)
    
    def _draw_victory(self, state: 'GameState') -> pygame.Rect:
        """Dessine l'écran de victoire avec le bouton.
        
        Args:
            state: État du jeu
            
        Returns:
            Rectangle du bouton "Niveau suivant"
        """
        title_surf = self.title_font.render("VICTOIRE", True, (80, 220, 80))
        score_surf = self.score_big_font.render(f"Score: {state.score}", True, COLOR_WHITE)
        
        title_rect = title_surf.get_rect(
            center=(state.width_px // 2, state.height_px // 2 + UI_OFFSET // 2 - 40)
        )
        score_rect = score_surf.get_rect(
            center=(state.width_px // 2, state.height_px // 2 + UI_OFFSET // 2)
        )
        
        state.screen.blit(title_surf, title_rect)
        state.screen.blit(score_surf, score_rect)
        
        # Bouton "Niveau suivant"
        btn_w, btn_h = 220, 48
        btn_rect = pygame.Rect(0, 0, btn_w, btn_h)
        btn_rect.center = (state.width_px // 2, state.height_px // 2 + UI_OFFSET // 2 + 60)
        
        pygame.draw.rect(state.screen, (40, 140, 255), btn_rect, border_radius=8)
        btn_text = self.font.render("Niveau suivant (Entrée)", True, COLOR_WHITE)
        btn_text_rect = btn_text.get_rect(center=btn_rect.center)
        state.screen.blit(btn_text, btn_text_rect)
        
        return btn_rect

