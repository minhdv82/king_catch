"""
 * Copyright (c) [2023] Minh v. Duong; dvminh82@gmail.com
 *
 * You are free to use, modify, re-distribute this code at your own risk
 */
"""
from time import time

class Clock:
    def __init__(self, total_ticks: int, inc_per_move: int=0) -> None:
        self._total_ticks = total_ticks
        self._inc_per_move = inc_per_move
        self._move_ticks = 0
        self._ticks_remained = self._total_ticks

    def tick(self):
        self._move_ticks += 1
        self._ticks_remained -= 1

    def move(self):
        self._ticks_remained += self._inc_per_move
        self._move_ticks = 0

    def reset(self):
        self._ticks_remained = self._total_ticks
        self._move_ticks = 0

    @property
    def total_time(self):
        return self._ticks_remained


class TimeControl:
    def __init__(self, total_time: int, inc_per_move: int=0, num_players: int=2, sec_to_ticks: int=60) -> None:
        self.num_players = num_players
        self._clocks = [Clock(total_time * sec_to_ticks, inc_per_move * sec_to_ticks) for _ in range(num_players)]
        self._current_index = 0
        self._sec_to_ticks = sec_to_ticks
        self._last_time = time()

    def tick(self):
        dur = time() - self._last_time
        if dur >= 1. / self._sec_to_ticks:
            self._clocks[self._current_index].tick()
            self.update_time()

    def move(self):
        self._clocks[self._current_index].move()
        self._current_index = (self._current_index + 1) % self.num_players
        self.update_time()

    def reset(self):
        self._current_index = 0
        for clock in self._clocks:
            clock.reset()
        self.update_time()

    @property
    def is_time_over(self):
        return self._clocks[self._current_index].total_time < 0
    
    def update_time(self):
        self._last_time = time()