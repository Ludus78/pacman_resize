MAP = [
    "####################",
    "#..............#...#",
    "#.####.#####...#.#.#",
    "#....#.....#...#.#.#",
    "####.#.###.#.###.#.#",
    "#....#.#.#.#.....#.#",
    "#.####.#.#.#####.#.#",
    "#......#.#.....#.#.#",
    "######.#.#####.#.#.#",
    "#......#.....#.#...#",
    "####################",
]


def print_map(grid, pacman_pos=None):
    """Affiche la carte dans la console. Optionnellement affiche 'P' à pacman_pos=(y,x)."""
    py, px = pacman_pos if pacman_pos else (-1, -1)
    for y, row in enumerate(grid):
        line = "".join("P" if (y, x) == (py, px) else c for x, c in enumerate(row))
        print(line)


if __name__ == "__main__":
    # Laisse pacman_pos à None pour ne pas afficher 'P'. Exemple: (1, 1)
    pacman_pos = None
    print_map(MAP, pacman_pos)


