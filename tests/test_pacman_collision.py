import importlib.util
import os
import sys
import types

# Import entities module directly to avoid package-level imports (game.__init__ imports curses on Windows)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTITIES_PATH = os.path.join(ROOT, "game", "entities.py")
MAP_PATH = os.path.join(ROOT, "assets", "maps", "map.py")

# Prepare package placeholders so dataclasses and relative imports behave
if "game" not in sys.modules:
    game_pkg = types.ModuleType("game")
    game_pkg.__path__ = []
    sys.modules["game"] = game_pkg

if "assets" not in sys.modules:
    assets_pkg = types.ModuleType("assets")
    assets_pkg.__path__ = []
    sys.modules["assets"] = assets_pkg

if "assets.maps" not in sys.modules:
    assets_maps_pkg = types.ModuleType("assets.maps")
    assets_maps_pkg.__path__ = []
    sys.modules["assets.maps"] = assets_maps_pkg

# Load as 'game.entities' so dataclasses find the module
spec = importlib.util.spec_from_file_location("game.entities", ENTITIES_PATH)
entities = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = entities
spec.loader.exec_module(entities)

spec2 = importlib.util.spec_from_file_location("assets.maps.map", MAP_PATH)
maps_map = importlib.util.module_from_spec(spec2)
sys.modules[spec2.name] = maps_map
spec2.loader.exec_module(maps_map)


def test_pacman_blocked_by_wall_on_left():
    # Place Pacman at (1,1) (col=1,row=1). Left at x=0 is a wall ('#') in the provided map
    Position = entities.Position
    Pacman = entities.Pacman
    p = Pacman(Position(1, 1), speed=4)
    p.set_desired_direction(-1, 0)  # move left
    # Use dt large enough to try to move at least one tile
    p.update(0.5, game_map=maps_map.MAP)
    assert (p.position.x, p.position.y) == (1, 1)


def test_pacman_can_move_right_into_free_tile():
    Position = entities.Position
    Pacman = entities.Pacman
    # From (1,1) moving right should be allowed (map has '.' at (2,1))
    p = Pacman(Position(1, 1), speed=4)
    p.set_desired_direction(1, 0)  # move right
    p.update(0.5, game_map=maps_map.MAP)
    # With speed=4 and dt=0.5 => dx = int(4 * 0.5) = 2 tiles
    # But stepwise movement prevents skipping walls; here we expect to move 2 tiles to x=3
    assert (p.position.x, p.position.y) == (3, 1)
