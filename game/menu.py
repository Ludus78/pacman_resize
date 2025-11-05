import curses
from typing import List


MENU_ITEMS: List[str] = ["JOUER", "PARAMÈTRES", "QUITTER"]


# Affiche les items du menu avec indicateurs visuels selon l'item sélectionné
def _draw_menu(stdscr: "curses._CursesWindow", selected_idx: int) -> None:
    # Efface l'écran et désactive le curseur
    stdscr.clear()
    curses.curs_set(0)
    height, width = stdscr.getmaxyx()

    title = "PACMAN TERMINAL"
    subtitle = "↑/↓ pour naviguer, Entrée pour valider, Échap pour quitter"

    # Title
    x_title = max(0, (width - len(title)) // 2)
    stdscr.attron(curses.A_BOLD)
    if 2 < height:
        stdscr.addnstr(2, x_title, title, max(0, width - x_title - 1))
    stdscr.attroff(curses.A_BOLD)

    x_sub = max(0, (width - len(subtitle)) // 2)
    if 4 < height:
        stdscr.addnstr(4, x_sub, subtitle, max(0, width - x_sub - 1))

    # Affiche les items du menu avec indicateurs visuels selon l'item sélectionné
    start_y = max(6, height // 2 - len(MENU_ITEMS))
    for idx, label in enumerate(MENU_ITEMS):
        marker_left = "▶ " if idx == selected_idx else "  "
        marker_right = " ◀" if idx == selected_idx else "  "
        line = f"{marker_left}{label}{marker_right}"
        x = max(0, (width - len(line)) // 2)
        y = start_y + idx * 2
        if y >= height:
            break
        draw_len = max(0, width - x - 1)
        if idx == selected_idx:
            stdscr.attron(curses.A_REVERSE)
            stdscr.addnstr(y, x, line, draw_len)
            stdscr.attroff(curses.A_REVERSE)
        else:
            stdscr.addnstr(y, x, line, draw_len)

    stdscr.refresh()

# Lance le menu principal
def run_main_menu(stdscr: "curses._CursesWindow") -> str:
    # Initialise les couleurs si disponible
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()

    stdscr.nodelay(False)
    stdscr.keypad(True)

    selected_idx = 0
    while True:
        _draw_menu(stdscr, selected_idx)
        key = stdscr.getch()

        if key in (curses.KEY_UP, ord('k')):
            selected_idx = (selected_idx - 1) % len(MENU_ITEMS)
        elif key in (curses.KEY_DOWN, ord('j')):
            selected_idx = (selected_idx + 1) % len(MENU_ITEMS)
        elif key in (curses.KEY_ENTER, 10, 13):
            return MENU_ITEMS[selected_idx]
        elif key in (27,):  # ESC
            return "QUITTER"

# Menu principal
def main_menu() -> str:
    try:
        return curses.wrapper(run_main_menu)
    except Exception:
        # Fallback sur terminaux non compatibles/tailles trop petites: démarrer directement
        return "JOUER"
