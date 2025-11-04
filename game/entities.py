from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass
class Position:
    # Représente une position dans le plan (x, y)
    x: int
    y: int


class Entity:
    # Classe de base pour toutes les entités du jeu (possède une position)
    def __init__(self, position: Position) -> None:
        self.position: Position = position

    # Met à jour l'entité (à implémenter dans les sous-classes)
    def update(self, dt: float) -> None:
        pass


class MovableEntity(Entity):
    # Entité qui peut se déplacer (possède une direction et une vitesse)
    def __init__(self, position: Position, direction: Tuple[int, int] | None = None, speed: int = 1) -> None:
        super().__init__(position)
        self.direction: Tuple[int, int] = direction if direction is not None else (0, 0)
        self.speed: int = speed

    # Met à jour la position de l'entité en fonction de la direction et de la vitesse
    def update(self, dt: float) -> None:
        dx = int(self.direction[0] * self.speed * dt)
        dy = int(self.direction[1] * self.speed * dt)
        if dx != 0 or dy != 0:
            self.position = Position(self.position.x + dx, self.position.y + dy)


class Pacman(MovableEntity):
    # Représente Pacman, contrôlé par le joueur
    def __init__(self, position: Position, speed: int = 100) -> None:
        """Initialise Pacman.

        position: Position en pixels (x, y).
        speed: vitesse en pixels par seconde.
        """
        # MovableEntity expects speed as int and direction tuple
        super().__init__(position=position, direction=(0, 0), speed=speed)
        # direction actuelle (unitaire sur x ou y) et direction désirée
        self.desired_direction: tuple[int, int] = (0, 0)

    def set_desired_direction(self, dx: int, dy: int) -> None:
        """Demande un changement de direction. N'autorise pas les diagonales.

        Seules les directions (1,0), (-1,0), (0,1), (0,-1) ou (0,0) sont acceptées.
        """
        # Normaliser pour n'autoriser qu'une seule composante non nulle
        if dx != 0:
            dy = 0
            dx = 1 if dx > 0 else -1
        elif dy != 0:
            dx = 0
            dy = 1 if dy > 0 else -1
        else:
            dx, dy = 0, 0

        self.desired_direction = (dx, dy)

    def update(self, dt: float) -> None:
        """Met à jour la position de Pacman en appliquant la direction désirée si présente.

        Cette méthode applique un mouvement en 4 directions. Si une direction désirée
        est définie, elle devient la direction active. Le mouvement reste sur les
        axes (pas de diagonales).
        dt: temps écoulé en secondes.
        """
        # Si une direction est demandée, l'appliquer (priorité au joueur)
        if self.desired_direction != (0, 0):
            self.direction = self.desired_direction

        # Appeler la logique de déplacement de la classe parente
        super().update(dt)

    # Méthode utilitaire pour obtenir la position en tuple
    def get_position(self) -> tuple[int, int]:
        return (self.position.x, self.position.y)


class Ghost(MovableEntity):
    # Représente un fantôme, adversaire de Pacman
    def __init__(self, position: Position, color: str = "red", **kwargs) -> None:
        super().__init__(position, **kwargs)
        self.color: str = color


class Pellet(Entity):
    # Pastille que Pacman peut manger pour gagner des points
    def __init__(self, position: Position, value: int = 1) -> None:
        super().__init__(position)
        self.value: int = value


class PowerPellet(Pellet):
    # Pastille spéciale donnant un pouvoir temporaire à Pacman
    def __init__(self, position: Position) -> None:
        super().__init__(position, value=10)


class Token(Entity):
    # Jeton bonus/malus (à définir)
    pass
