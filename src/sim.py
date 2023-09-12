from dataclasses import dataclass

from .game_model import *
from .agent import AI


@dataclass
class Game_Result:
    game_state: Game_State
    win_side: int


class Simulator:
    def __init__(self, game: KingGameModel = None) -> None:
        if game is None:
            game = KingGameModel(game_mode=Game_Mode.AI_VS_AI, game_type=Game_Type.VISIBLE, network=Game_Network.offline)
        self._game = game
        self.player = AI(game)

    def _play_single_game(self, state: Game_State = None) -> Game_Result:
        win_side = None
        if state is None:
            self._game.reset()
            state = self._game.get_state()
        else:
            self._game.from_state(state)
        while True:
            move = self.player._make_move()
            m = self._game.make_move(move)
            if m == Move_Type.WIN:
                win_side = -self._game.side_to_move
                break
            elif m == Move_Type.LOSE:
                win_side = self._game.side_to_move
                break

        return Game_Result(state, win_side)

    def simulate(self, num_games: int = 1):
        for _ in range(num_games):

        

    