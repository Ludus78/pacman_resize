"""Interface utilisateur pour le mode tournoi.

Ce module gère les écrans d'inscription, d'attente entre joueurs et de résultats.
"""
import pygame
from typing import Optional, List
from game.tournament import tournament_manager
from game.constants import TILE


class TournamentUI:
    """Gère l'interface du mode tournoi."""
    
    def __init__(self, screen: pygame.Surface):
        """Initialise l'interface du tournoi.
        
        Args:
            screen: Surface pygame pour l'affichage
        """
        self.screen = screen
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        self.font_tiny = pygame.font.Font(None, 24)
    
    def show_registration_screen(self) -> bool:
        """Affiche l'écran d'inscription des participants.
        
        Returns:
            True si on commence le tournoi, False si on annule
        """
        clock = pygame.time.Clock()
        input_text = ""
        error_message = ""
        error_timer = 0
        scroll_offset = 0  # Pour le défilement de la liste
        
        while True:
            dt = clock.tick(60) / 1000.0
            
            # Décrémenter le timer d'erreur
            if error_timer > 0:
                error_timer -= dt
                if error_timer <= 0:
                    error_message = ""
            
            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return False
                    
                    elif event.key == pygame.K_RETURN:
                        if input_text.strip():
                            # Vérifier la limite de 30 joueurs
                            if len(tournament_manager.players) >= 30:
                                error_message = "Maximum 30 joueurs !"
                                error_timer = 2.0
                            # Ajouter le joueur
                            elif tournament_manager.add_player(input_text.strip()):
                                input_text = ""
                                error_message = ""
                                # Ajuster le scroll pour voir le nouveau joueur
                                if len(tournament_manager.players) > 10:
                                    scroll_offset = len(tournament_manager.players) - 10
                            else:
                                error_message = "Ce nom existe déjà !"
                                error_timer = 2.0
                        elif len(tournament_manager.players) >= 2:
                            # Commencer le tournoi
                            return True
                        else:
                            error_message = "Il faut au moins 2 joueurs !"
                            error_timer = 2.0
                    
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    
                    elif event.key == pygame.K_DELETE and tournament_manager.players:
                        # Supprimer le dernier joueur ajouté
                        tournament_manager.remove_player(tournament_manager.players[-1].name)
                        # Ajuster le scroll
                        if scroll_offset > 0 and len(tournament_manager.players) <= scroll_offset + 10:
                            scroll_offset = max(0, len(tournament_manager.players) - 10)
                    
                    # Défilement avec flèches haut/bas
                    elif event.key == pygame.K_UP and scroll_offset > 0:
                        scroll_offset -= 1
                    
                    elif event.key == pygame.K_DOWN and scroll_offset < max(0, len(tournament_manager.players) - 10):
                        scroll_offset += 1
                    
                    elif len(input_text) < 30 and event.unicode.isprintable():
                        input_text += event.unicode
            
            # Affichage
            self.screen.fill((0, 0, 0))
            
            # Titre
            title = self.font_large.render("INSCRIPTION TOURNOI", True, (255, 255, 0))
            self.screen.blit(title, (self.screen.get_width() // 2 - title.get_width() // 2, 30))
            
            # Instructions
            inst1 = self.font_tiny.render("Entrez le nom des participants et appuyez sur ENTRÉE", True, (255, 255, 255))
            inst2 = self.font_tiny.render("Appuyez sur ENTRÉE sans nom pour COMMENCER (min 2 joueurs)", True, (255, 255, 255))
            inst3 = self.font_tiny.render("DELETE : supprimer le dernier joueur | ÉCHAP : annuler", True, (200, 200, 200))
            
            self.screen.blit(inst1, (self.screen.get_width() // 2 - inst1.get_width() // 2, 120))
            self.screen.blit(inst2, (self.screen.get_width() // 2 - inst2.get_width() // 2, 150))
            self.screen.blit(inst3, (self.screen.get_width() // 2 - inst3.get_width() // 2, 180))
            
            # Champ de saisie
            input_box = pygame.Rect(self.screen.get_width() // 2 - 200, 230, 400, 50)
            pygame.draw.rect(self.screen, (255, 255, 255), input_box, 2)
            
            input_surface = self.font_medium.render(input_text + "|", True, (255, 255, 255))
            self.screen.blit(input_surface, (input_box.x + 10, input_box.y + 10))
            
            # Message d'erreur
            if error_message:
                error_surface = self.font_small.render(error_message, True, (255, 0, 0))
                self.screen.blit(error_surface, (self.screen.get_width() // 2 - error_surface.get_width() // 2, 290))
            
            # Liste des joueurs inscrits
            y_offset = 340
            players_title = self.font_medium.render(
                f"Joueurs inscrits ({len(tournament_manager.players)}/30) :", 
                True, 
                (100, 200, 255)
            )
            self.screen.blit(players_title, (self.screen.get_width() // 2 - players_title.get_width() // 2, y_offset))
            
            y_offset += 60
            if not tournament_manager.players:
                no_player = self.font_small.render("Aucun joueur inscrit", True, (150, 150, 150))
                self.screen.blit(no_player, (self.screen.get_width() // 2 - no_player.get_width() // 2, y_offset))
            else:
                # Affiche jusqu'à 10 joueurs à la fois avec scroll
                visible_players = tournament_manager.players[scroll_offset:scroll_offset + 10]
                for i, player in enumerate(visible_players):
                    actual_index = scroll_offset + i
                    # Limite l'affichage du nom à 30 caractères
                    display_name = player.name[:30]
                    player_text = self.font_small.render(f"{actual_index + 1}. {display_name}", True, (255, 255, 255))
                    self.screen.blit(player_text, (self.screen.get_width() // 2 - player_text.get_width() // 2, y_offset))
                    y_offset += 40
                
                # Indicateurs de scroll
                if scroll_offset > 0:
                    scroll_up = self.font_tiny.render("▲ Plus haut (Flèche Haut)", True, (150, 150, 150))
                    self.screen.blit(scroll_up, (self.screen.get_width() // 2 - scroll_up.get_width() // 2, 330))
                
                if scroll_offset < len(tournament_manager.players) - 10:
                    scroll_down = self.font_tiny.render("▼ Plus bas (Flèche Bas)", True, (150, 150, 150))
                    self.screen.blit(scroll_down, (self.screen.get_width() // 2 - scroll_down.get_width() // 2, y_offset))
            
            pygame.display.flip()
        
        return False
    
    def show_player_ready_screen(self) -> bool:
        """Affiche l'écran d'attente avant qu'un joueur commence.
        
        Returns:
            True si le joueur appuie sur ENTRÉE, False si annulation
        """
        player = tournament_manager.get_current_player()
        if not player:
            return False
        
        clock = pygame.time.Clock()
        
        while True:
            clock.tick(60)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return True
                    elif event.key == pygame.K_ESCAPE:
                        return False
            
            # Affichage
            self.screen.fill((0, 0, 0))
            
            # Nom du joueur
            title = self.font_large.render(player.name, True, (255, 255, 0))
            self.screen.blit(title, (self.screen.get_width() // 2 - title.get_width() // 2, 150))
            
            # Numéro de la vie
            lives_remaining = 3 - player.current_attempt
            life_text = self.font_medium.render(
                f"Vie {player.current_attempt + 1} / 3  ({lives_remaining} restantes)",
                True,
                (255, 100, 100)
            )
            self.screen.blit(life_text, (self.screen.get_width() // 2 - life_text.get_width() // 2, 250))
            
            # Instructions
            inst = self.font_medium.render("Appuyez sur ENTRÉE pour commencer", True, (255, 255, 255))
            self.screen.blit(inst, (self.screen.get_width() // 2 - inst.get_width() // 2, 350))
            
            # Récapitulatif des tentatives précédentes
            if player.attempts:
                recap_title = self.font_small.render("Tentatives précédentes :", True, (150, 150, 255))
                self.screen.blit(recap_title, (self.screen.get_width() // 2 - recap_title.get_width() // 2, 450))
                
                y_offset = 490
                for i, attempt in enumerate(player.attempts):
                    time_str = f"{attempt.time_level1:.2f}s" if attempt.time_level1 else "N/A"
                    recap = self.font_tiny.render(
                        f"Vie {i + 1}: Score {attempt.score} | Niveau {attempt.level_reached} | Temps Niv1: {time_str}",
                        True,
                        (200, 200, 200)
                    )
                    self.screen.blit(recap, (self.screen.get_width() // 2 - recap.get_width() // 2, y_offset))
                    y_offset += 30
            
            pygame.display.flip()
        
        return False
    
    def show_results_screen(self) -> bool:
        """Affiche l'écran des résultats finaux du tournoi.
        
        Returns:
            True pour retourner au menu
        """
        clock = pygame.time.Clock()
        rankings = tournament_manager.get_rankings()
        scroll_offset = 0
        max_scroll = max(0, len(tournament_manager.players) - 15)
        
        # Identifie les top 3 de chaque catégorie
        top3_score = set(r[0] for r in rankings['max_score'][:3])
        top3_level = set(r[0] for r in rankings['max_level'][:3])
        top3_time = set(r[0] for r in rankings['fastest_level1'][:3])
        
        while True:
            clock.tick(60)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True
                
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                        return True
                    elif event.key == pygame.K_UP and scroll_offset > 0:
                        scroll_offset -= 1
                    elif event.key == pygame.K_DOWN and scroll_offset < max_scroll:
                        scroll_offset += 1
            
            # Affichage
            self.screen.fill((0, 0, 0))
            
            # Titre
            title = self.font_large.render("RÉSULTATS DU TOURNOI", True, (255, 215, 0))
            self.screen.blit(title, (self.screen.get_width() // 2 - title.get_width() // 2, 20))
            
            # Colonnes de résultats
            screen_width = self.screen.get_width()
            col_width = screen_width // 3
            
            y_start = 120
            
            # En-têtes des colonnes
            headers = [
                ("🏆 MEILLEUR SCORE", (255, 215, 0)),
                ("🎖️ NIVEAU MAX", (192, 192, 192)),
                ("⚡ TEMPS NIVEAU 1", (205, 127, 50))
            ]
            
            for i, (header_text, color) in enumerate(headers):
                x_center = col_width * i + col_width // 2
                header = self.font_medium.render(header_text, True, color)
                self.screen.blit(header, (x_center - header.get_width() // 2, y_start))
            
            y_start += 70
            
            # Afficher tous les joueurs dans chaque catégorie
            visible_players = tournament_manager.players[scroll_offset:scroll_offset + 15]
            
            for idx, player in enumerate(visible_players):
                y_pos = y_start + idx * 35
                
                # Colonne 1 : Score
                max_score = player.get_max_score()
                is_top3_score = player.name in top3_score
                color = (255, 215, 0) if is_top3_score else (255, 255, 255)
                prefix = "★ " if is_top3_score else ""
                score_text = self.font_small.render(f"{prefix}{player.name[:15]}: {max_score}", True, color)
                self.screen.blit(score_text, (20, y_pos))
                
                # Colonne 2 : Niveau
                max_level = player.get_max_level()
                is_top3_level = player.name in top3_level
                color = (192, 192, 192) if is_top3_level else (255, 255, 255)
                prefix = "★ " if is_top3_level else ""
                level_text = self.font_small.render(f"{prefix}{player.name[:15]}: Niv {max_level}", True, color)
                x_center = col_width + col_width // 2
                self.screen.blit(level_text, (col_width + 20, y_pos))
                
                # Colonne 3 : Temps
                best_time = player.get_best_level1_time()
                if best_time is not None:
                    is_top3_time = player.name in top3_time
                    color = (205, 127, 50) if is_top3_time else (255, 255, 255)
                    prefix = "★ " if is_top3_time else ""
                    time_text = self.font_small.render(f"{prefix}{player.name[:15]}: {best_time:.2f}s", True, color)
                    self.screen.blit(time_text, (col_width * 2 + 20, y_pos))
                else:
                    time_text = self.font_small.render(f"{player.name[:15]}: N/A", True, (100, 100, 100))
                    self.screen.blit(time_text, (col_width * 2 + 20, y_pos))
            
            # Indicateurs de scroll
            if scroll_offset > 0:
                scroll_up = self.font_tiny.render("▲ Scroll Haut", True, (150, 150, 150))
                self.screen.blit(scroll_up, (self.screen.get_width() // 2 - scroll_up.get_width() // 2, 90))
            
            if scroll_offset < max_scroll:
                scroll_down = self.font_tiny.render("▼ Scroll Bas", True, (150, 150, 150))
                self.screen.blit(scroll_down, (self.screen.get_width() // 2 - scroll_down.get_width() // 2, self.screen.get_height() - 70))
            
            # Légende
            legend = self.font_tiny.render("★ = Top 3 dans cette catégorie", True, (150, 150, 150))
            self.screen.blit(legend, (20, self.screen.get_height() - 70))
            
            # Instructions
            inst = self.font_tiny.render("Appuyez sur ENTRÉE pour retourner au menu", True, (200, 200, 200))
            self.screen.blit(inst, (self.screen.get_width() // 2 - inst.get_width() // 2, self.screen.get_height() - 40))
            
            pygame.display.flip()
        
        return True
    
    def _draw_award(self, title: str, ranking: List, y: int, value_formatter):
        """Dessine un prix avec son podium.
        
        Args:
            title: Titre du prix
            ranking: Liste de tuples (nom, valeur, tiebreak)
            y: Position Y
            value_formatter: Fonction pour formater la valeur
        """
        # Titre du prix
        award_title = self.font_medium.render(title, True, (255, 215, 0))
        self.screen.blit(award_title, (self.screen.get_width() // 2 - award_title.get_width() // 2, y))
        
        # Top 3
        y += 50
        podium_colors = [(255, 215, 0), (192, 192, 192), (205, 127, 50)]  # Or, Argent, Bronze
        
        for i, (name, value, tiebreak) in enumerate(ranking[:3]):
            color = podium_colors[i] if i < len(podium_colors) else (255, 255, 255)
            position_text = ["1er", "2ème", "3ème"][i]
            
            text = self.font_small.render(
                f"{position_text}: {name} - {value_formatter((name, value, tiebreak))}",
                True,
                color
            )
            self.screen.blit(text, (self.screen.get_width() // 2 - text.get_width() // 2, y))
            y += 35

