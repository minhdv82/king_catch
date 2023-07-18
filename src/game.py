
from .configs import *
from .base import *
from .agent import *


class Game:
    def __init__(self, board: Board=None, side_to_move=RED, game_mode=Game_Mode.AI_VS_AI, game_type=Game_Type.VISIBLE) -> None:
        self.game_mode = game_mode
        self.game_type = game_type
        self.games_played = 1
        self.red_wins = 0
        self.black_wins = 0
        self.red_player = None
        self.black_player = None
        if board is not None:
            self.board = board
        else:
            red_king_pos, black_king_pos = self.random_kings()
            self.board = Board(red_king_pos=red_king_pos, black_king_pos=black_king_pos, side_to_move=side_to_move)
        self.init_players()

    @property
    def side_to_move(self):
        return self.board.side_to_move

    @property
    def is_human_turn(self):
        return (self.side_to_move == RED and self.red_player.type == Agent_Type.HUMAN) or \
            (self.side_to_move == BLACK and self.black_player.type == Agent_Type.HUMAN)

    def init_players(self):
        if self.game_mode == Game_Mode.MAN_VS_MAN:
            self.red_player = Human()
            self.black_player = Human()
        elif self.game_mode == Game_Mode.AI_VS_AI:
            self.red_player = AI()
            self.black_player = AI()
        else:
            self.red_player = Human()
            self.black_player = AI()

    def reset(self, side_to_move: int=RED) -> None:
        red_king_pos, black_king_pos = self.random_kings()
        self.board.reset(red_king_pos=red_king_pos, black_king_pos=black_king_pos, side_to_move=side_to_move)
    
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
    