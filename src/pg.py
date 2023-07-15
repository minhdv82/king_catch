import pygame

from .game import Game
from .configs import SCR_HEIGHT, SCR_WIDTH, NUM_ROWS, NUM_COLS
from .utils import rc_2_pos
from .base import Block_State, Position, Move, Move_Type


class KingGame:
    def __init__(self, game: Game=None) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCR_WIDTH, SCR_HEIGHT))
        pygame.display.set_caption('King_Catch')

        if game is not None:
            self.game = game
        else:
            self.game = Game()

        self.cursor = Position(0, 0)

    def play(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.cursor.row = (self.cursor.row + NUM_ROWS - 1) % NUM_ROWS
                    elif event.key == pygame.K_DOWN:
                        self.cursor.row = (self.cursor.row + 1) % NUM_ROWS
                    elif event.key == pygame.K_LEFT:
                        self.cursor.col = (self.cursor.col + NUM_COLS - 1) % NUM_COLS
                    elif event.key == pygame.K_RIGHT:
                        self.cursor.col = (self.cursor.col + 1) % NUM_COLS
                    elif event.key == pygame.K_KP_ENTER:
                        move = Move(side=self.game.side_to_move, pos=self.cursor)
                        m = self.game.make_move(move)
                        if m == Move_Type.WIN:
                            self.game_over(win_side=1-self.game.side_to_move)
            self.draw()
            pygame.display.update()

    def reset(self):
        self.game.reset()

    def quit(self):
        # self.game.quit()
        pygame.quit()
        exit()

    def draw(self):
        blocks = self.game.board.blocks
        wsz, hsz = SCR_WIDTH // NUM_COLS, SCR_HEIGHT // NUM_ROWS
        for r in range(NUM_ROWS):
            for c in range(NUM_COLS):
                color = (50, 100, 100) if blocks[rc_2_pos(r, c)].state == Block_State.UNFOG else (125, 125, 125)
                pygame.draw.rect(self.screen, color, (c * wsz, r * hsz, hsz, wsz))
        pygame.draw.rect(self.screen, (255, 192, 203), (self.cursor.row * hsz, self.cursor.col * wsz, hsz, wsz))

    def update(self):
        pass

    def game_over(self, win_side: int):
        self.game.game_over(win_side=win_side)
        self.reset()