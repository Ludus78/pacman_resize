"""Fonctions utilitaires pour le jeu Pacman.

Ce module contient diverses fonctions helper utilisées dans le jeu.
"""
import os
import sys
import pygame
from typing import Tuple


def resource_path(rel_path: str) -> str:
    """Helper pour PyInstaller : retourne le chemin absolu vers une ressource.
    
    Gère les cas où le jeu est lancé depuis le code source ou depuis
    un bundle PyInstaller (utilise _MEIPASS).
    
    Args:
        rel_path: Chemin relatif vers la ressource
        
    Returns:
        Chemin absolu vers la ressource
    """
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel_path)


def get_ghost_points(combo_count: int) -> int:
    """Retourne les points pour un fantôme selon le nombre de fantômes mangés à la suite.
    
    Args:
        combo_count: Nombre de fantômes déjà mangés dans le combo actuel
        
    Returns:
        Nombre de points pour ce fantôme
    """
    from game.constants import GHOST_POINTS
    
    if combo_count < len(GHOST_POINTS):
        return GHOST_POINTS[combo_count]
    # Si plus de 4 fantômes, reste à 80 points
    return GHOST_POINTS[-1]


def wait_for_enter(screen: pygame.Surface, clock: pygame.time.Clock) -> bool:
    """Attend l'appui sur Entrée pour relancer la manche.
    
    Args:
        screen: Surface pygame pour le rendu
        clock: Horloge pygame
        
    Returns:
        True si Enter (ou pavé numérique Enter) est pressé,
        False si Échap ou fermeture de la fenêtre
    """
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return True
                if ev.key == pygame.K_ESCAPE:
                    return False
        # On garde un léger rythme pour rester réactif sans cramer le CPU
        clock.tick(30)


def wait_for_button_or_enter(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    button_rect: pygame.Rect
) -> bool:
    """Attend un clic sur un bouton rectangulaire ou Entrée.
    
    Args:
        screen: Surface pygame pour le rendu
        clock: Horloge pygame
        button_rect: Rectangle définissant la zone du bouton
        
    Returns:
        True si l'utilisateur valide (clic dans le bouton ou Entrée),
        False si Échap ou fermeture de la fenêtre
    """
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return True
                if ev.key == pygame.K_ESCAPE:
                    return False
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if button_rect.collidepoint(ev.pos):
                    return True
        clock.tick(30)


def load_map_file(path: str) -> list[str]:
    """Charge une carte depuis un fichier .map.
    
    Args:
        path: Chemin vers le fichier de carte
        
    Returns:
        Liste de lignes représentant la carte, ou liste vide si erreur
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [line.rstrip("\n") for line in f]
    except OSError:
        return []


def format_time(elapsed_time: float) -> str:
    """Formate le temps écoulé en format MM:SS.
    
    Args:
        elapsed_time: Temps écoulé en secondes
        
    Returns:
        Chaîne formatée "MM:SS"
    """
    mm = int(elapsed_time) // 60
    ss = int(elapsed_time) % 60
    return f"{mm:02d}:{ss:02d}"

