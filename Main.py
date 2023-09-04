import itertools
import pygame as pg
import chess
import numpy as np

pg.init()

BLACK = pg.Color('black')
WHITE = pg.Color('white')

board = np.zeros((8, 8))
print(board[0][1])

screen = pg.display.set_mode((600, 600))
clock = pg.time.Clock()

def DrawBoard():
    colors = itertools.cycle((WHITE, BLACK))
    tile_size = 60
    width, height = 8*tile_size, 8*tile_size
    background = pg.Surface((width, height))

    for y in range(0, height, tile_size):
        for x in range(0, width, tile_size):
            rect = (x, y, tile_size, tile_size)
            pg.draw.rect(background, next(colors), rect)
            board[x][y]
        next(colors)

    #rect = 0, 0, tile_size, tile_size
    #pg.draw.rect(background, "green", rect) 
    

    game_exit = False
    while not game_exit:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                game_exit = True

        screen.fill((20, 70, 90))
        screen.blit(background, (63, 60))

        pg.display.flip()
        clock.tick(30)


DrawBoard()
pg.quit()