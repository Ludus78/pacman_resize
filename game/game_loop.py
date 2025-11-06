"""Boucle principale du jeu Pacman.

Ce module contient la logique principale du jeu et orchestre tous les
composants (état, rendu, collisions, etc.).
"""
import pygame
from game.game_state import GameState
from game.level_manager import LevelManager
from game.renderer import Renderer
from game.collision_manager import CollisionManager
from game.entities import Position, Ghost
from game.utils import wait_for_enter, wait_for_button_or_enter
from game import settings, hardcore
from game.constants import (
    TILE, FPS, MIN_FOV, FOV_SHRINK_RATE
)


class GameLoop:
    """Gère la boucle principale du jeu."""
    
    def __init__(self):
        """Initialise la boucle de jeu."""
        pygame.init()
        
        # Gestionnaires
        self.level_manager = LevelManager()
        self.renderer = Renderer()
        
        # Charge la carte initiale
        initial_rows = self.level_manager.get_initial_map()
        width_px = max(len(r) for r in initial_rows) * TILE if initial_rows else 28 * TILE
        height_px = len(initial_rows) * TILE
        
        # État du jeu
        self.state = GameState(width_px, height_px)
        
        # Initialise la première manche
        self.state.reset_round(initial_rows, self.level_manager.ghost_speed_factor, reset_score=True)
        
        # Active le mode hardcore si nécessaire
        if settings.hardcore_mode:
            hardcore.start()
        else:
            hardcore.stop()
        
        # Horloge pour les FPS
        self.clock = pygame.time.Clock()
        
        # Titre de la fenêtre
        pygame.display.set_caption("Pacman")
    
    def run(self) -> None:
        """Lance la boucle principale du jeu."""
        running = True
        
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            
            # Gestion des événements
            if not self._handle_events():
                running = False
                continue
            
            # Mise à jour du jeu si pas en pause
            if not self.state.game_over and not self.state.victory:
                self._update_game(dt)
            
            # Rendu
            self.renderer.render(self.state, self.level_manager.level_number)
            
            # Gestion de la fin de manche
            if self.state.game_over:
                if not self._handle_game_over():
                    running = False
            elif self.state.victory:
                if not self._handle_victory():
                    running = False
        
        # Nettoyage
        hardcore.stop()
        pygame.quit()
    
    def _handle_events(self) -> bool:
        """Gère les événements pygame.
        
        Returns:
            False si on doit quitter, True sinon
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                # Raccourci debug : force la victoire
                elif event.key == pygame.K_p:
                    if not self.state.game_over and not self.state.victory:
                        self.state.dots.clear()
                        self.state.power_dots.clear()
                        self.state.victory = True
                # Raccourci 'm' : ajoute 101 points
                elif event.key == pygame.K_m:
                    if not self.state.game_over and not self.state.victory:
                        self.state.score.add(101)
        
        return True
    
    def _update_game(self, dt: float) -> None:
        """Met à jour l'état du jeu.
        
        Args:
            dt: Delta time en secondes
        """
        self.state.elapsed_time += dt
        
        # Lecture des touches pour le mouvement de Pacman
        self._handle_pacman_input()
        
        # Déplacement de Pacman
        self._update_pacman(dt)
        
        # Déplacement des fantômes
        self._update_ghosts(dt)
        
        # Collision finale (vérification supplémentaire)
        if CollisionManager.check_ghost_collision(self.state):
            self.state.game_over = True
        
        # Gestion des timers
        self._update_timers(dt)
        
        # Animation du champ de vision
        self._update_fov_animation(dt)
        
        # Rétrécissement du champ de vision
        self._update_fov(dt)
        
        # Vérification de la victoire
        if self.state.check_victory():
            self.state.victory = True
    
    def _handle_pacman_input(self) -> None:
        """Gère les entrées clavier pour Pacman."""
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        
        # Priorité horizontale si les deux axes sont pressés
        if keys[pygame.K_LEFT] or keys[pygame.K_q]:
            dx = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
        elif keys[pygame.K_UP] or keys[pygame.K_z]:
            dy = -1
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1
        
        self.state.pacman.set_desired_direction(dx, dy)
    
    def _update_pacman(self, dt: float) -> None:
        """Met à jour la position et l'état de Pacman.
        
        Args:
            dt: Delta time
        """
        # Accumulation des mouvements pour un déplacement fluide
        self.state.move_accum += self.state.pacman.speed * dt
        steps = int(self.state.move_accum)
        
        if steps > 0:
            self.state.move_accum -= steps
            
            for _ in range(steps):
                self.state.pacman.update(1 / self.state.pacman.speed, game_map=self.state.game_map)
                
                # Collisions avec collectibles
                CollisionManager.check_pellet_collision(self.state)
                CollisionManager.check_power_pellet_collision(self.state, self.level_manager.level_number)
                
                # Collision avec fantômes
                if CollisionManager.check_ghost_collision(self.state):
                    self.state.game_over = True
                    break
        
        # Changement de direction instantané au bord de tuile
        ddx, ddy = self.state.pacman.desired_direction
        if (ddx, ddy) != (0, 0):
            nx = self.state.pacman.position.x + ddx
            ny = self.state.pacman.position.y + ddy
            
            if self.state.pacman.can_move_to(nx, ny, self.state.game_map):
                cur_dx, cur_dy = self.state.pacman.direction
                self.state.pacman.direction = (ddx, ddy)
                
                if (ddx, ddy) != (cur_dx, cur_dy):
                    self.state.move_accum = 0.0
    
    def _update_ghosts(self, dt: float) -> None:
        """Met à jour les fantômes.
        
        Args:
            dt: Delta time
        """
        pacman_grid_pos = (self.state.pacman.position.x, self.state.pacman.position.y)
        is_frightened = (self.state.frightened_timer > 0.0)
        
        i = 0
        while i < len(self.state.ghosts):
            ghost = self.state.ghosts[i]
            self.state.ghost_accums[i] += ghost.speed * dt
            gsteps = int(self.state.ghost_accums[i])
            ghost_eaten = False
            
            if gsteps > 0:
                self.state.ghost_accums[i] -= gsteps
                prev_dir = ghost.direction
                
                for _ in range(gsteps):
                    ghost.update(
                        1 / ghost.speed,
                        game_map=self.state.game_map,
                        pacman_pos=pacman_grid_pos,
                        is_frightened=is_frightened
                    )
                    
                    # Collision immédiate
                    if (ghost.position.x == self.state.pacman.position.x and 
                        ghost.position.y == self.state.pacman.position.y):
                        
                        if self.state.frightened_timer > 0.0:
                            CollisionManager._eat_ghost(self.state, i)
                            ghost_eaten = True
                            break
                        else:
                            self.state.game_over = True
                            break
                
                # Transition douce lors des changements de direction
                if (not ghost_eaten and i < len(self.state.ghosts) and 
                    prev_dir != (0, 0) and ghost.direction != prev_dir):
                    self.state.ghost_accums[i] = min(self.state.ghost_accums[i], 0.2)
                
                if self.state.game_over:
                    break
            
            if not ghost_eaten:
                i += 1
    
    def _update_timers(self, dt: float) -> None:
        """Met à jour tous les timers du jeu.
        
        Args:
            dt: Delta time
        """
        # Timer frightened
        if self.state.frightened_timer > 0.0:
            self.state.frightened_timer = max(0.0, self.state.frightened_timer - dt)
            
            # Fin du pouvoir : réinitialise le combo
            if self.state.frightened_timer <= 0.0:
                self.state.ghost_combo_counter = 0
        
        # Timer boost Pacman
        if self.state.pacman_boost_timer > 0.0:
            self.state.pacman_boost_timer = max(0.0, self.state.pacman_boost_timer - dt)
            
            if self.state.pacman_boost_timer == 0.0 and self.state.pacman_original_speed is not None:
                self.state.pacman.speed = self.state.pacman_original_speed
                self.state.pacman_original_speed = None
        
        # Respawn des fantômes
        self._update_ghost_respawn(dt)
    
    def _update_ghost_respawn(self, dt: float) -> None:
        """Gère le respawn des fantômes.
        
        Args:
            dt: Delta time
        """
        if not self.state.respawn_timers:
            return
        
        new_list = []
        for remaining, color, speed in self.state.respawn_timers:
            remaining -= dt
            
            if remaining <= 0.0:
                # Respawn le fantôme
                if self.state.cage_pos is None:
                    cx = max(0, self.state.game_map.width // 2)
                    cy = max(0, self.state.game_map.height // 2)
                else:
                    cx, cy = self.state.cage_pos
                
                new_ghost = Ghost(
                    Position(x=cx, y=cy),
                    speed=max(1.0, speed),
                    direction=(0, -1),
                    color=color
                )
                self.state.ghosts.append(new_ghost)
                self.state.ghost_accums.append(0.0)
            else:
                new_list.append((remaining, color, speed))
        
        self.state.respawn_timers = new_list
    
    def _update_fov_animation(self, dt: float) -> None:
        """Anime le champ de vision vers la valeur cible.
        
        Args:
            dt: Delta time
        """
        if abs(self.state.fov_tiles - self.state.fov_target) > 0.01:
            # Anime progressivement vers la cible
            diff = self.state.fov_target - self.state.fov_tiles
            max_change = self.state.fov_animation_speed * dt
            
            if abs(diff) <= max_change:
                # On est proche, on met directement à la cible
                self.state.fov_tiles = self.state.fov_target
            else:
                # On se rapproche progressivement
                self.state.fov_tiles += max_change if diff > 0 else -max_change
    
    def _update_fov(self, dt: float) -> None:
        """Met à jour le champ de vision (rétrécissement de la cible).
        
        Args:
            dt: Delta time
        """
        if not self.state.game_over and self.state.fov_target > MIN_FOV:
            shrink_rate = FOV_SHRINK_RATE / float(self.level_manager.level_number)
            self.state.fov_target = max(MIN_FOV, self.state.fov_target - (dt / shrink_rate))
    
    def _handle_game_over(self) -> bool:
        """Gère l'écran de Game Over.
        
        Returns:
            False si on quitte, True si on redémarre
        """
        if wait_for_enter(self.state.screen, self.clock):
            # Redémarrage complet
            new_rows = self.level_manager.reset()
            self.state.reset_round(new_rows, self.level_manager.ghost_speed_factor, reset_score=True)
            return True
        else:
            return False
    
    def _handle_victory(self) -> bool:
        """Gère l'écran de victoire et passage au niveau suivant.
        
        Returns:
            False si on quitte, True si on continue
        """
        # Récupère le rectangle du bouton depuis le renderer
        btn_rect = self.renderer._draw_victory(self.state)
        pygame.display.flip()
        
        if wait_for_button_or_enter(self.state.screen, self.clock, btn_rect):
            # Charge le niveau suivant
            next_rows = self.level_manager.get_next_map()
            
            # Active/désactive hardcore selon les paramètres
            hardcore.stop()
            if settings.hardcore_mode:
                hardcore.start()
            
            # Nouvelle manche sans réinitialiser le score
            self.state.reset_round(next_rows, self.level_manager.ghost_speed_factor, reset_score=False)
            return True
        else:
            return False

