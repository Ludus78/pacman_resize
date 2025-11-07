"""Menu graphique avec pygame pour Pac-Man.

Ce module remplace le menu curses par un menu graphique moderne.
"""
import pygame
from typing import List, Optional
from game import settings
from game.tournament import tournament_manager
from game.records import records_manager


class Button:
    """Représente un bouton cliquable."""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, font: pygame.font.Font):
        """Initialise un bouton.
        
        Args:
            x, y: Position du bouton
            width, height: Dimensions du bouton
            text: Texte du bouton
            font: Police à utiliser
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = (50, 50, 100)
        self.hover_color = (80, 80, 150)
        self.text_color = (255, 255, 255)
        self.is_hovered = False
    
    def draw(self, screen: pygame.Surface):
        """Dessine le bouton."""
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def update(self, mouse_pos: tuple):
        """Met à jour l'état du bouton."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def is_clicked(self, mouse_pos: tuple) -> bool:
        """Vérifie si le bouton est cliqué."""
        return self.rect.collidepoint(mouse_pos)


class GraphicalMenu:
    """Menu graphique principal avec pygame."""
    
    def __init__(self):
        """Initialise le menu graphique."""
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.APPACTIVE)
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        pygame.display.set_caption("Pac-Man")
        
        self.font_title = pygame.font.Font(None, 120)
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_screen = "main_menu"
    
    def create_centered_buttons(self, labels: List[str], start_y: int, spacing: int = 80) -> List[Button]:
        """Crée une liste de boutons centrés verticalement.
        
        Args:
            labels: Liste des textes des boutons
            start_y: Position Y de départ
            spacing: Espacement entre les boutons
            
        Returns:
            Liste de boutons
        """
        buttons = []
        padding = 80
        max_label_width = 0
        for label in labels:
            rendered = self.font_medium.render(label, True, (0, 0, 0))
            if rendered.get_width() > max_label_width:
                max_label_width = rendered.get_width()
        button_width = max(400, max_label_width + padding)
        button_width = min(button_width, self.screen_width - 120)
        button_height = 60
        
        for i, label in enumerate(labels):
            x = (self.screen_width - button_width) // 2
            y = start_y + i * spacing
            button = Button(x, y, button_width, button_height, label, self.font_medium)
            buttons.append(button)
        
        return buttons
    
    def show_main_menu(self) -> Optional[str]:
        """Affiche le menu principal.
        
        Returns:
            Choix de l'utilisateur
        """
        buttons = self.create_centered_buttons(
            ["JOUER", "MODE TOURNOI", "SCOREBOARD", "PARAMÈTRES", "QUITTER"],
            300
        )
        selected_index = 0
        
        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "QUITTER"
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "QUITTER"
                    
                    elif event.key == pygame.K_UP:
                        selected_index = (selected_index - 1) % len(buttons)
                    
                    elif event.key == pygame.K_DOWN:
                        selected_index = (selected_index + 1) % len(buttons)
                    
                    elif event.key == pygame.K_RETURN:
                        return buttons[selected_index].text
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Clic gauche
                        for i, button in enumerate(buttons):
                            if button.is_clicked(mouse_pos):
                                return button.text
                
                elif event.type == pygame.MOUSEMOTION:
                    # Mettre à jour la sélection basée sur la souris
                    for i, button in enumerate(buttons):
                        if button.rect.collidepoint(mouse_pos):
                            selected_index = i
            
            # Mise à jour
            for i, button in enumerate(buttons):
                button.update(mouse_pos)
                # Marque le bouton sélectionné au clavier
                if i == selected_index:
                    button.is_hovered = True
            
            # Affichage
            self.screen.fill((0, 0, 0))
            
            # Titre
            title = self.font_title.render("PAC-MAN", True, (255, 255, 0))
            title_rect = title.get_rect(center=(self.screen_width // 2, 150))
            self.screen.blit(title, title_rect)
            
            # Boutons
            for button in buttons:
                button.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(60)
        
        return "QUITTER"
    
    def show_settings_menu(self) -> bool:
        """Affiche le menu des paramètres.
        
        Returns:
            True si on retourne au menu principal
        """
        selected_index = 0
        
        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            
            # Crée les boutons à chaque frame pour mettre à jour le texte
            buttons = self.create_centered_buttons([
                f"MODE HARDCORE : {'ON' if settings.hardcore_mode else 'OFF'}",
                f"CODES CHEAT : {'ON' if settings.cheats_enabled else 'OFF'}",
                "RÉINITIALISER TOURNOI",
                "RÉINITIALISER RECORDS",
                "RETOUR"
            ], 250, 90)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return True
                    
                    elif event.key == pygame.K_UP:
                        selected_index = (selected_index - 1) % len(buttons)
                    
                    elif event.key == pygame.K_DOWN:
                        selected_index = (selected_index + 1) % len(buttons)
                    
                    elif event.key == pygame.K_RETURN:
                        if selected_index == 0:  # Hardcore
                            settings.hardcore_mode = not settings.hardcore_mode
                        elif selected_index == 1:  # Cheats
                            settings.cheats_enabled = not settings.cheats_enabled
                        elif selected_index == 2:  # Réinitialiser tournoi
                            tournament_manager.reset()
                        elif selected_index == 3:  # Réinitialiser records
                            records_manager.reset()
                        elif selected_index == 4:  # Retour
                            return True
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for i, button in enumerate(buttons):
                            if button.is_clicked(mouse_pos):
                                if "HARDCORE" in button.text:
                                    settings.hardcore_mode = not settings.hardcore_mode
                                elif "CODES CHEAT" in button.text:
                                    settings.cheats_enabled = not settings.cheats_enabled
                                elif button.text == "RÉINITIALISER TOURNOI":
                                    tournament_manager.reset()
                                elif button.text == "RÉINITIALISER RECORDS":
                                    records_manager.reset()
                                elif button.text == "RETOUR":
                                    return True
                
                elif event.type == pygame.MOUSEMOTION:
                    for i, button in enumerate(buttons):
                        if button.rect.collidepoint(mouse_pos):
                            selected_index = i
            
            # Mise à jour
            for i, button in enumerate(buttons):
                button.update(mouse_pos)
                if i == selected_index:
                    button.is_hovered = True
            
            # Affichage
            self.screen.fill((0, 0, 0))
            
            # Titre
            title = self.font_large.render("PARAMÈTRES", True, (255, 255, 0))
            title_rect = title.get_rect(center=(self.screen_width // 2, 120))
            self.screen.blit(title, title_rect)
            
            # Boutons
            for button in buttons:
                button.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(60)
        
        return False
    
    def get_screen(self) -> pygame.Surface:
        """Retourne l'écran pygame."""
        return self.screen
    
    def quit(self):
        """Ferme le menu."""
        pygame.quit()

