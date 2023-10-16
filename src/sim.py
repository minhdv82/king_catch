import os

from dataclasses import dataclass
from typing import List

import pickle

from .game_model import *
from .agent import AI


@dataclass
class Game_Result:
    game_state: Game_State
    win_side: int


class Simulator:
    def __init__(self, game: KingGameModel = None, file_name: str = 'sim_run_nega') -> None:
        if game is None:
            game = KingGameModel(game_mode=Game_Mode.AI_VS_AI, game_type=Game_Type.VISIBLE)
        self._game = game
        self.player = AI(stupidity='negamax')
        f_name = os.path.dirname(os.path.abspath(__file__))
        f_name = os.path.join(f_name, '../data/')
        f_name = os.path.abspath(os.path.join(f_name, file_name))
        self.file_name = f_name

    @property
    def num_actions(self):
        return 8

    def _play_single_game(self, state: Game_State = None) -> Game_Result:
        win_side = None
        if state is None:
            self._game.reset()
            state = self._game.get_state()
        else:
            self._game.from_state(state)
        while True:
            state = self._game.get_state()
            move = self.player.get_move_now(state)
            m = self._game.make_move(move)
            if m == Move_Type.WIN:
                win_side = -self._game.side_to_move
                break
            elif m == Move_Type.LOSE:
                win_side = self._game.side_to_move
                break

        return Game_Result(state, win_side)

    def simulate(self, num_games: int = 1):
        games = []
        for _ in range(num_games):
            games.append(self._play_single_game())

        with open(self.file_name, 'wb') as f:
            pickle.dump(games, f)
            f.close()

    def resume(self):
        with open(self.file_name, 'rb') as f:
            sim_games = pickle.load(f)
            for game in sim_games:
                print(game.win_side)
            print(len(sim_games))
            f.close()
