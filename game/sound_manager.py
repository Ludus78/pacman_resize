"""Gestionnaire des sons du jeu Pacman.

Ce module gère le chargement et la lecture des effets sonores
et de la musique de fond du jeu.
"""
import pygame
import os
from pathlib import Path
from typing import Optional, Dict


class SoundManager:
    """Gère tous les sons du jeu."""
    
    def __init__(self):
        """Initialise le gestionnaire de sons."""
        pygame.mixer.init()
        
        # Chemin vers le dossier des assets
        self.assets_path = Path(__file__).parent.parent / "assets" / "sounds"
        
        # Dictionnaires pour stocker les sons
        self.sounds: Dict[str, Optional[pygame.mixer.Sound]] = {
            'pellet_eat': None,        # Quand Pacman mange une pastille
            'power_pellet': None,      # Quand Pacman mange une super-pastille
            'ghost_eaten': None,       # Quand Pacman mange un fantôme
            'death': None,             # Quand Pacman meurt
            'victory': None,           # Quand le niveau est terminé
            'background': None,        # Musique de fond
        }
        
        self.background_music_playing = False
        self._load_sounds()
    
    def _load_sounds(self) -> None:
        """Charge tous les fichiers son disponibles."""
        sound_files = {
            'pellet_eat': ['pellet.wav', 'eat_pellet.wav', 'chomp.wav'],
            'power_pellet': ['power_pellet.wav', 'power.wav', 'boost.wav'],
            'ghost_eaten': ['ghost_eaten.wav', 'eat_ghost.wav', 'ghost.wav'],
            'death': ['death.wav', 'die.wav', 'gameover.wav'],
            'victory': ['victory.wav', 'level_complete.wav', 'win.wav'],
            'background': ['background.wav', 'music.wav', 'theme.wav'],
        }
        
        for sound_name, filenames in sound_files.items():
            for filename in filenames:
                sound_path = self.assets_path / filename
                if sound_path.exists():
                    try:
                        self.sounds[sound_name] = pygame.mixer.Sound(str(sound_path))
                        print(f"✓ Son chargé: {sound_name} ({filename})")
                        break
                    except pygame.error as e:
                        print(f"✗ Erreur lors du chargement de {filename}: {e}")
            
            if self.sounds[sound_name] is None:
                print(f"⚠ Pas de fichier trouvé pour: {sound_name}")
    
    def play_pellet_eat(self) -> None:
        """Joue le son de Pacman mangeant une pastille."""
        if self.sounds['pellet_eat']:
            self.sounds['pellet_eat'].play()
    
    def play_power_pellet(self) -> None:
        """Joue le son de Pacman mangeant une super-pastille."""
        if self.sounds['power_pellet']:
            self.sounds['power_pellet'].play()
    
    def play_ghost_eaten(self) -> None:
        """Joue le son d'un fantôme mangé.
        
        Coupe et recommence le son à chaque appel pour plus de fluidité.
        """
        if self.sounds['ghost_eaten']:
            # Arrête le son s'il est en cours de lecture pour le recommencer
            self.sounds['ghost_eaten'].stop()
            # Joue le son depuis le début
            self.sounds['ghost_eaten'].play()
    
    def play_death(self) -> None:
        """Joue le son de mort de Pacman."""
        if self.sounds['death']:
            self.sounds['death'].play()
    
    def play_victory(self) -> None:
        """Joue le son de victoire du niveau."""
        if self.sounds['victory']:
            self.sounds['victory'].play()
    
    def play_background_music(self) -> None:
        """Lance la musique de fond en boucle."""
        if self.sounds['background'] and not self.background_music_playing:
            self.sounds['background'].play(-1)  # -1 = boucle infinie
            self.background_music_playing = True
    
    def stop_background_music(self) -> None:
        """Arrête la musique de fond."""
        if self.sounds['background']:
            self.sounds['background'].stop()
            self.background_music_playing = False
    
    def set_music_volume(self, volume: float) -> None:
        """Définit le volume de la musique de fond.
        
        Args:
            volume: Volume entre 0.0 et 1.0
        """
        if self.sounds['background']:
            self.sounds['background'].set_volume(max(0.0, min(1.0, volume)))
    
    def set_effects_volume(self, volume: float) -> None:
        """Définit le volume des effets sonores.
        
        Args:
            volume: Volume entre 0.0 et 1.0
        """
        volume = max(0.0, min(1.0, volume))
        for sound_name in ['pellet_eat', 'power_pellet', 'ghost_eaten', 'death', 'victory']:
            if self.sounds[sound_name]:
                self.sounds[sound_name].set_volume(volume)
    
    def stop_all(self) -> None:
        """Arrête tous les sons."""
        pygame.mixer.stop()
        self.background_music_playing = False
    
    def cleanup(self) -> None:
        """Nettoie les ressources sonores."""
        self.stop_all()
