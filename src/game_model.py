"""
 * Copyright (c) [2023] Minh v. Duong; dvminh82@gmail.com
 *
 * You are free to use, modify, re-distribute this code at your own risk
 */
"""
from .configs import *
from .base import *


class KingGameModel:
    def __init__(self, board: Board=None, game_mode=Game_Mode.MAN_VS_AI,
                 game_type=Game_Type.VISIBLE) -> None:
        self.game_mode = Game_Mode(game_mode)
        self.game_type = Game_Type(game_type)
        self.games_played = 1
        self.red_wins = 0
        self.black_wins = 0
        if board is not None:
            self.board = board
        else:
            red_king_pos, black_king_pos = self.random_kings()
            self.board = Board(red_king_pos=red_king_pos, black_king_pos=black_king_pos)

    @classmethod
    def init_client(cls, board: Board):
        return KingGameModel(board=board)

    @property
    def side_to_move(self):
        return self.board.side_to_move

    def reset(self, side_to_move: int=RED) -> None:
        red_king_pos, black_king_pos = self.random_kings()
        self.board.reset(red_king_pos=red_king_pos, black_king_pos=black_king_pos)
    
    @staticmethod
    def random_kings():
        import random
        while True:
            red_row, black_row = random.randint(0, NUM_ROWS - 1), random.randint(0, NUM_ROWS - 1)
            red_col, black_col = random.randint(0, NUM_COLS - 1), random.randint(0, NUM_COLS - 1)
            if red_row != black_row or red_col != black_col:
                red_king_pos, black_king_pos = Position(red_row, red_col), Position(black_row, black_col)
                return (red_king_pos, black_king_pos)
            
    def game_over(self, win_side: int) -> None:
        if win_side == RED:
            print('Red has won the game!')
            self.red_wins += 1
        else:
            print('Black has won the game!')
            self.black_wins += 1
        self.games_played += 1
        self.reset()

    def make_move(self, move: Move) -> Move_Type:
        return self.board.make_move(move)

    def play(self):
        win_side = None
        print('Game number {}:'.format(self.games_played))
        while True:
            side_to_move = self.board.side_to_move
            self.board.draw()
            if self.board.check_lose(side_to_move):
                win_side = -self.side_to_move
                break
            if self.side_to_move == RED:
                move = self.red_player.make_move(self.board, side_to_move)
            else:
                move = self.black_player.make_move(self.board, side_to_move)
            m = self.board.make_move(move)
            if m == Move_Type.WIN:
                win_side = self.side_to_move
                break
        self.game_over(win_side=win_side)

    def get_state(self):
        return self.board.get_state(self.game_type)
    
    def from_state(self, state: Game_State):
        self.board.from_state(state)

    def check_move(self, move: Move):
        return self.board.check_move(move)