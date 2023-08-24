import time

from .game_model import KingGameModel
from .configs import *
from .base import Move, Move_Type
from .clock import TimeControl
from .agent import *
from .network import *
from .utils import threaded

class KingGameController:
    def __init__(self, game_view, game_mode, game_type, network, host=HOST, port=PORT) -> None:        
        self.network = Game_Network(network)
        self.game_mode = Game_Mode(game_mode)
        self.game_type = Game_Type(game_type)
        self.host = host
        self.port = port
        self.time_control = TimeControl(total_time=GAME_TIME, inc_per_move=2, num_players=2)
        self.side = BLACK if self.network == Game_Network.client else RED
        if self.game_mode == Game_Mode.AI_VS_AI:
            self.side = KIBITZ
        self.game_view = game_view

        if self.network != Game_Network.client:
            self.game = KingGameModel(game_mode=game_mode, game_type=game_type)         

        self.init_game()

    @property
    def board(self):
        return self.game.board

    def from_packet(self, gp: GamePacket) -> KingGameModel:
        num_rows, num_cols = gp.board_size
        self.game_type, self.game_mode, self.side = gp.game_type, gp.game_mode, gp.side
        red_king_pos, black_king_pos = gp.red_king_pos, gp.black_king_pos
        blocks = gp.blocks
        return KingGameModel(board=Board(num_rows, num_cols, red_king_pos, black_king_pos, RED, blocks),
                             game_mode=self.game_mode, game_type=self.game_type)

    def to_packet(self):
        return GamePacket(-self.side, self.game_mode, self.game_type,
                          self.board.red_king_pos, self.board.black_king_pos, self.board.blocks,
                          (self.board.num_rows, self.board.num_cols))

    def set_move(self, move):
        self.move_buffer = move

    def init_game(self):
        if self.network == Game_Network.offline:
            if self.game_mode == Game_Mode.MAN_VS_MAN:
                self.red_player = Human(self.game_view)
                self.black_player = Human(self.game_view)
            elif self.game_mode == Game_Mode.AI_VS_AI:
                self.red_player = AI(self.game)
                self.black_player = AI(self.game)
            else:
                self.red_player = Human(self.game_view)
                self.black_player = AI(self.game)
        elif self.network == Game_Network.server:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.host, self.port))
            self.server.listen()
            self.red_player = Human(self.game_view)
            self.black_player = Bot()
            self.side = RED
        else:
            self.black_player = Human(self.game_view)
            self.red_player = Bot()
            self.side = BLACK

        if self.network == Game_Network.server:
            self.connect_as_server()
        if self.network == Game_Network.client:
            self.connect_as_client()

    @threaded
    def connect_as_server(self):
        print('Waiting client to connect')
        c_sock, _ = self.server.accept()
        print('Client has connected')
        self.black_player._client = GameClient(sock=c_sock)
        self.black_player.send_game(self.to_packet())

    # @threaded
    def connect_as_client(self):
        c_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c_sock.connect((self.host, self.port))
        print('Connected to server')
        self.red_player._client = GameClient(sock=c_sock)
        self.get_game(self.red_player)

    def get_game(self, bot):
        while True:
            gp = bot.get_game()
            if gp is not None and isinstance(gp, GamePacket):
                self.game = self.from_packet(gp)
                break

    @property
    def player(self):
        return self.red_player if self.game.side_to_move == RED else self.black_player
    
    def game_over(self, win_side: int):
        self.game.game_over(win_side=win_side)
        self.game_view.game_over(win_side=win_side)
        self.reset()

    def play(self):
        self.time_control.tick()
        if self.time_control.is_time_over:
            win_side = -self.side_to_move
            self.game_over(win_side=win_side)
            return
        move = self.get_move()
        if isinstance(move, Move):
            self.make_move(move)

    @property
    def is_human_turn(self):
        return (self.side_to_move == RED and self.red_player.type == Agent_Type.HUMAN) or \
            (self.side_to_move == BLACK and self.black_player.type == Agent_Type.HUMAN)

    @property
    def side_to_move(self):
        return self.game.side_to_move

    def make_move(self, move: Move):
        if move is None or self.board.check_move(move) == Move_Type.INVALID:
            return
        m = self.game.make_move(move)
        if m != Move_Type.INVALID:
            self.time_control.move()
            self.broad_cast(move)
        if m == Move_Type.WIN:
            win_side = -self.side_to_move
            self.game_over(win_side=win_side)
    
    def get_move(self):
        return None if self.player is None else self.player.get_move()

    def broad_cast(self, move):
        if self.player.type == Agent_Type.BOT:
            self.player.send_move(move)

    def reset(self):
        self.game_view.reset()
        self.time_control.reset()
        if self.network != Game_Network.client:
            self.game.reset()
            if self.network == Game_Network.server:
                bot = self.red_player if self.side == BLACK else self.black_player
                bot.send_game(self.to_packet())
        else:
            bot = self.red_player if self.side == BLACK else self.black_player
            self.get_game(bot)
        self.play()