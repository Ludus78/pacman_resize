import curses
from typing import List
from . import settings


MAIN_MENU_ITEMS: List[str] = ["JOUER", "PARAMÈTRES", "QUITTER"]


# Affiche les items du menu avec indicateurs visuels selon l'item sélectionné
def _draw_menu(stdscr: "curses._CursesWindow", items: List[str], selected_idx: int, header: str) -> None:
    # Efface l'écran et désactive le curseur
    stdscr.clear()
    curses.curs_set(0)
    height, width = stdscr.getmaxyx()

    if not header:
        header = "PACMAN TERMINAL"
    subtitle = "↑/↓ pour naviguer, Entrée pour valider, Échap pour quitter"

    # Title
    x_title = max(0, (width - len(header)) // 2)
    stdscr.attron(curses.A_BOLD)
    if 2 < height:
        stdscr.addnstr(2, x_title, header, max(0, width - x_title - 1))
    stdscr.attroff(curses.A_BOLD)

    x_sub = max(0, (width - len(subtitle)) // 2)
    if 4 < height:
        stdscr.addnstr(4, x_sub, subtitle, max(0, width - x_sub - 1))

    # Affiche les items du menu avec indicateurs visuels selon l'item sélectionné
    start_y = max(6, height // 2 - len(items))
    for idx, label in enumerate(items):
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
def _run_menu(stdscr: "curses._CursesWindow", items: List[str], title: str = "") -> str:
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
    stdscr.nodelay(False)
    stdscr.keypad(True)
    selected_idx = 0
    while True:
        _draw_menu(stdscr, items, selected_idx, title)
        key = stdscr.getch()
        if key in (curses.KEY_UP, ord('k')):
            selected_idx = (selected_idx - 1) % len(items)
        elif key in (curses.KEY_DOWN, ord('j')):
            selected_idx = (selected_idx + 1) % len(items)
        elif key in (curses.KEY_ENTER, 10, 13):
            return items[selected_idx]
        elif key in (27,):
            return "RETOUR"

def run_parameters_menu(stdscr: "curses._CursesWindow") -> None:
    while True:
        choice = _run_menu(stdscr, [f"MODE HARDCORE : {'ON' if settings.hardcore_mode else 'OFF'}", "RETOUR"], title="PARAMÈTRES")
        if choice.startswith("MODE HARDCORE"):
            settings.hardcore_mode = not settings.hardcore_mode
        else:
            break

# Menu principal
def _main_menu_curses(stdscr: "curses._CursesWindow") -> str:
    while True:
        choice = _run_menu(stdscr, MAIN_MENU_ITEMS, title="MENU PRINCIPAL")
        if choice == "PARAMÈTRES":
            run_parameters_menu(stdscr)
        else:
            return choice

def main_menu() -> str:
    try:
        return curses.wrapper(_main_menu_curses)
    except Exception:
        return "JOUER"
