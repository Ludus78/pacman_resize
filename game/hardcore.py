import threading
import time
from typing import List

_ram_buffer: List[bytearray] = []
_lock = threading.Lock()
_running = False
_thread: threading.Thread | None = None


def _stress_loop() -> None:
    while _running:
        with _lock:
            _ram_buffer.append(bytearray(10_000_000))  # ~10 Mo
        time.sleep(1)


def decrease() -> None:
    """Libère 10 Mo (une unité) si le buffer n'est pas vide."""
    with _lock:
        if _ram_buffer:
            _ram_buffer.pop()

def start() -> None:
    """Démarre le remplissage mémoire (mode hardcore)."""
    global _running, _thread
    if _running:
        return
    _running = True
    _thread = threading.Thread(target=_stress_loop, daemon=True)
    _thread.start()


def stop() -> None:
    """Arrête le remplissage mémoire et libère le buffer."""
    global _running, _ram_buffer, _thread
    _running = False
    if _thread is not None:
        _thread.join()
        _thread = None
    with _lock:
        _ram_buffer.clear()
        # réalloue une nouvelle liste pour libérer la mémoire au GC / alloc système
        _ram_buffer = []
