from __future__ import annotations

import random
from typing import List, Tuple


def _blank_grid(width: int, height: int, fill: str = "#") -> List[List[str]]:
    return [[fill for _ in range(width)] for _ in range(height)]


def _neighbors(x: int, y: int) -> Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int]]:
    return ((x + 2, y), (x - 2, y), (x, y + 2), (x, y - 2))


def _carve_maze(width: int, height: int, rng: random.Random) -> List[List[str]]:
    # Dimensions impaires pour un maze parfait
    w = width if width % 2 == 1 else width - 1
    h = height if height % 2 == 1 else height - 1
    grid = _blank_grid(w, h, '#')

    # Point de départ au hasard sur la grille impaire
    sx = rng.randrange(1, w, 2)
    sy = rng.randrange(1, h, 2)
    grid[sy][sx] = ' '

    stack: List[Tuple[int, int]] = [(sx, sy)]
    while stack:
        x, y = stack[-1]
        dirs = list(_neighbors(x, y))
        rng.shuffle(dirs)
        carved = False
        for nx, ny in dirs:
            if 1 <= nx < w - 1 and 1 <= ny < h - 1 and grid[ny][nx] == '#':
                mx = (x + nx) // 2
                my = (y + ny) // 2
                grid[my][mx] = ' '
                grid[ny][nx] = ' '
                stack.append((nx, ny))
                carved = True
                break
        if not carved:
            stack.pop()

    return grid


def _sprinkle_rooms(grid: List[List[str]], room_attempts: int, rng: random.Random) -> None:
    h = len(grid)
    w = len(grid[0]) if h else 0
    for _ in range(room_attempts):
        # Réduire la taille des "salles" pour éviter des couloirs/espaces trop larges
        rw = rng.randint(3, 5)
        rh = rng.randint(3, 4)
        rx = rng.randint(1, max(1, w - rw - 2))
        ry = rng.randint(1, max(1, h - rh - 2))
        for y in range(ry, min(h - 1, ry + rh)):
            for x in range(rx, min(w - 1, rx + rw)):
                grid[y][x] = ' '


def _open_neighbors_count(grid: List[List[str]], x: int, y: int) -> int:
    h = len(grid)
    w = len(grid[0]) if h else 0
    cnt = 0
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] != '#':
            cnt += 1
    return cnt


def _reduce_dead_ends(grid: List[List[str]], rng: random.Random, *, max_passes: int = 3) -> None:
    """
    Évite les voies sans issue en connectant les cul-de-sacs:
    - Pour chaque case ouverte avec un seul voisin ouvert, on ouvre une paroi adjacente
      supplémentaire afin d'obtenir au moins deux sorties.
    - On répète quelques passes pour propager l'effet et réduire fortement les cul-de-sacs.
    """
    h = len(grid)
    if h == 0:
        return
    w = len(grid[0])

    for _ in range(max_passes):
        changes = 0
        # Liste des dead-ends actuels
        dead_ends: List[Tuple[int, int]] = []
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                if grid[y][x] != '#':
                    if _open_neighbors_count(grid, x, y) == 1:
                        dead_ends.append((x, y))

        rng.shuffle(dead_ends)
        for x, y in dead_ends:
            if _open_neighbors_count(grid, x, y) != 1:
                continue
            # Choisir une paroi à ouvrir qui n'est pas déjà le seul voisin ouvert
            neighbors = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            rng.shuffle(neighbors)
            # Identifier la direction du seul voisin ouvert pour l'éviter si possible
            open_dir = None
            for dx, dy in neighbors:
                if grid[y + dy][x + dx] != '#':
                    open_dir = (dx, dy)
                    break

            for dx, dy in neighbors:
                if open_dir is not None and (dx, dy) == open_dir:
                    continue
                nx, ny = x + dx, y + dy
                if 0 < nx < w - 1 and 0 < ny < h - 1 and grid[ny][nx] == '#':
                    # Ouvre cette paroi pour créer une connexion
                    grid[ny][nx] = ' '
                    changes += 1
                    break
        if changes == 0:
            break

def _place_entities(grid: List[List[str]], num_ghosts: int, rng: random.Random) -> None:
    h = len(grid)
    w = len(grid[0]) if h else 0
    floor: List[Tuple[int, int]] = [(x, y) for y in range(h) for x in range(w) if grid[y][x] == ' ']
    if not floor:
        return

    # Place Pacman start 'P'
    px, py = rng.choice(floor)
    grid[py][px] = 'P'

    # Place ghosts 'G'
    rng.shuffle(floor)
    placed = 0
    for x, y in floor:
        if (x, y) == (px, py):
            continue
        if placed >= num_ghosts:
            break
        # Keep some distance from P if possible
        if abs(x - px) + abs(y - py) < 6:
            continue
        grid[y][x] = 'G'
        placed += 1


def _place_pellets(grid: List[List[str]], rng: random.Random) -> None:
    h = len(grid)
    w = len(grid[0]) if h else 0
    # Regular pellets everywhere else (leave walls and entities intact initially)
    for y in range(h):
        for x in range(w):
            if grid[y][x] == ' ':
                grid[y][x] = '.'

    # Place exactement 4 power pellets 'o'
    def manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    candidates_border = [(x, y) for y in range(h) for x in range(w)
                         if grid[y][x] == '.' and (x < 3 or y < 3 or x > w - 4 or y > h - 4)]
    rng.shuffle(candidates_border)

    placed_positions: list[tuple[int, int]] = []
    # Essayer d'abord les bords avec écart minimal
    for x, y in candidates_border:
        if len(placed_positions) >= 4:
            break
        if all(manhattan((x, y), pos) >= 6 for pos in placed_positions):
            grid[y][x] = 'o'
            placed_positions.append((x, y))

    # Compléter si moins de 4
    if len(placed_positions) < 4:
        candidates_inner = [(x, y) for y in range(h) for x in range(w) if grid[y][x] == '.']
        rng.shuffle(candidates_inner)
        for x, y in candidates_inner:
            if len(placed_positions) >= 4:
                break
            if all(manhattan((x, y), pos) >= 6 for pos in placed_positions):
                grid[y][x] = 'o'
                placed_positions.append((x, y))


def generate_map(width: int, height: int, *, num_ghosts: int = 4, seed: int | None = None) -> List[str]:
    """
    Génère une carte procédurale:
    - Labyrinthe parfait de base (DFS sur grille impaire)
    - Quelques "salles" grossières sculptées dans le labyrinthe
    - Placement de P, G, pastilles '.' et super pastilles 'o'
    - Retourne List[str] utilisable par GameMap(rows)
    """
    rng = random.Random(seed)
    # Garantit des dimensions minimales raisonnables
    width = max(15, width)
    height = max(11, height)

    grid = _carve_maze(width, height, rng)
    # Moins de salles pour limiter les zones trop ouvertes
    _sprinkle_rooms(grid, room_attempts=2, rng=rng)
    # Connecte les cul-de-sacs pour éviter les voies sans issue
    _reduce_dead_ends(grid, rng, max_passes=4)
    _place_entities(grid, num_ghosts=num_ghosts, rng=rng)
    _place_pellets(grid, rng=rng)

    return ["".join(row) for row in grid]


