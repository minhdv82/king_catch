

class Clock:
    def __init__(self, total_time: int, inc_per_move: int=0) -> None:
        self._total_time = total_time
        self._inc_per_move = inc_per_move
        self._move_ticks = 0

    def tick(self):
        self._move_ticks += 1
        self._total_time -= 1

    def move(self):
        self._total_time += self._inc_per_move
        self._move_ticks = 0

    @property
    def total_time(self):
        return self._total_time


class TimeControl:
    def __init__(self, total_time: int, inc_per_move: int=0, num_players: int=2) -> None:
        self.num_players = num_players
        self._clocks = [Clock(total_time, inc_per_move) for _ in range(num_players)]
        self.player_to_move = 0

    def tick(self):
        self._clocks[self.player_to_move].tick()

    def move(self):
        self._clocks[self.player_to_move].move()
        self.player_to_move = (self.player_to_move + 1) % self.num_players

    @property
    def is_time_over(self):
        return self._clocks[self.player_to_move].total_time < 0
    