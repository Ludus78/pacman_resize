from game.menu import main_menu
import curses
from game.map import GameMap
from game.entities import Position

# Lance la boucle de jeu
def run_game(stdscr) -> None:
    # Initialise l'affichage
    stdscr.clear()
    curses.curs_set(0)
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()

    # Charge la carte et prépare les collisions
    game_map = GameMap.from_file("assets/maps/maplv1.map")

    # Position initiale: essaie de lire 'P' depuis la carte, sinon fallback
    start = game_map.find_char('P')
    if start is None:
        # cherche une case vide proche
        start_pos = (1, 1)
        if game_map.is_blocked(*start_pos):
            start_pos = (0, 0)
    else:
        start_pos = start
        game_map.clear_char('P')

    player = Position(x=start_pos[0], y=start_pos[1])

    stdscr.nodelay(True)
    while True:
        stdscr.clear()
        game_map.draw(stdscr)
        # Dessine le joueur
        try:
            stdscr.addch(player.y, player.x, 'P')
        except curses.error:
            pass
        stdscr.refresh()

        key = stdscr.getch()
        if key == -1:
            # pas d'entrée, boucle continue
            continue

        if key in (27, ord('q')):
            # ESC ou q pour quitter la partie
            break

        dx, dy = 0, 0
        # azerty layout: z (haut), s (bas), q (gauche), d (droite)
        if key in (curses.KEY_UP, ord('z'), ord('w'), ord('k')):
            dy = -1
        elif key in (curses.KEY_DOWN, ord('s'), ord('j')):
            dy = 1
        elif key in (curses.KEY_LEFT, ord('q'), ord('a'), ord('h')):
            dx = -1
        elif key in (curses.KEY_RIGHT, ord('d'), ord('l')):
            dx = 1

        next_x = player.x + dx
        next_y = player.y + dy
        if not game_map.is_blocked(next_x, next_y):
            player.x = next_x
            player.y = next_y

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
