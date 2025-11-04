from game.menu import main_menu
import curses
import pygame  # type: ignore
from game.map import GameMap
from game.entities import Position, Pacman, Ghost, Pellet, PowerPellet
from game.score import Score

# Lance la boucle de jeu
def run_game(stdscr) -> None:
    # Initialisation de pygame et de la fenêtre
    pygame.init()
    TILE = 16

    clock = pygame.time.Clock()

    # boucle externe: lance une partie, puis si Enter est pressé sur Game Over recommence
    while True:
        game_map = GameMap.from_file("assets/maps/maplv1.map")

        # collectibles
        dots: dict[tuple[int, int], Pellet] = {}
        power_dots: dict[tuple[int, int], PowerPellet] = {}
        for y, row in enumerate(game_map.rows):
            for x, ch in enumerate(row):
                if ch == '.':
                    dots[(x, y)] = Pellet(Position(x, y), value=1)
                elif ch in ('o', 'O'):
                    power_dots[(x, y)] = PowerPellet(Position(x, y))

        width_px = max(len(r) for r in game_map.rows) * TILE if game_map.rows else 28 * TILE
        height_px = len(game_map.rows) * TILE
        screen = pygame.display.set_mode((width_px, height_px))
        pygame.display.set_caption("Pacman")

        start = game_map.find_char('P')
        if start is None:
            start_pos = (1, 1)
            if game_map.is_blocked(*start_pos):
                start_pos = (0, 0)
        else:
            start_pos = start
            game_map.clear_char('P')

        pacman = Pacman(Position(x=start_pos[0], y=start_pos[1]), speed=4)

        score = Score()
        font = pygame.font.SysFont(None, 18)
        title_font = pygame.font.SysFont(None, 72)
        score_big_font = pygame.font.SysFont(None, 48)

        ghosts: list[Ghost] = []
        colors = ["red", "blue", "pink", "orange"]
        while True:
            gpos = game_map.find_char('G')
            if gpos is None:
                break
            gx, gy = gpos
            game_map.clear_char('G')
            ghosts.append(Ghost(Position(x=gx, y=gy), speed=pacman.speed, direction=(0, 0), color=colors[len(ghosts) % len(colors)]))

        ghost_accums = [0.0 for _ in ghosts]
        move_accum = 0.0
        running = True
        game_over = False

        while running:
            dt = clock.tick(30) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return

            if not game_over:
                keys = pygame.key.get_pressed()
                dx, dy = 0, 0
                if keys[pygame.K_LEFT] or keys[pygame.K_q]:
                    dx = -1
                elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    dx = 1
                elif keys[pygame.K_UP] or keys[pygame.K_z]:
                    dy = -1
                elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    dy = 1

                pacman.set_desired_direction(dx, dy)

                move_accum += pacman.speed * dt
                steps = int(move_accum)
                if steps > 0:
                    move_accum -= steps
                    for _ in range(steps):
                        pacman.update(1 / pacman.speed, game_map=game_map)
                        ppos = (pacman.position.x, pacman.position.y)
                        if ppos in dots:
                            score.add(dots[ppos].value)
                            del dots[ppos]
                        elif ppos in power_dots:
                            score.add(power_dots[ppos].value)
                            del power_dots[ppos]

                        for ghost in ghosts:
                            if ghost.position.x == pacman.position.x and ghost.position.y == pacman.position.y:
                                game_over = True
                                break
                        if game_over:
                            break

                for i, ghost in enumerate(ghosts):
                    ghost_accums[i] += ghost.speed * dt
                    gsteps = int(ghost_accums[i])
                    if gsteps > 0:
                        ghost_accums[i] -= gsteps
                        for _ in range(gsteps):
                            ghost.update(1 / ghost.speed, game_map=game_map)
                            if ghost.position.x == pacman.position.x and ghost.position.y == pacman.position.y:
                                game_over = True
                                break
                        if game_over:
                            break

                for ghost in ghosts:
                    if ghost.position.x == pacman.position.x and ghost.position.y == pacman.position.y:
                        game_over = True
                        break

            # rendu
            screen.fill((0, 0, 0))
            for y, row in enumerate(game_map.rows):
                for x, ch in enumerate(row):
                    if ch == '#':
                        pygame.draw.rect(screen, (0, 0, 200), (x * TILE, y * TILE, TILE, TILE))

            for (cx, cy) in dots.keys():
                pygame.draw.circle(screen, (230, 230, 230), (cx * TILE + TILE // 2, cy * TILE + TILE // 2), max(2, TILE // 8))
            for (cx, cy) in power_dots.keys():
                pygame.draw.circle(screen, (255, 255, 255), (cx * TILE + TILE // 2, cy * TILE + TILE // 2), max(4, TILE // 4))

            px = pacman.position.x * TILE + TILE // 2
            py = pacman.position.y * TILE + TILE // 2
            pygame.draw.circle(screen, (255, 215, 0), (px, py), TILE // 2)

            for ghost in ghosts:
                col = ghost.color
                if isinstance(col, str):
                    color_map = {
                        "red": (200, 30, 30),
                        "blue": (60, 120, 255),
                        "pink": (255, 100, 180),
                        "orange": (255, 150, 24),
                    }
                    col = color_map.get(col.lower(), (200, 30, 30))
                elif not isinstance(col, (tuple, list)):
                    col = (200, 30, 30)
                gx = ghost.position.x * TILE + TILE // 2
                gy = ghost.position.y * TILE + TILE // 2
                pygame.draw.circle(screen, col, (gx, gy), TILE // 2)

            score_surf = font.render(str(score), True, (255, 255, 255))
            screen.blit(score_surf, (4, 2))

            if game_over:
                title_surf = title_font.render("GAME OVER", True, (255, 50, 50))
                score_big_surf = score_big_font.render(f"Score: {score}", True, (255, 255, 255))
                title_rect = title_surf.get_rect(center=(width_px // 2, height_px // 2 - 24))
                score_rect = score_big_surf.get_rect(center=(width_px // 2, height_px // 2 + 24))
                screen.blit(title_surf, title_rect)
                screen.blit(score_big_surf, score_rect)

            pygame.display.flip()

            if game_over:
                waiting = True
                restart = False
                while waiting:
                    for ev in pygame.event.get():
                        if ev.type == pygame.QUIT:
                            pygame.quit()
                            return
                        if ev.type == pygame.KEYDOWN:
                            if ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                                restart = True
                                waiting = False
                                break
                            if ev.key == pygame.K_ESCAPE:
                                pygame.quit()
                                return
                    clock.tick(10)
                if restart:
                    break

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