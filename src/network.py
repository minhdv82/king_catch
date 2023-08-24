from typing import List, Tuple
from dataclasses import dataclass

import socket
import pickle

from .base import *
from .utils import threaded


HOST = '127.0.0.1'
PORT = 12345
MAX_CLIENTS = 5
MOVE_BUFF_SIZE = 1024
GAME_BUFF_SIZE = 8192


@dataclass
class MovePacket:
    move: Move
    id: str=''


@dataclass
class GamePacket:
    side: int
    game_mode: Game_Mode
    game_type: Game_Type
    red_king_pos: Position
    black_king_pos: Position
    blocks: List[Block]
    board_size: Tuple[int, int]


@dataclass
class ClientAddress:
    ip: str
    port: int = PORT
    name: str = ''
    key: str = ''


class GameClient:
    def __init__(self, sock: socket=None, id: str='', host=HOST, port=PORT) -> None:
        self.id = id
        self.sock = sock
        self._data_buffer = []
        self._busy = False

    @property
    def is_busy(self):
        return self._busy

    def _pop_data(self):
        return self._data_buffer.pop() if len(self._data_buffer) else None

    @threaded
    def recv(self, buff_size=GAME_BUFF_SIZE):
        self._busy = True
        while True:
            data = self.sock.recv(buff_size)
            p = pickle.loads(data)
            if p:
                self._data_buffer.append(p)
                break
        self._busy = False

    @threaded
    def send(self, data):
        self.sock.send(data)

    def _get(self, buff_size=MOVE_BUFF_SIZE):
        if self.is_busy:
            return None
        if self._data_buffer:
            data = self._pop_data()
            return data 
        self.recv(buff_size)
        return None

    def get_move(self):
        data = self._get(MOVE_BUFF_SIZE)
        return data.move if isinstance(data, MovePacket) else None

    def get_game(self):
        data = self._get(GAME_BUFF_SIZE)
        return data if isinstance(data, GamePacket) else None
            
    def send_move(self, move: Move):
        self.send(pickle.dumps(MovePacket(id=self.id, move=move)))

    def send_game(self, game_packet):
        self.send(pickle.dumps(game_packet))
