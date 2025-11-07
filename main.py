"""Point d'entrée principal du jeu Pacman.

Ce module lance le menu principal et démarre la partie de jeu.
"""
import pygame
from game.gui_menu import GraphicalMenu
from game.game_loop import GameLoop
from game.tournament import tournament_manager
from game.tournament_ui import TournamentUI
from game.records import records_manager


def run_tournament_mode(menu: GraphicalMenu):
    """Lance le mode tournoi.
    
    Args:
        menu: Instance du menu graphique pour réutiliser l'écran
    """
    screen = menu.get_screen()
    ui = TournamentUI(screen)
    
    # Écran d'inscription
    if not ui.show_registration_screen():
        return
    
    # Démarre le tournoi
    if not tournament_manager.start_tournament():
        return
    
    # Boucle du tournoi
    while tournament_manager.is_active:
        player = tournament_manager.get_current_player()
        if not player:
            break
        
        # Écran d'attente du joueur
        if not ui.show_player_ready_screen():
            return
        
        # Lance une partie (réutilise l'écran existant)
        game_loop = GameLoop(tournament_mode=True, existing_screen=screen)
        result = game_loop.run()
        
        # Recrée l'UI tournoi (garde le même écran)
        ui = TournamentUI(screen)
        
        # Enregistre la tentative
        if result:
            score, level, time_level1, level1_completed = result
            tournament_manager.record_attempt(score, level, time_level1, level1_completed)
        
        # Passe au joueur suivant ou termine
        has_next, is_finished = tournament_manager.next_player_or_finish()
        
        if is_finished:
            # Met à jour les records globaux
            _update_records_from_tournament()
            
            # Affiche les résultats
            ui.show_results_screen()
            break


def _update_records_from_tournament():
    """Met à jour les records globaux à partir des résultats du tournoi."""
    for player in tournament_manager.players:
        if not player.attempts:
            continue
        
        # Calcul du total de points pour départage
        total_score = sum(a.score for a in player.attempts)
        
        # Vérifier le meilleur score
        max_score = player.get_max_score()
        records_manager.check_and_update_score(player.name, max_score, total_score)
        
        # Vérifier le meilleur niveau
        max_level = player.get_max_level()
        records_manager.check_and_update_level(player.name, max_level, total_score)
        
        # Vérifier le meilleur temps niveau 1
        best_time = player.get_best_level1_time()
        if best_time is not None:
            records_manager.check_and_update_time(player.name, best_time, total_score)


def show_scoreboard(menu: GraphicalMenu):
    """Affiche le tableau des records.
    
    Args:
        menu: Instance du menu graphique pour réutiliser l'écran
    """
    screen = menu.get_screen()
    
    font_large = pygame.font.Font(None, 72)
    font_medium = pygame.font.Font(None, 48)
    font_small = pygame.font.Font(None, 36)
    font_tiny = pygame.font.Font(None, 24)
    
    clock = pygame.time.Clock()
    
    while True:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    return
        
        # Affichage
        screen.fill((0, 0, 0))
        
        # Titre
        title = font_large.render("TABLEAU DES RECORDS", True, (255, 215, 0))
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 50))
        
        records = records_manager.get_all_records()
        y_offset = 200
        
        # Record de score
        record_title = font_medium.render("🏆 MEILLEUR SCORE", True, (255, 215, 0))
        screen.blit(record_title, (screen.get_width() // 2 - record_title.get_width() // 2, y_offset))
        y_offset += 60
        
        if records['best_score']:
            rec = records['best_score']
            text = font_small.render(f"{rec.player_name} - {int(rec.value)} points", True, (255, 255, 255))
            screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, y_offset))
        else:
            text = font_small.render("Aucun record", True, (150, 150, 150))
            screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, y_offset))
        y_offset += 100
        
        # Record de niveau
        record_title = font_medium.render("🎖️ NIVEAU MAXIMUM", True, (192, 192, 192))
        screen.blit(record_title, (screen.get_width() // 2 - record_title.get_width() // 2, y_offset))
        y_offset += 60
        
        if records['best_level']:
            rec = records['best_level']
            text = font_small.render(f"{rec.player_name} - Niveau {int(rec.value)}", True, (255, 255, 255))
            screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, y_offset))
        else:
            text = font_small.render("Aucun record", True, (150, 150, 150))
            screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, y_offset))
        y_offset += 100
        
        # Record de temps
        record_title = font_medium.render("⚡ NIVEAU 1 LE PLUS RAPIDE", True, (205, 127, 50))
        screen.blit(record_title, (screen.get_width() // 2 - record_title.get_width() // 2, y_offset))
        y_offset += 60
        
        if records['best_time_level1']:
            rec = records['best_time_level1']
            text = font_small.render(f"{rec.player_name} - {rec.value:.2f}s", True, (255, 255, 255))
            screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, y_offset))
        else:
            text = font_small.render("Aucun record", True, (150, 150, 150))
            screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, y_offset))
        
        # Instructions
        inst = font_tiny.render("Appuyez sur ENTRÉE ou ÉCHAP pour retourner au menu", True, (200, 200, 200))
        screen.blit(inst, (screen.get_width() // 2 - inst.get_width() // 2, screen.get_height() - 50))
        
        pygame.display.flip()


def main() -> None:
    """Point d'entrée du jeu Pacman.
    
    Affiche le menu principal et lance le jeu selon le choix de l'utilisateur.
    """
    # Crée le menu graphique (une seule fenêtre pour toute l'application)
    menu = GraphicalMenu()
    
    while menu.running:
        # Affiche le menu principal et attend un choix
        choix = menu.show_main_menu()
        
        if choix == "JOUER":
            # Lance la boucle de jeu normale en réutilisant l'écran du menu
            game_loop = GameLoop(tournament_mode=False, existing_screen=menu.get_screen())
            game_loop.run()
            # Pas besoin de réinitialiser pygame, on garde la même fenêtre
        
        elif choix == "MODE TOURNOI":
            # Lance le mode tournoi
            run_tournament_mode(menu)
            # Pas besoin de réinitialiser, on garde la même fenêtre
        
        elif choix == "SCOREBOARD":
            # Affiche le tableau des records
            show_scoreboard(menu)
        
        elif choix == "PARAMÈTRES":
            # Ouvre les paramètres
            menu.show_settings_menu()
        
        elif choix == "QUITTER":
            break
    
    # Ferme proprement
    menu.quit()


if __name__ == "__main__":
    main()
