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
    pass


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
    # Jeton bonus ou objet spécial (à définir selon les besoins)
    pass

