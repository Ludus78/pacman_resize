from game.menu import main_menu
import curses
import pygame  # type: ignore
from game.map import GameMap
from game.entities import Position, Pacman, Ghost, Pellet, PowerPellet
from game.score import Score
from game import settings, hardcore
import random
from game.map_generator import generate_map

# Attend l'appui sur Entrée pour relancer la manche.
# Retourne True si Enter (ou pavé numérique Enter) est pressé,
# False si Échap ou fermeture de la fenêtre.
def wait_for_enter(screen, clock):
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return True
                if ev.key == pygame.K_ESCAPE:
                    return False
        # On garde un léger rythme pour rester réactif sans cramer le CPU
        clock.tick(30)

# Attend un clic sur un bouton rectangulaire ou Entrée.
# Retourne True si l'utilisateur valide (clic dans le bouton ou Entrée),
# False si Échap ou fermeture de la fenêtre.
def wait_for_button_or_enter(screen, clock, button_rect: pygame.Rect) -> bool:
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return True
                if ev.key == pygame.K_ESCAPE:
                    return False
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if button_rect.collidepoint(ev.pos):
                    return True
        clock.tick(30)

# Lance la boucle de jeu
def run_game(stdscr) -> None:
    # Initialisation de pygame et de la fenêtre
    pygame.init()
    TILE = 16

    # Gestion des niveaux: génération procédurale
    # Dimensions cibles (en tuiles) pour la génération; on peut varier légèrement par niveau
    base_w, base_h = 28, 20
    current_rows = generate_map(base_w, base_h, num_ghosts=4)
    ghost_speed_factor = 1.0

    # Active le mode hardcore si nécessaire
    if settings.hardcore_mode:
        hardcore.start()
    else:
        hardcore.stop()

    # Charge la carte et prépare les collisions + fenêtre
    game_map = GameMap(current_rows)
    width_px = max(len(r) for r in game_map.rows) * TILE if game_map.rows else 28 * TILE
    height_px = len(game_map.rows) * TILE
    screen = pygame.display.set_mode((width_px, height_px))
    pygame.display.set_caption("Pacman")

    # Score et polices d'affichage (polices réutilisées même après reset)
    score = Score()
    font = pygame.font.SysFont(None, 18)
    title_font = pygame.font.SysFont(None, 72)
    score_big_font = pygame.font.SysFont(None, 48)

    # État de la manche (réinitialisable)
    dots: dict[tuple[int, int], Pellet] = {}
    power_dots: dict[tuple[int, int], PowerPellet] = {}
    pacman = Pacman(Position(0, 0), speed=4)
    ghosts: list[Ghost] = []
    ghost_accums: list[float] = []
    fov_tiles = max(width_px, height_px) // TILE
    shrink_timer = 0.0
    move_accum = 0.0

    # Helper interne pour (re)créer une manche (niveau) sans relancer le jeu complet
    def reset_round(rows: list[str], *, reset_score: bool) -> None:
        nonlocal game_map, dots, power_dots, pacman, ghosts, ghost_accums, fov_tiles, shrink_timer, move_accum, score, width_px, height_px, screen
        # Recharge la carte depuis des lignes générées
        game_map = GameMap(rows)
        # Adapter la taille de la fenêtre si la carte change de dimensions
        width_px = max(len(r) for r in game_map.rows) * TILE if game_map.rows else 28 * TILE
        height_px = len(game_map.rows) * TILE
        screen = pygame.display.set_mode((width_px, height_px))
        # Recrée les collectibles
        dots = {}
        power_dots = {}
        for y, row in enumerate(game_map.rows):
            for x, ch in enumerate(row):
                if ch == '.':
                    dots[(x, y)] = Pellet(Position(x, y), value=1)
                elif ch in ('o', 'O'):
                    power_dots[(x, y)] = PowerPellet(Position(x, y))
        # Position initiale
        start = game_map.find_char('P')
        if start is None:
            start_pos = (1, 1)
            if game_map.is_blocked(*start_pos):
                start_pos = (0, 0)
        else:
            start_pos = start
            game_map.clear_char('P')
        pacman = Pacman(Position(x=start_pos[0], y=start_pos[1]), speed=4)
        # Fantômes
        ghosts = []
        colors_local = ["red", "blue", "pink", "orange"]
        while True:
            gpos = game_map.find_char('G')
            if gpos is None:
                break
            gx, gy = gpos
            game_map.clear_char('G')
            # Applique un léger scaling de vitesse des fantômes selon le niveau
            ghost_speed = max(1.0, pacman.speed * ghost_speed_factor)
            ghost = Ghost(Position(x=gx, y=gy), speed=ghost_speed, direction=(0, 0), color=colors_local[len(ghosts) % len(colors_local)])
            ghosts.append(ghost)
        ghost_accums = [0.0 for _ in ghosts]
        # Champ de vision et timers
        fov_tiles = max(width_px, height_px) // TILE
        shrink_timer = 0.0
        move_accum = 0.0
        # Score: remis à zéro uniquement si demandé (ex: après Game Over)
        if reset_score:
            score = Score()

    # Première initialisation de la manche (nouvelle partie => reset score)
    reset_round(current_rows, reset_score=True)

    clock = pygame.time.Clock()
    running = True
    game_over = False
    victory = False
    while running:
        # 30 FPS et dt en secondes
        dt = clock.tick(30) / 1000.0

        # Gestion des événements (quit/escape + debug)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                # Raccourci debug: force la victoire en vidant les pastilles
                if not game_over and not victory:
                    dots.clear()
                    power_dots.clear()
                    victory = True

        if not game_over and not victory:
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
                        score.add(dots[ppos].value)
                        del dots[ppos]
                        if settings.hardcore_mode:
                            hardcore.decrease()
                    elif ppos in power_dots:
                        score.add(power_dots[ppos].value)
                        del power_dots[ppos]
                        if settings.hardcore_mode:
                            hardcore.decrease()
                        # Superpoint: élargit le champ de vision de 5 tuiles
                        fov_tiles += 5

                    # Victoire si toutes les pastilles sont mangées
                    if not dots and not power_dots:
                        victory = True
                        break

                    # Collision immédiate Pacman <-> fantôme après ce pas
                    for ghost in ghosts:
                        if ghost.position.x == pacman.position.x and ghost.position.y == pacman.position.y:
                            game_over = True
                            break
                    if game_over:
                        break

            # Met à jour les fantômes
            for i, ghost in enumerate(ghosts):
                ghost_accums[i] += ghost.speed * dt
                gsteps = int(ghost_accums[i])
                if gsteps > 0:
                    ghost_accums[i] -= gsteps
                    for _ in range(gsteps):
                        ghost.update(1 / ghost.speed, game_map=game_map)
                        # Collision immédiate après le pas du fantôme
                        if ghost.position.x == pacman.position.x and ghost.position.y == pacman.position.y:
                            game_over = True
                            break
                    if game_over:
                        break

            # Détection de collision Pacman <-> fantôme (même tuile)
            for ghost in ghosts:
                if ghost.position.x == pacman.position.x and ghost.position.y == pacman.position.y:
                    game_over = True
                    break

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

        # Dessine les fantômes
        for ghost in ghosts:
            col = ghost.color
            if isinstance(col, str):
                # Color names to RGB fallback
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

        # Masque de champ de vision: rétrécit d'1 tuile toutes les 5 secondes
        if not game_over:
            shrink_timer += dt
            if shrink_timer >= 3.0:
                shrink_timer -= 3.0
                if fov_tiles > 0:
                    fov_tiles -= 1

        # Applique un overlay sombre avec trou circulaire autour de Pacman
        overlay = pygame.Surface((width_px, height_px), pygame.SRCALPHA)
        overlay.fill((0, 0, 0))
        pygame.draw.circle(overlay, (0, 0, 0, 0), (px, py), max(0, fov_tiles) * TILE + TILE // 2)
        screen.blit(overlay, (0, 0))

        # Affiche le score (coin haut-gauche)
        score_surf = font.render(str(score), True, (255, 255, 255))
        screen.blit(score_surf, (4, 2))

        # Surimpression GAME OVER si nécessaire
        if game_over:
            title_surf = title_font.render("GAME OVER", True, (255, 50, 50))
            score_big_surf = score_big_font.render(f"Score: {score}", True, (255, 255, 255))
            title_rect = title_surf.get_rect(center=(width_px // 2, height_px // 2 - 24))
            score_rect = score_big_surf.get_rect(center=(width_px // 2, height_px // 2 + 24))
            screen.blit(title_surf, title_rect)
            screen.blit(score_big_surf, score_rect)

        # Écran de VICTOIRE
        if victory:
            title_surf = title_font.render("VICTOIRE", True, (80, 220, 80))
            score_big_surf = score_big_font.render(f"Score: {score}", True, (255, 255, 255))
            title_rect = title_surf.get_rect(center=(width_px // 2, height_px // 2 - 40))
            score_rect = score_big_surf.get_rect(center=(width_px // 2, height_px // 2))
            screen.blit(title_surf, title_rect)
            screen.blit(score_big_surf, score_rect)

            # Bouton "Niveau suivant"
            btn_w, btn_h = 220, 48
            btn_rect = pygame.Rect(0, 0, btn_w, btn_h)
            btn_rect.center = (width_px // 2, height_px // 2 + 60)
            pygame.draw.rect(screen, (40, 140, 255), btn_rect, border_radius=8)
            btn_text = font.render("Niveau suivant (Entrée)", True, (255, 255, 255))
            btn_text_rect = btn_text.get_rect(center=btn_rect.center)
            screen.blit(btn_text, btn_text_rect)

        pygame.display.flip()

        # Si la manche est terminée (défaite ou victoire), on attend l'action du joueur
        if game_over:
            # Attente Entrée (relancer) ou Échap/Fermeture (quitter) – reset score
            if wait_for_enter(screen, clock):
                # Redémarre depuis une nouvelle carte générée, remet le score
                ghost_speed_factor = 1.0
                # Regénère une carte de base
                current_rows = generate_map(base_w, base_h, num_ghosts=4)
                reset_round(current_rows, reset_score=True)
                game_over = False
                victory = False
                continue
            else:
                running = False

        if victory:
            # Attente clic sur le bouton ou Entrée pour passer au niveau suivant
            # (Échap/Fermeture quitte le jeu)
            btn_w, btn_h = 220, 48
            btn_rect = pygame.Rect(0, 0, btn_w, btn_h)
            btn_rect.center = (width_px // 2, height_px // 2 + 60)
            if wait_for_button_or_enter(screen, clock, btn_rect):
                # Génère une nouvelle carte (peut varier légèrement en taille)
                # Variation légère de dimensions pour la variété
                jitter_w = random.choice([-2, 0, 2])
                jitter_h = random.choice([-2, 0, 2])
                width_new = max(21, base_w + jitter_w)
                height_new = max(15, base_h + jitter_h)
                current_rows = generate_map(width_new, height_new, num_ghosts=4)
                # Augmente légèrement la vitesse des fantômes
                hardcore.stop()
                if settings.hardcore_mode:
                    hardcore.start()
                ghost_speed_factor *= 1.10
                # Démarre le nouveau niveau sans réinitialiser le score
                reset_round(current_rows, reset_score=False)
                victory = False
                game_over = False
                continue
            else:
                running = False

    hardcore.stop()
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