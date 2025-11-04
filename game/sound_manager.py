"""Gestionnaire de son pour le jeu Pacman."""
import os
import pygame.mixer

class SoundManager:
    DEFAULT_MUSIC = "Songretrogaming.mp3"  # Musique par défaut

    def __init__(self):
        """Initialise le gestionnaire de son."""
        # Initialiser pygame.mixer si pas déjà fait
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except Exception:
                print("Impossible d'initialiser le système audio")
                return
        
        self.sound_dir = os.path.join("assets", "sounds")
        # Jouer la musique par défaut au démarrage
        self.start_background_music()

    def start_background_music(self) -> None:
        """Démarre la musique de fond du jeu."""
        music_files = [
            self.DEFAULT_MUSIC,
            "theme.mp3",
            "theme.ogg",
            "theme.wav"
        ]
        
        # Essaie chaque format jusqu'à ce qu'un fonctionne
        for music in music_files:
            if self.play_music(music):
                break

    def play_music(self, filename: str, loop: bool = True) -> bool:
        """Joue un fichier musical en boucle.
        
        Args:
            filename: Nom du fichier dans assets/sounds/
            loop: True pour jouer en boucle, False pour une seule fois
        
        Returns:
            bool: True si le son a pu être joué, False sinon
        """
        try:
            song_path = os.path.join(self.sound_dir, filename)
            if os.path.exists(song_path):
                pygame.mixer.music.load(song_path)
                pygame.mixer.music.play(-1 if loop else 0)
                return True
            return False
        except Exception:
            return False
    
    def stop_music(self):
        """Arrête la musique en cours."""
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass