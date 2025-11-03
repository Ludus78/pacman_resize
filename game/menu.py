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
    stdscr.addstr(2, x_title, title)
    stdscr.attroff(curses.A_BOLD)

    x_sub = max(0, (width - len(subtitle)) // 2)
    stdscr.addstr(4, x_sub, subtitle)

    # Affiche les items du menu avec indicateurs visuels selon l'item sélectionné
    start_y = max(6, height // 2 - len(MENU_ITEMS))
    for idx, label in enumerate(MENU_ITEMS):
        marker_left = "▶ " if idx == selected_idx else "  "
        marker_right = " ◀" if idx == selected_idx else "  "
        line = f"{marker_left}{label}{marker_right}"
        x = max(0, (width - len(line)) // 2)
        if idx == selected_idx:
            stdscr.attron(curses.A_REVERSE)
            stdscr.addstr(start_y + idx * 2, x, line)
            stdscr.attroff(curses.A_REVERSE)
        else:
            stdscr.addstr(start_y + idx * 2, x, line)

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
    return curses.wrapper(run_main_menu)
