"""Gestion du score pour Pacman.

Cette classe encapsule la logique de comptage de points afin de pouvoir être
réutilisée aussi bien par le joueur que par d'éventuels fantômes ou autres
composants du jeu.
"""
from __future__ import annotations


class Score:
    """Représente un compteur de score simple (non négatif)."""

    def __init__(self) -> None:
        # Initialise le score à zéro.
        self._value: int = 0

    @property
    def value(self) -> int:
        # Retourne la valeur actuelle du score.
        return self._value

    def add(self, amount: int = 1) -> None:
        # Ajoute un certain nombre de points au score.
        if amount < 0:
            raise ValueError("Le nombre de points ajouté doit être positif.")
        self._value += amount

    def reset(self) -> None:
        # Remet le score à zéro.
        self._value = 0

    def __int__(self) -> int:
        # Retourne la valeur du score sous forme d'entier.
        return self._value

    def __str__(self) -> str:
        # Retourne le score formaté avec cinq chiffres.
        return f"{self._value:05d}"
