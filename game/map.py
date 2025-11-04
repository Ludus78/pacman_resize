from __future__ import annotations

from typing import List, Optional, Tuple


def load_map(path: str) -> list[str]:
    # Charge une carte depuis un fichier
    lines: List[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            lines.append(line.rstrip("\n"))
    return lines


def draw_map(stdscr, map_data: list[str]) -> None:
    # Affiche la carte dans le terminal en respectant la taille de l'écran
    height, width = stdscr.getmaxyx()
    max_y = max(0, height - 1)
    max_w = max(0, width - 1)
    for y, line in enumerate(map_data):
        if y > max_y:
            break
        safe_line = line[:max_w]
        try:
            stdscr.addstr(y, 0, safe_line)
        except Exception:
            pass


class GameMap:
    # Représente une carte de jeu sous forme de grille, avec détection de murs
    def __init__(self, rows: List[str]) -> None:
        # Initialise la carte
        self.rows: List[str] = rows
        self.height: int = len(rows)
        self.width: int = max((len(r) for r in rows), default=0)

        # Pré-calcule l'ensemble des murs pour des collisions rapides
        self._walls: set[Tuple[int, int]] = set()
        for y, row in enumerate(self.rows):
            for x, ch in enumerate(row):
                if ch == '#':
                    self._walls.add((x, y))

    @classmethod
    def from_file(cls, path: str) -> "GameMap":
        # Charge une carte depuis un fichier
        return cls(load_map(path))

    def is_inside(self, x: int, y: int) -> bool:
        # Est-ce que la position est à l'intérieur de la carte ?
        return 0 <= y < self.height and 0 <= x < len(self.rows[y])

    def is_wall(self, x: int, y: int) -> bool:
        # Est-ce qu'il y a un mur à cette position ?
        return (x, y) in self._walls

    def is_blocked(self, x: int, y: int) -> bool:
        # Bloqué si hors-limites ou mur
        if not self.is_inside(x, y):
            return True
        return self.is_wall(x, y)

    def draw(self, stdscr) -> None:
        # Affiche la carte dans le terminal
        draw_map(stdscr, self.rows)

    def find_char(self, ch: str) -> Optional[Tuple[int, int]]:
        # Trouve la première occurrence d'un caractère dans la carte
        for y, row in enumerate(self.rows):
            x = row.find(ch)
            if x != -1:
                return (x, y)
        return None

    def clear_char(self, ch: str) -> None:
        # Remplace le premier caractère trouvé par un espace pour l'affichage
        pos = self.find_char(ch)
        if pos is None:
            return
        x, y = pos
        row = self.rows[y]
        if 0 <= x < len(row):
            self.rows[y] = row[:x] + ' ' + row[x + 1:]
