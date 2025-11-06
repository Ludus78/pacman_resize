from game.menu import main_menu
import curses
import pygame  # type: ignore
from game.map import GameMap
from game.entities import Position, Pacman, Ghost, Pellet, PowerPellet
from game.score import Score
from game import settings, hardcore
import random
import os
from game.map_generator import generate_map

# Calcule les points pour un fantôme mangé selon le combo
def get_ghost_points(combo_count: int) -> int:
    """Retourne les points pour le fantôme selon le nombre de fantômes mangés à la suite"""
    points_sequence = [10, 20, 40, 80]
    if combo_count < len(points_sequence):
        return points_sequence[combo_count]
    # Si plus de 4 fantômes, reste à 80 points
    return 80

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

    # Gestion des niveaux: 3 cartes statiques, puis génération procédurale
    # Dimensions cibles (en tuiles) pour la génération; on peut varier légèrement par niveau
    base_w, base_h, num_ghosts = 28, 24, 4

    # Chargeur de carte depuis un fichier .map
    def load_map_file(path: str) -> list[str]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return [line.rstrip("\n") for line in f]
        except OSError:
            return []

    # Liste des niveaux statiques (absolus, basés sur ce fichier)
    root_dir = os.path.dirname(os.path.abspath(__file__))
    static_levels = [
        os.path.join(root_dir, "assets", "maps", "maplv1.map"),
        os.path.join(root_dir, "assets", "maps", "maplv2.map"),
        os.path.join(root_dir, "assets", "maps", "maplv3.map")
    ]
    current_level_index = 0
    in_procedural_mode = False
    ghost_speed_factor = 1.0
    level_number = 1

    # Détermine la carte initiale: priorise les niveaux statiques
    initial_rows = load_map_file(static_levels[current_level_index]) if static_levels else []
    if initial_rows:
        current_rows = initial_rows
    else:
        # Fallback si fichiers manquants
        in_procedural_mode = True
        current_rows = generate_map(base_w, base_h, num_ghosts=num_ghosts)

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
    ui_title_font = pygame.font.SysFont(None, 22)
    # Espace réservé sous le titre pour éviter la superposition avec le jeu
    ui_offset = 28

    # État de la manche (réinitialisable)
    dots: dict[tuple[int, int], Pellet] = {}
    power_dots: dict[tuple[int, int], PowerPellet] = {}
    pacman = Pacman(Position(0, 0), speed=4)
    ghosts: list[Ghost] = []
    ghost_accums: list[float] = []
    fov_tiles = float(max(width_px, height_px) // TILE)
    shrink_timer = 0.0
    move_accum = 0.0
    frightened_timer = 0.0
    pacman_base_speed = 4  # Vitesse de base de Pacman
    pacman_boost_timer = 0.0  # Timer pour le boost de vitesse
    ghost_combo_counter = 0  # Compteur de combo pour les fantômes mangés à la suite
    respawn_timers: list[tuple[float, str, float]] = []  # (remaining, color, speed)
    cage_pos: tuple[int, int] | None = None
    pacman_boost_timer: float = 0.0
    pacman_original_speed: float | None = None
    elapsed_time = 0.0

    # Helper interne pour (re)créer une manche (niveau) sans relancer le jeu complet
    def reset_round(rows: list[str], *, reset_score: bool) -> None:
        nonlocal game_map, dots, power_dots, pacman, ghosts, ghost_accums, fov_tiles, shrink_timer, move_accum, score, width_px, height_px, screen, frightened_timer, respawn_timers, cage_pos, pacman_boost_timer, pacman_original_speed, elapsed_time, ghost_combo_counter
        # Recharge la carte depuis des lignes générées
        game_map = GameMap(rows)
        # Adapter la taille de la f
        # fenêtre si la carte change de dimensions
        width_px = max(len(r) for r in game_map.rows) * TILE if game_map.rows else 28 * TILE
        height_px = len(game_map.rows) * TILE
        screen = pygame.display.set_mode((width_px, height_px + ui_offset))
        # Recrée les collectibles
        dots = {}
        power_dots = {}
        for y, row in enumerate(game_map.rows):
            for x, ch in enumerate(row):
                if ch == '.':
                    dots[(x, y)] = Pellet(Position(x, y), value=1)
                elif ch in ('o', 'O'):
                    power_dots[(x, y)] = PowerPellet(Position(x, y))
                elif ch == 'C':
                    cage_pos = (x, y)
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
            # réinitialise le timer de boost quand on (re)créé la manche
            pacman_boost_timer = 0.0
            pacman_original_speed = None
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
        fov_tiles = float(max(width_px, height_px) // TILE)
        shrink_timer = 0.0
        move_accum = 0.0
        frightened_timer = 0.0
        pacman_boost_timer = 0.0
        ghost_combo_counter = 0
        respawn_timers = []
        elapsed_time = 0.0
        _ = elapsed_time
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
        # 60 FPS et dt en secondes pour un rendu plus fluide
        dt = clock.tick(60) / 1000.0

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
            elapsed_time += dt
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
                        # Active pouvoir: Pacman peut manger les fantômes (10s niveau 1, décroît avec le niveau, min 3s)
                        duration = max(3.0, 10.0 / max(1, level_number))
                        frightened_timer = duration

                        # Boost de vitesse : Pacman devient 50% plus rapide pendant la même durée
                        # que la capacité à manger les fantômes (proportionnel au niveau)
                        if pacman_boost_timer <= 0.0:
                            pacman_original_speed = pacman.speed
                            pacman.speed = int(pacman_base_speed * 1.5)
                        pacman_boost_timer = duration

                        # Réinitialise le compteur de combo
                        ghost_combo_counter = 0


                    # Collision immédiate Pacman <-> fantôme après ce pas
                    eaten_indexes: list[int] = []
                    for idx, ghost in enumerate(ghosts):
                        if ghost.position.x == pacman.position.x and ghost.position.y == pacman.position.y:
                            if frightened_timer > 0.0:
                                eaten_indexes.append(idx)
                            else:
                                game_over = True
                                break
                    if eaten_indexes:
                        for idx in reversed(eaten_indexes):
                            # Fantôme mangé - ajoute les points selon le combo
                            ghost_points = get_ghost_points(ghost_combo_counter)
                            score.add(ghost_points)
                            ghost_combo_counter += 1
                            g = ghosts.pop(idx)
                            ghost_accums.pop(idx)
                            color = g.color if isinstance(g.color, str) else "red"
                            respawn_timers.append((3.0, color, g.speed))
                    if game_over:
                        break

            # Aligne immédiatement la direction au bord de tuile pour un virage visuel instantané
            ddx, ddy = pacman.desired_direction
            if (ddx, ddy) != (0, 0):
                nx = pacman.position.x + ddx
                ny = pacman.position.y + ddy
                if pacman.can_move_to(nx, ny, game_map):
                    cur_dx, cur_dy = pacman.direction
                    pacman.direction = (ddx, ddy)
                    # Si changement de direction (notamment opposée), on coupe l'interpolation
                    if (ddx, ddy) != (cur_dx, cur_dy):
                        move_accum = 0.0

            # Met à jour les fantômes
            pacman_grid_pos = (pacman.position.x, pacman.position.y)
            is_frightened = (frightened_timer > 0.0)
            i = 0
            while i < len(ghosts):
                ghost = ghosts[i]
                ghost_accums[i] += ghost.speed * dt
                gsteps = int(ghost_accums[i])
                ghost_eaten = False
                if gsteps > 0:
                    ghost_accums[i] -= gsteps
                    prev_dir = ghost.direction
                    for _ in range(gsteps):
                        ghost.update(1 / ghost.speed, game_map=game_map, pacman_pos=pacman_grid_pos, is_frightened=is_frightened)
                        # Collision immédiate après le pas du fantôme
                        if ghost.position.x == pacman.position.x and ghost.position.y == pacman.position.y:
                            if frightened_timer > 0.0:
                                # Fantôme mangé - ajoute les points selon le combo
                                ghost_points = get_ghost_points(ghost_combo_counter)
                                score.add(ghost_points)
                                ghost_combo_counter += 1
                                color = ghost.color if isinstance(ghost.color, str) else "red"
                                respawn_timers.append((3.0, color, ghost.speed))
                                ghosts.pop(i)
                                ghost_accums.pop(i)
                                ghost_eaten = True
                                break
                            else:
                                game_over = True
                                break
                    # Réinitialise l'accumulateur si le fantôme a changé de direction (pour éviter les sauts visuels)
                    if not ghost_eaten and i < len(ghosts) and prev_dir != (0, 0) and ghost.direction != prev_dir:
                        # Changement de direction détecté: reset partiel pour transition douce
                        ghost_accums[i] = min(ghost_accums[i], 0.2)  # Réduit encore plus pour plus de fluidité
                    if game_over:
                        break
                # N'incrémente l'index que si le fantôme n'a pas été mangé
                if not ghost_eaten:
                    i += 1

            # Détection de collision Pacman <-> fantôme (même tuile)
            for idx, ghost in enumerate(list(ghosts)):
                if ghost.position.x == pacman.position.x and ghost.position.y == pacman.position.y:
                    if frightened_timer > 0.0:
                        # Fantôme mangé - ajoute les points selon le combo
                        ghost_points = get_ghost_points(ghost_combo_counter)
                        score.add(ghost_points)
                        ghost_combo_counter += 1
                        ghosts.pop(idx)
                        ghost_accums.pop(idx)
                        color = ghost.color if isinstance(ghost.color, str) else "red"
                        respawn_timers.append((3.0, color, ghost.speed))
                    else:
                        game_over = True
                        break

            # Timers pouvoir et respawn
            if frightened_timer > 0.0:
                frightened_timer = max(0.0, frightened_timer - dt)
                # Fin du pouvoir: réinitialise le combo
                if frightened_timer <= 0.0:
                    ghost_combo_counter = 0
            
            if respawn_timers:
                new_list: list[tuple[float, str, float]] = []
                for remaining, color, speed in respawn_timers:
                    remaining -= dt
                    if remaining <= 0.0:
                        if cage_pos is None:
                            cx, cy = (max(0, (game_map.width // 2)), max(0, (game_map.height // 2)))
                        else:
                            cx, cy = cage_pos
                        ghost_speed = max(1.0, speed)
                        new_ghost = Ghost(Position(x=cx, y=cy), speed=ghost_speed, direction=(0, -1), color=color)
                        ghosts.append(new_ghost)
                        ghost_accums.append(0.0)
                    else:
                        new_list.append((remaining, color, speed))
                respawn_timers = new_list

            # Timer du boost de vitesse, restaure la vitesse quand fini
            if pacman_boost_timer > 0.0:
                pacman_boost_timer = max(0.0, pacman_boost_timer - dt)
                if pacman_boost_timer == 0.0 and pacman_original_speed is not None:
                    pacman.speed = pacman_original_speed
                    pacman_original_speed = None

        # Rendu
        screen.fill((0, 0, 0))
        # Position de Pacman en pixels (monde) avec interpolation sous-tuile
        px = pacman.position.x * TILE + TILE // 2
        py = pacman.position.y * TILE + TILE // 2
        if pacman.direction != (0, 0) and move_accum > 0.0:
            # Interpolation uniquement si la prochaine tuile est libre
            npx = pacman.position.x + pacman.direction[0]
            npy = pacman.position.y + pacman.direction[1]
            if pacman.can_move_to(npx, npy, game_map):
                off_x = pacman.direction[0] * int(move_accum * TILE)
                off_y = pacman.direction[1] * int(move_accum * TILE)
                px += off_x
                py += off_y
        # Calcule la caméra centrée sur Pacman (défilement dynamique)
        map_w_px = game_map.width * TILE
        map_h_px = game_map.height * TILE
        view_w_px = width_px
        view_h_px = height_px
        target_sx = view_w_px // 2
        target_sy = ui_offset + view_h_px // 2
        cam_x = int(max(0, min(map_w_px - view_w_px, px - target_sx)))
        cam_y = int(max(0, min(map_h_px - view_h_px, py - (target_sy - ui_offset))))

        # Dessine la carte (# = mur bleu, sinon noir)
        # On ne dessine que les tuiles visibles pour optimiser
        x0 = max(0, cam_x // TILE)
        y0 = max(0, cam_y // TILE)
        x1 = min(game_map.width, (cam_x + view_w_px) // TILE + 1)
        y1 = min(game_map.height, (cam_y + view_h_px) // TILE + 1)
        for y in range(y0, y1):
            row = game_map.rows[y]
            for x in range(x0, x1):
                ch = row[x]
                if ch == '#':
                    sx = x * TILE - cam_x
                    sy = y * TILE - cam_y + ui_offset
                    pygame.draw.rect(screen, (0, 0, 200), (sx, sy, TILE, TILE))
        # Dessine les collectibles
        for (cx, cy) in dots.keys():
            sx = cx * TILE + TILE // 2 - cam_x
            sy = cy * TILE + TILE // 2 - cam_y + ui_offset
            pygame.draw.circle(screen, (230, 230, 230), (sx, sy), max(2, TILE // 8))
        for (cx, cy) in power_dots.keys():
            sx = cx * TILE + TILE // 2 - cam_x
            sy = cy * TILE + TILE // 2 - cam_y + ui_offset
            pygame.draw.circle(screen, (255, 255, 255), (sx, sy), max(4, TILE // 4))

        # Dessine Pacman
        pygame.draw.circle(screen, (255, 215, 0), (px - cam_x, py - cam_y + ui_offset), TILE // 2)

        # Dessine les fantômes
        for i, ghost in enumerate(ghosts):
            # Si pouvoir actif, fantômes en violet
            if frightened_timer > 0.0:
                col = (170, 80, 255)
            else:
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
            # Interpolation fantôme basée sur son accumulateur dédié
            if ghost.direction != (0, 0) and 0 <= i < len(ghost_accums) and ghost_accums[i] > 0.0:
                ngx = ghost.position.x + ghost.direction[0]
                ngy = ghost.position.y + ghost.direction[1]
                if ghost.can_move_to(ngx, ngy, game_map):
                    goff_x = ghost.direction[0] * int(ghost_accums[i] * TILE)
                    goff_y = ghost.direction[1] * int(ghost_accums[i] * TILE)
                    gx += goff_x
                    gy += goff_y
            pygame.draw.circle(screen, col, (gx - cam_x, gy - cam_y + ui_offset), TILE // 2)

        # Masque de champ de vision: rétrécit en continu (1 tuile toutes les 1.5 secondes - 2x plus rapide)
        if not game_over:
            shrink_timer += dt
            # Réduction continue jusqu'à un minimum de 5 tuiles
            min_fov = 5.0
            if fov_tiles > min_fov:
                fov_tiles = max(min_fov, fov_tiles - (dt / (1.5 / float(level_number))))

        # Applique un overlay sombre avec trou circulaire autour de Pacman
        overlay = pygame.Surface((width_px, height_px + ui_offset), pygame.SRCALPHA)
        overlay.fill((0, 0, 0))
        radius = int(max(0.0, fov_tiles) * TILE + TILE // 2)
        pygame.draw.circle(overlay, (0, 0, 0, 0), (px - cam_x, py - cam_y + ui_offset), radius)
        screen.blit(overlay, (0, 0))

        # Ligne supérieure (titre) + barre d'interface
        # Fine ligne colorée tout en haut
        pygame.draw.line(screen, (255, 160, 60), (0, 0), (width_px, 0), 2)
        bar_h = 24
        pygame.draw.rect(screen, (20, 24, 60), (0, 2, width_px, bar_h))
        # Titre centré
        title_s = ui_title_font.render("PACMAN", True, (255, 255, 255))
        screen.blit(title_s, (width_px // 2 - title_s.get_width() // 2, 4))
        # Infos: Level & Score à gauche, Temps à droite
        level_surf = font.render(f"Level {level_number}", True, (0, 200, 255))
        x_left = 6
        screen.blit(level_surf, (x_left, 4))
        score_surf = font.render(f"Score {score}", True, (255, 230, 80))
        x_left += level_surf.get_width() + 12
        screen.blit(score_surf, (x_left, 4))
        # Temps format MM:SS à droite
        mm = int(elapsed_time) // 60
        ss = int(elapsed_time) % 60
        time_text = f"{mm:02d}:{ss:02d}"
        time_surf = font.render(time_text, True, (255, 200, 200))
        screen.blit(time_surf, (width_px - time_surf.get_width() - 6, 4))
        # Ligne de séparation sous la barre
        pygame.draw.line(screen, (90, 100, 160), (0, 2 + bar_h), (width_px, 2 + bar_h), 2)

        # Surimpression GAME OVER si nécessaire
        if game_over:
            title_surf = title_font.render("GAME OVER", True, (255, 50, 50))
            score_big_surf = score_big_font.render(f"Score: {score}", True, (255, 255, 255))
            title_rect = title_surf.get_rect(center=(width_px // 2, height_px // 2 + ui_offset // 2 - 24))
            score_rect = score_big_surf.get_rect(center=(width_px // 2, height_px // 2 + ui_offset // 2 + 24))
            screen.blit(title_surf, title_rect)
            screen.blit(score_big_surf, score_rect)

        # Écran de VICTOIRE
        if victory:
            title_surf = title_font.render("VICTOIRE", True, (80, 220, 80))
            score_big_surf = score_big_font.render(f"Score: {score}", True, (255, 255, 255))
            title_rect = title_surf.get_rect(center=(width_px // 2, height_px // 2 + ui_offset // 2 - 40))
            score_rect = score_big_surf.get_rect(center=(width_px // 2, height_px // 2 + ui_offset // 2))
            screen.blit(title_surf, title_rect)
            screen.blit(score_big_surf, score_rect)

            # Bouton "Niveau suivant"
            btn_w, btn_h = 220, 48
            btn_rect = pygame.Rect(0, 0, btn_w, btn_h)
            btn_rect.center = (width_px // 2, height_px // 2 + ui_offset // 2 + 60)
            pygame.draw.rect(screen, (40, 140, 255), btn_rect, border_radius=8)
            btn_text = font.render("Niveau suivant (Entrée)", True, (255, 255, 255))
            btn_text_rect = btn_text.get_rect(center=btn_rect.center)
            screen.blit(btn_text, btn_text_rect)

        pygame.display.flip()

        # Si la manche est terminée (défaite ou victoire), on attend l'action du joueur
        if game_over:
            # Attente Entrée (relancer) ou Échap/Fermeture (quitter) – reset score
            if wait_for_enter(screen, clock):
                # Redémarrage complet de la boucle de niveaux: 3 cartes statiques puis procédural
                ghost_speed_factor = 1.0
                in_procedural_mode = False
                current_level_index = 0
                level_number = 1
                first_rows = load_map_file(static_levels[current_level_index]) if static_levels else []
                if first_rows:
                    current_rows = first_rows
                else:
                    # Fallback si fichiers absents
                    in_procedural_mode = True
                    current_rows = generate_map(base_w, base_h, num_ghosts=num_ghosts)
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
                # Si on a encore des niveaux statiques à jouer, charge le suivant
                if not in_procedural_mode and current_level_index + 1 < len(static_levels):
                    current_level_index += 1
                    level_number += 1
                    next_rows = load_map_file(static_levels[current_level_index])
                    if not next_rows:
                        # Si le fichier est manquant, bascule en génération
                        in_procedural_mode = True
                        jitter_w = random.choice([-2, 0, 2])
                        jitter_h = random.choice([-2, 0, 2])
                        width_new = max(21, base_w + jitter_w)
                        height_new = max(15, base_h + jitter_h)
                        next_rows = generate_map(width_new, height_new, num_ghosts=num_ghosts)
                        ghost_speed_factor *= 1.10
                    current_rows = next_rows
                else:
                    # Procédural (après les 3 cartes): génère un nouveau niveau
                    in_procedural_mode = True
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
                    level_number += 1

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