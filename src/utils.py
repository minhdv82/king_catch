from typing import Tuple
from threading import Thread

from .configs import NUM_ROWS


def rc_2_pos(row: int, col: int, nr=NUM_ROWS) -> int:
    return row + col * nr


def pos_2_rc(pos: int, nr=NUM_ROWS) -> Tuple[int, int]:
    row = pos % nr
    col = pos // nr
    return tuple(row, col)


def threaded(func):
    """
    Decorator that multithreads the target function
    with the given parameters. Returns the thread
    created for the function
    """
    def wrapper(*args):
        thread = Thread(target=func, args=args, daemon=True)
        thread.start()
        return thread
    return wrapper


def gen_test(func, *args, **kwargs):
    pass
