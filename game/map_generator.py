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


def _flood_fill(grid: List[List[str]], start_x: int, start_y: int, visited: set[Tuple[int, int]]) -> None:
    """Utilise un flood fill pour marquer toutes les cases accessibles depuis un point de départ."""
    h = len(grid)
    w = len(grid[0])
    stack = [(start_x, start_y)]
    
    while stack:
        x, y = stack.pop()
        if (x, y) in visited or grid[y][x] == '#':
            continue
        visited.add((x, y))
        
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] != '#' and (nx, ny) not in visited:
                stack.append((nx, ny))

def _find_disconnected_regions(grid: List[List[str]]) -> List[Tuple[int, int]]:
    """Trouve les régions déconnectées et retourne un point de chaque région."""
    h = len(grid)
    w = len(grid[0])
    visited = set()
    regions = []

    # Trouve le premier point non-mur comme point de départ
    start = None
    for y in range(h):
        for x in range(w):
            if grid[y][x] != '#':
                start = (x, y)
                break
        if start:
            break
    
    if not start:
        return []

    # Premier flood fill pour marquer la région principale
    _flood_fill(grid, start[0], start[1], visited)

    # Cherche d'autres régions non connectées
    for y in range(h):
        for x in range(w):
            if grid[y][x] != '#' and (x, y) not in visited:
                regions.append((x, y))
                _flood_fill(grid, x, y, visited)

    return regions

def _count_wall_neighbors(grid: List[List[str]], x: int, y: int) -> int:
    """Compte le nombre de murs autour d'une case."""
    count = 0
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        nx, ny = x + dx, y + dy
        if grid[ny][nx] == '#':
            count += 1
    return count

def _is_corridor(grid: List[List[str]], x: int, y: int) -> bool:
    """Vérifie si une case fait partie d'un corridor (2 murs opposés)."""
    if grid[y][x] == '#':
        return False
    h_walls = (grid[y][x-1] == '#' and grid[y][x+1] == '#')
    v_walls = (grid[y-1][x] == '#' and grid[y+1][x] == '#')
    return h_walls or v_walls

def _reduce_dead_ends(grid: List[List[str]], rng: random.Random, *, max_passes: int = 6) -> None:
    """
    Améliore la connectivité et élimine les impasses:
    - Détecte et ouvre les cul-de-sacs
    - Crée des connexions alternatives pour les corridors
    - Assure des chemins multiples
    """
    h = len(grid)
    if h == 0:
        return
    w = len(grid[0])

    for _ in range(max_passes):
        changes = 0
        
        # 1. Détection améliorée des impasses
        dead_ends = []
        corridors = []
        
        for y in range(1, h-1):
            for x in range(1, w-1):
                if grid[y][x] != '#':
                    open_count = _open_neighbors_count(grid, x, y)
                    wall_count = _count_wall_neighbors(grid, x, y)
                    
                    # Détecte les cul-de-sacs
                    if open_count == 1:
                        dead_ends.append((x, y))
                    # Détecte les corridors isolés
                    elif open_count == 2 and _is_corridor(grid, x, y):
                        corridors.append((x, y))
        
        # 2. Traitement des cul-de-sacs
        rng.shuffle(dead_ends)
        for x, y in dead_ends:
            if _open_neighbors_count(grid, x, y) != 1:
                continue
            
            # Ouvre au moins deux nouvelles directions
            neighbors = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            rng.shuffle(neighbors)
            
            # Trouve la direction ouverte existante
            open_dir = next((dir for dir in neighbors 
                           if grid[y + dir[1]][x + dir[0]] != '#'), None)
            
            # Compte les nouvelles ouvertures créées
            new_openings = 0
            for dx, dy in neighbors:
                if (dx, dy) != open_dir:
                    nx, ny = x + dx, y + dy
                    if 0 < nx < w-1 and 0 < ny < h-1 and grid[ny][nx] == '#':
                        grid[ny][nx] = ' '
                        changes += 1
                        new_openings += 1
                        if new_openings >= 2:  # Assure au moins deux nouvelles connexions
                            break
        
        # 3. Amélioration des corridors
        rng.shuffle(corridors)
        for x, y in corridors:
            if not _is_corridor(grid, x, y):
                continue
                
            # Tente d'ouvrir une connexion diagonale pour créer des chemins alternatifs
            diagonals = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            rng.shuffle(diagonals)
            
            for dx, dy in diagonals:
                nx, ny = x + dx, y + dy
                if (0 < nx < w-1 and 0 < ny < h-1 and 
                    grid[ny][nx] == '#' and 
                    _count_wall_neighbors(grid, nx, ny) >= 3):
                    # Crée un passage en ouvrant la diagonale et un chemin vers elle
                    grid[ny][nx] = ' '
                    grid[y][ny] = ' '
                    grid[ny][x] = ' '
                    changes += 1
                    break
        
        # 2. Connecte les régions isolées
        disconnected = _find_disconnected_regions(grid)
        for x, y in disconnected:
            # Cherche le chemin le plus court vers une région connectée
            shortest_path = None
            min_dist = float('inf')
            
            for dy in range(-3, 4):
                for dx in range(-3, 4):
                    nx, ny = x + dx, y + dy
                    if 0 < nx < w-1 and 0 < ny < h-1:
                        if grid[ny][nx] != '#' and (nx, ny) not in disconnected:
                            dist = abs(dx) + abs(dy)
                            if dist < min_dist:
                                min_dist = dist
                                shortest_path = (dx, dy)
            
            if shortest_path:
                dx, dy = shortest_path
                # Crée un passage direct
                curr_x, curr_y = x, y
                while (curr_x, curr_y) != (x + dx, y + dy):
                    if abs(curr_x - (x + dx)) > abs(curr_y - (y + dy)):
                        curr_x += 1 if dx > 0 else -1
                    else:
                        curr_y += 1 if dy > 0 else -1
                    grid[curr_y][curr_x] = ' '
                changes += 1
        
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
    - Salles et connexions additionnelles pour plus de diversité
    - Optimisation poussée de la connectivité et élimination des impasses
    - Placement de P, G, pastilles '.' et super pastilles 'o'
    - Retourne List[str] utilisable par GameMap(rows)
    """
    rng = random.Random(seed)
    # Garantit des dimensions minimales raisonnables
    width = max(15, width)
    height = max(11, height)

    while True:
        grid = _carve_maze(width, height, rng)
        
        # Ajoute quelques salles pour diversifier
        _sprinkle_rooms(grid, room_attempts=3, rng=rng)
        
        # Plusieurs passes d'amélioration de la connectivité
        for _ in range(2):
            _reduce_dead_ends(grid, rng, max_passes=6)
            
            # Vérifie qu'il ne reste pas trop d'impasses
            dead_ends = sum(1 for y in range(1, height-1) 
                          for x in range(1, width-1)
                          if grid[y][x] != '#' and _open_neighbors_count(grid, x, y) == 1)
            
            # Si moins de 5% d'impasses, la carte est acceptable
            if dead_ends <= (width * height * 0.05):
                break
        
        # Vérifie que la carte est complètement connectée
        if not _find_disconnected_regions(grid):
            break  # Carte valide trouvée
        # Sinon, réessaye avec une nouvelle carte
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


