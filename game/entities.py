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
    def __init__(self, position: Position, speed: int = 4) -> None:
        """Initialise Pacman.

        position: Position en tuiles (x, y) — colonne, ligne.
        speed: vitesse en tuiles par seconde (par défaut 4 tuiles/s).
        Note: la valeur par défaut a été choisie pour être tile-based. Si ton code
        attend des pixels, ajuste la valeur en conséquence.
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

    def update(self, dt: float, game_map=None) -> None:
        """Met à jour la position de Pacman en appliquant la direction désirée si présente.

        Si `game_map` est fourni, on empêchera Pacman de traverser les murs.
        Le `game_map` peut être :
          - un module/objet ayant un attribut `MAP` (liste de chaînes),
          - ou un objet exposant `is_wall(x, y)` / `is_blocked(x, y)` / `get_tile(x, y)`.

        La fonction supporte des déplacements multiples (si la vitesse produit dx>1),
        en testant chaque pas intermédiaire pour éviter de sauter des murs.

        dt: temps écoulé en secondes.
        """
        # Appliquer la direction désirée si demandée
        if self.desired_direction != (0, 0):
            self.direction = self.desired_direction

        # Calculer le déplacement proposé (utilise la même logique que MovableEntity)
        dx = int(self.direction[0] * self.speed * dt)
        dy = int(self.direction[1] * self.speed * dt)

        # Si pas de carte fournie, déléguer au parent (comportement précédent)
        if game_map is None:
            if dx != 0 or dy != 0:
                self.position = Position(self.position.x + dx, self.position.y + dy)
            return

        # Déplacer en pas unitaires pour éviter de traverser un mur si dx/dy > 1
        steps = max(abs(dx), abs(dy))
        if steps == 0:
            return

        step_x = 0
        step_y = 0
        if dx != 0:
            step_x = 1 if dx > 0 else -1
        if dy != 0:
            step_y = 1 if dy > 0 else -1

        for i in range(1, steps + 1):
            nx = self.position.x + (step_x * i if step_x != 0 else 0)
            ny = self.position.y + (step_y * i if step_y != 0 else 0)

            if not self.can_move_to(nx, ny, game_map):
                # Ne pas entrer dans la case bloquée : placer Pacman juste avant
                # la case bloquée (i-1 pas complets)
                self.position = Position(self.position.x + (step_x * (i - 1) if step_x != 0 else 0),
                                         self.position.y + (step_y * (i - 1) if step_y != 0 else 0))
                return

        # Si toutes les cases intermédiaires sont franchissables, appliquer le déplacement
        self.position = Position(self.position.x + dx, self.position.y + dy)

    def can_move_to(self, x: int, y: int, game_map) -> bool:
        """Retourne True si la case (x, y) est franchissable.

        Le comportement par défaut :
          - si `game_map` a un attribut `MAP` (liste de chaînes), on considère '#'
            comme mur (non franchissable).
          - sinon, on essaie d'appeler des méthodes usuelles (`is_wall`, `is_blocked`,
            `get_tile`) si elles existent.

        x est la colonne, y la ligne (convention compatible avec `assets/maps/map.py`).
        """
        # 1) Si game_map expose MAP (liste de chaînes)
        grid = getattr(game_map, "MAP", None)
        if grid is None:
            # Peut être que game_map est directement la grille
            if isinstance(game_map, (list, tuple)):
                grid = game_map

        if isinstance(grid, (list, tuple)) and len(grid) > 0:
            try:
                # Vérifier bornes
                if y < 0 or y >= len(grid):
                    return False
                row = grid[y]
                if x < 0 or x >= len(row):
                    return False
                return row[x] != "#"
            except Exception:
                # En cas d'erreur, considérer comme bloqué
                return False

        # 2) Vérifier méthodes usuelles sur game_map
        if hasattr(game_map, "is_wall") and callable(game_map.is_wall):
            try:
                return not game_map.is_wall(x, y)
            except Exception:
                pass
        if hasattr(game_map, "is_blocked") and callable(game_map.is_blocked):
            try:
                return not game_map.is_blocked(x, y)
            except Exception:
                pass
        if hasattr(game_map, "get_tile") and callable(game_map.get_tile):
            try:
                return game_map.get_tile(x, y) != "#"
            except Exception:
                pass

        # Si aucun test possible, on renvoie True pour ne pas casser le jeu
        return True

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
