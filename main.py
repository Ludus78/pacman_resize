from game.menu import main_menu
import curses
import pygame
from game.map import GameMap
from game.entities import Position, Pacman, Pellet, PowerPellet

# Lance la boucle de jeu
def run_game(stdscr) -> None:
    # Initialisation de pygame et de la fenêtre
    pygame.init()
    TILE = 16

    # Charge la carte et prépare les collisions
    game_map = GameMap.from_file("assets/maps/maplv1.map")

    # Extrait les collectibles (points '.' et gros 'o') comme entités
    dots: dict[tuple[int, int], Pellet] = {}
    power_dots: dict[tuple[int, int], PowerPellet] = {}
    for y, row in enumerate(game_map.rows):
        for x, ch in enumerate(row):
            if ch == '.':
                pos = (x, y)
                dots[pos] = Pellet(Position(x, y), value=1)
            elif ch in ('o', 'O'):
                pos = (x, y)
                power_dots[pos] = PowerPellet(Position(x, y))

    # Calcul de la taille de la fenêtre en pixels
    width_px = max(len(r) for r in game_map.rows) * TILE if game_map.rows else 28 * TILE
    height_px = len(game_map.rows) * TILE
    screen = pygame.display.set_mode((width_px, height_px))
    pygame.display.set_caption("Pacman")

    # Position initiale: essaie de lire 'P' depuis la carte, sinon fallback
    start = game_map.find_char('P')
    if start is None:
        start_pos = (1, 1)
        if game_map.is_blocked(*start_pos):
            start_pos = (0, 0)
    else:
        start_pos = start
        game_map.clear_char('P')

    # Vitesse en tuiles/seconde (mouvement fluide avec dt)
    pacman = Pacman(Position(x=start_pos[0], y=start_pos[1]), speed=4)

    clock = pygame.time.Clock()
    move_accum = 0.0  # accumule la progression pour des pas d'une tuile
    running = True
    while running:
        # 30 FPS et dt en secondes
        dt = clock.tick(30) / 1000.0

        # Gestion des événements (quit/escape)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # Lecture des touches maintenues pour orienter Pacman en continu
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        # Priorité horizontale si les deux axes sont pressés (évite diagonales)
        if keys[pygame.K_LEFT] or keys[pygame.K_q]:
            dx = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
        elif keys[pygame.K_UP] or keys[pygame.K_z]:
            dy = -1
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1

        pacman.set_desired_direction(dx, dy)

        # Convertit la vitesse continue en pas de 1 tuile avec un accumulateur
        move_accum += pacman.speed * dt
        steps = int(move_accum)
        if steps > 0:
            move_accum -= steps
            # Chaque step déplace d'exactement 1 tuile (avec collisions)
            for _ in range(steps):
                pacman.update(1 / pacman.speed, game_map=game_map)
                # Vérifie si Pacman mange un collectible à la nouvelle case
                ppos = (pacman.position.x, pacman.position.y)
                if ppos in dots:
                    del dots[ppos]
                elif ppos in power_dots:
                    del power_dots[ppos]

        # Rendu
        screen.fill((0, 0, 0))
        # Dessine la carte (# = mur bleu, sinon noir)
        for y, row in enumerate(game_map.rows):
            for x, ch in enumerate(row):
                if ch == '#':
                    pygame.draw.rect(screen, (0, 0, 200), (x * TILE, y * TILE, TILE, TILE))
        # Dessine les collectibles
        for (cx, cy) in dots.keys():
            pygame.draw.circle(screen, (230, 230, 230), (cx * TILE + TILE // 2, cy * TILE + TILE // 2), max(2, TILE // 8))
        for (cx, cy) in power_dots.keys():
            pygame.draw.circle(screen, (255, 255, 255), (cx * TILE + TILE // 2, cy * TILE + TILE // 2), max(4, TILE // 4))

        # Dessine Pacman
        px = pacman.position.x * TILE + TILE // 2
        py = pacman.position.y * TILE + TILE // 2
        pygame.draw.circle(screen, (255, 215, 0), (px, py), TILE // 2)

        pygame.display.flip()

    pygame.quit()

# Point d'entrée du jeu Pacman
def main() -> None:
    # Affiche le menu principal et attend un choix de l'utilisateur
    choix = main_menu()

    if choix == "JOUER":
        curses.wrapper(run_game)
    elif choix == "PARAMÈTRES":
        print("Ouverture des paramètres... (à implémenter)")
        # TODO: ouvrir un écran de paramètres
    else:
        print("Au revoir.")


if __name__ == "__main__":
    main()
