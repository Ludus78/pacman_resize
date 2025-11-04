from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple
import random


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
    """
    Pacman contrôlé par le joueur : il bouge en continu dans sa direction actuelle.
    Les flèches ou touches modifient sa direction désirée. Pacman ne s'arrête jamais
    sauf blocage complet, il rebondit/demande la direction jusqu'à ce qu'une case 
    libre soit trouvée, à la manière des Pacman classiques.
    """
    def __init__(self, position: Position, speed: int = 4) -> None:
        super().__init__(position=position, direction=(0, 0), speed=speed)
        # Direction vers laquelle Pacman souhaite tourner (set_désirée par keypress)
        self.desired_direction: tuple[int, int] = (0, 0)

    def set_desired_direction(self, dx: int, dy: int) -> None:
        """
        Met à jour la direction désirée selon la touche pressée (seulement une des 4 directions cardinales).
        """
        if dx != 0:
            self.desired_direction = (1 if dx > 0 else -1, 0)
        elif dy != 0:
            self.desired_direction = (0, 1 if dy > 0 else -1)
        else:
            self.desired_direction = (0, 0)

    def update(self, dt: float, game_map=None) -> None:
        """
        Fait bouger Pacman à chaque update, si possible.
        Applique en priorité la desired_direction dès qu'elle est possible,
        sinon continue tout droit dans direction actuelle. S'arrête uniquement
        si aucune des deux directions n'est possible (dans un coin).
        """
        # Calcul de la direction vers laquelle on souhaite tourner
        ddx, ddy = self.desired_direction
        cdx, cdy = self.direction

        moved = False

        def can_move(d):
            nx = self.position.x + d[0]
            ny = self.position.y + d[1]
            return self.can_move_to(nx, ny, game_map)

        # Tente de tourner dès que possible dans la direction désirée
        if (ddx, ddy) != (0, 0) and can_move((ddx, ddy)):
            self.direction = (ddx, ddy)
            cdx, cdy = self.direction  # On actualise direction courante pour ce tick

        if (cdx, cdy) != (0, 0) and can_move((cdx, cdy)):
            # Applique le déplacement à la vitesse demandée (en pas unitaires)
            steps = int(self.speed * dt)
            for _ in range(steps):
                nx = self.position.x + cdx
                ny = self.position.y + cdy
                if self.can_move_to(nx, ny, game_map):
                    self.position = Position(nx, ny)
                    moved = True
                else:
                    break
        else:
            # Aucun mouvement possible, Pacman est bloqué ; on arrête son déplacement
            self.direction = (0, 0)

    def can_move_to(self, x: int, y: int, game_map) -> bool:
        """
        Retourne True si la case (x, y) est libre ; utilise # comme mur et fallback méthodes usuelles.
        """
        grid = getattr(game_map, "MAP", None)
        if grid is None and isinstance(game_map, (list, tuple)):
            grid = game_map

        if isinstance(grid, (list, tuple)) and len(grid) > 0:
            if y < 0 or y >= len(grid):
                return False
            row = grid[y]
            if x < 0 or x >= len(row):
                return False
            return row[x] != "#"

        for method in ("is_wall", "is_blocked"):
            fn = getattr(game_map, method, None)
            if callable(fn):
                try:
                    return not fn(x, y)
                except Exception:
                    continue
        fn = getattr(game_map, "get_tile", None)
        if callable(fn):
            try:
                return fn(x, y) != "#"
            except Exception:
                pass

        return True

    def get_position(self) -> tuple[int, int]:
        return (self.position.x, self.position.y)
    # Représente Pacman, contrôlé par le joueur
    def __init__(self, position: Position, **kwargs) -> None:
        super().__init__(position, **kwargs)
        from .score import Score  # import local pour éviter les dépendances circulaires
        self.score: Score = Score()

    def add_points(self, amount: int) -> None:
        """Ajoute *amount* points au score du joueur."""
        self.score.add(amount)

    def reset_score(self) -> None:
        self.score.reset()


class Ghost(MovableEntity):
    # Représente un fantôme, adversaire de Pacman
    def __init__(self, position: Position, color: str = "red", **kwargs) -> None:
        # Initialise le fantôme avec une position, une couleur et des paramètres de déplacement
        super().__init__(position, **kwargs)
        self.color: str = color
        # probabilité de changer de direction
        self.change_dir_chance: float = 0.2

    def can_move_to(self, x: int, y: int, game_map) -> bool:
        """
        Retourne True si la case (x,y) est libre selon la même logique que Pacman.
        """
        grid = getattr(game_map, "MAP", None)
        if grid is None and isinstance(game_map, (list, tuple)):
            grid = game_map

        if isinstance(grid, (list, tuple)) and len(grid) > 0:
            if y < 0 or y >= len(grid):
                return False
            row = grid[y]
            if x < 0 or x >= len(row):
                return False
            return row[x] != "#"

        for method in ("is_wall", "is_blocked"):
            fn = getattr(game_map, method, None)
            if callable(fn):
                try:
                    return not fn(x, y)
                except Exception:
                    continue
        fn = getattr(game_map, "get_tile", None)
        if callable(fn):
            try:
                return fn(x, y) != "#"
            except Exception:
                pass

        return True

    def _available_moves(self, game_map):
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        res = []
        for d in dirs:
            nx = self.position.x + d[0]
            ny = self.position.y + d[1]
            if self.can_move_to(nx, ny, game_map):
                res.append(d)
        return res

    def update(self, dt: float, game_map=None) -> None:
        """
        Déplacement aléatoire respectant la carte : à chaque pas (tuile) on
        calcule les directions disponibles et on en choisit une au hasard
        On essaie de conserver la direction courante la plupart du temps
        """
        steps = int(self.speed * dt) if dt > 0 else 0
        if steps <= 0:
            return

        for _ in range(steps):
            # directions possibles depuis la position actuelle
            moves = self._available_moves(game_map)
            if not moves:
                self.direction = (0, 0)
                return

            # si la direction courante est possible, on essaye de la continuer
            if self.direction in moves and random.random() > self.change_dir_chance:
                choice = self.direction
            else:
                choice = random.choice(moves)

            self.direction = choice
            nx = self.position.x + self.direction[0]
            ny = self.position.y + self.direction[1]
            if self.can_move_to(nx, ny, game_map):
                self.position = Position(nx, ny)
            else:
                # si finalement bloqué, invalide la direction pour le prochain tick
                self.direction = (0, 0)


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
