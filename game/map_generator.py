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

def _place_entities(grid: List[List[str]], num_ghosts: int, rng: random.Random, *, cage_center: Tuple[int, int] | None = None) -> None:
    """Place Pacman et les fantômes en garantissant une distance minimale de sécurité.
    
    Args:
        grid: Grille de jeu
        num_ghosts: Nombre de fantômes à placer
        rng: Générateur aléatoire
        cage_center: Centre de la cage pour les fantômes
    """
    h = len(grid)
    w = len(grid[0]) if h else 0
    floor: List[Tuple[int, int]] = [(x, y) for y in range(h) for x in range(w) if grid[y][x] == ' ']
    if not floor:
        return

    def manhattan_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Calcule la distance de Manhattan entre deux positions."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    # Place ghosts 'G' d'abord – privilégie l'intérieur de la cage si présente
    ghost_positions: List[Tuple[int, int]] = []
    positions: List[Tuple[int, int]] = []
    
    if cage_center is not None:
        cx, cy = cage_center
        for y in range(cy - 1, cy + 2):
            for x in range(cx - 1, cx + 2):
                if 0 <= y < h and 0 <= x < w and grid[y][x] == ' ':
                    positions.append((x, y))
    
    if not positions:
        positions = floor.copy()
    
    rng.shuffle(positions)
    
    # Place les fantômes
    for i in range(min(num_ghosts, len(positions))):
        x, y = positions[i]
        grid[y][x] = 'G'
        ghost_positions.append((x, y))

    # Place Pacman dans une zone sûre (distance minimale des fantômes)
    from game.constants import MIN_SAFE_SPAWN_DISTANCE
    
    safe_positions = [
        pos for pos in floor 
        if grid[pos[1]][pos[0]] == ' ' and  # Case encore vide
        all(manhattan_distance(pos, ghost_pos) >= MIN_SAFE_SPAWN_DISTANCE for ghost_pos in ghost_positions)
    ]
    
    if safe_positions:
        # Choisit une position sûre
        px, py = rng.choice(safe_positions)
    else:
        # Fallback : choisit la position la plus éloignée des fantômes
        available = [(x, y) for x, y in floor if grid[y][x] == ' ']
        if available:
            px, py = max(available, key=lambda pos: min(manhattan_distance(pos, gpos) for gpos in ghost_positions))
        else:
            # Dernière chance : n'importe quelle case libre
            px, py = rng.choice(floor)
    
    grid[py][px] = 'P'


def _place_pellets(grid: List[List[str]], rng: random.Random, *, cage_center: Tuple[int, int] | None = None) -> None:
    h = len(grid)
    w = len(grid[0]) if h else 0
    # Regular pellets everywhere else (leave walls and entities intact initially)
    for y in range(h):
        for x in range(w):
            if grid[y][x] == ' ':
                # Évite les pastilles dans/près de la cage (rayon Manhattan 2)
                if cage_center is not None and abs(x - cage_center[0]) + abs(y - cage_center[1]) <= 2:
                    continue
                grid[y][x] = '.'
def _break_2x2_pellets(grid: List[List[str]]) -> None:
    h = len(grid)
    w = len(grid[0]) if h else 0
    changed = True
    while changed:
        changed = False
        for y in range(h - 1):
            for x in range(w - 1):
                block = [grid[y][x], grid[y][x + 1], grid[y + 1][x], grid[y + 1][x + 1]]
                if all(c == '.' for c in block):
                    grid[y + 1][x + 1] = ' '
                    changed = True
                    break
            if changed:
                break

def _add_cage(grid: List[List[str]]) -> Tuple[int, int]:
    """Ajoute une cage 5x5 centrée avec ouverture de 2 blocs en haut et centre 'C'. Retourne (cx, cy)."""
    h = len(grid)
    w = len(grid[0]) if h else 0
    cx = w // 2
    cy = h // 2
    left = max(1, cx - 2)
    right = min(w - 2, cx + 2)
    top = max(1, cy - 2)
    bottom = min(h - 2, cy + 2)
    # Nettoie la zone en murs
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            grid[y][x] = '#'
    # Intérieur vide
    for y in range(top + 1, bottom):
        for x in range(left + 1, right):
            grid[y][x] = ' '
    # Mur périmétrique déjà '#', crée ouverture 2 blocs au haut-centre
    midx = (left + right) // 2
    grid[top][midx] = ' '
    if midx + 1 <= right:
        grid[top][midx + 1] = ' '
    # Assure un couloir au-dessus de l'ouverture
    if top - 1 >= 0:
        grid[top - 1][midx] = ' '
        if midx + 1 < w:
            grid[top - 1][midx + 1] = ' '
    # Centre de cage
    grid[cy][cx] = 'C'
    return (cx, cy)


def _place_power_pellets(grid: List[List[str]], rng: random.Random) -> None:
    """Place exactement 4 power pellets 'o' sur la grille."""
    h = len(grid)
    w = len(grid[0]) if h else 0
    
    def manhattan(a: Tuple[int, int], b: Tuple[int, int]) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    candidates_border = [(x, y) for y in range(h) for x in range(w)
                         if grid[y][x] == '.' and (x < 3 or y < 3 or x > w - 4 or y > h - 4)]
    rng.shuffle(candidates_border)

    placed_positions: List[Tuple[int, int]] = []
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
    # Ajoute la cage 5x5 avec sortie et centre 'C'
    cage_center = _add_cage(grid)
    # Place entités en privilégiant la cage pour les fantômes
    _place_entities(grid, num_ghosts=num_ghosts, rng=rng, cage_center=cage_center)
    # Place pastilles en évitant la cage et casse les carrés 2x2
    _place_pellets(grid, rng=rng, cage_center=cage_center)
    _break_2x2_pellets(grid)
    # Place les 4 power pellets
    _place_power_pellets(grid, rng)

    return ["".join(row) for row in grid]


