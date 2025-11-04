from __future__ import annotations

from typing import Iterable, Optional, Tuple

# Tentative d'importer pygame si disponible pour exposer les constantes utiles
try:
    import pygame  # type: ignore
    _HAS_PYGAME = True
except Exception:
    pygame = None  # type: ignore
    _HAS_PYGAME = False

Direction = Tuple[int, int]

# Mapping de touches (noms) vers direction
_NAME_TO_DIR: dict[str, Direction] = {
    "left": (-1, 0),
    "right": (1, 0),
    "up": (0, -1),
    "down": (0, 1),
    # AZERTY keys (ZQSD)
    "z": (0, -1),
    "q": (-1, 0),
    "s": (0, 1),
    "d": (1, 0),
}

# If pygame is available, create a mapping from pygame key constants to directions
_PYGAME_KEY_TO_DIR: dict[int, Direction] = {}
if _HAS_PYGAME:
    _PYGAME_KEY_TO_DIR = {
        pygame.K_LEFT: _NAME_TO_DIR["left"],
        pygame.K_RIGHT: _NAME_TO_DIR["right"],
        pygame.K_UP: _NAME_TO_DIR["up"],
        pygame.K_DOWN: _NAME_TO_DIR["down"],
        pygame.K_z: _NAME_TO_DIR["z"],
        pygame.K_q: _NAME_TO_DIR["q"],
        pygame.K_s: _NAME_TO_DIR["s"],
        pygame.K_d: _NAME_TO_DIR["d"],
    }


def direction_from_key(key) -> Optional[Direction]:
    
    # Gestion pygame si on a une constante entière qui est dans la map
    if _HAS_PYGAME and isinstance(key, int):
        return _PYGAME_KEY_TO_DIR.get(key)

    # Si la touche est fournie comme chaîne
    if isinstance(key, str):
        k = key.lower()
        return _NAME_TO_DIR.get(k)

    # Pas connu
    return None


def direction_from_key_state(key_state: Iterable[bool]) -> Optional[Direction]:
    
    # Si pygame est disponible et key_state est la séquence attendue
    if _HAS_PYGAME and hasattr(pygame, "K_LEFT"):
        try:
            # Vérifier flèches
            if key_state[pygame.K_LEFT]:
                return _NAME_TO_DIR["left"]
            if key_state[pygame.K_RIGHT]:
                return _NAME_TO_DIR["right"]
            if key_state[pygame.K_UP]:
                return _NAME_TO_DIR["up"]
            if key_state[pygame.K_DOWN]:
                return _NAME_TO_DIR["down"]
            # Puis ZQSD
            if key_state[pygame.K_z]:
                return _NAME_TO_DIR["z"]
            if key_state[pygame.K_q]:
                return _NAME_TO_DIR["q"]
            if key_state[pygame.K_s]:
                return _NAME_TO_DIR["s"]
            if key_state[pygame.K_d]:
                return _NAME_TO_DIR["d"]
        except Exception:
            # key_state n'était pas indexable de la façon attendue
            pass

    # Fallback heuristique : si key_state est un itérable de (name, pressed)
    try:
        for item in key_state:
            if not item:
                continue
            # tenter de déduire
            if isinstance(item, tuple) and len(item) == 2:
                name, pressed = item
                if pressed and isinstance(name, str):
                    dir_ = _NAME_TO_DIR.get(name.lower())
                    if dir_:
                        return dir_
    except Exception:
        pass

    return None


# Petit utilitaire : convertir une direction en chaîne lisible (pour debug)
def dir_to_name(direction: Direction) -> str:
    for k, v in _NAME_TO_DIR.items():
        if v == direction:
            return k
    return "none"
