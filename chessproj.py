import itertools
import pygame as pg
import pygame
import chess
import threading

BLACK = pg.Color('grey')
WHITE = pg.Color('white')

#Setup(loading images, making lists.):
white_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
white_locations = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                   (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1)]
black_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
black_locations = [(0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7),
                   (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6)]

captured_pieces_white = []
captured_pieces_black = []

black_queen = pygame.image.load('b_queen.png')
black_king = pygame.image.load('b_king.png')

black_rook = pygame.image.load('b_rook.png')
black_bishop = pygame.image.load('b_bishop.png')
black_knight = pygame.image.load('b_knight.png')
black_pawn = pygame.image.load('b_pawn.png')
white_queen = pygame.image.load('w_queen.png')
white_king = pygame.image.load('w_king.png')
white_rook = pygame.image.load('w_rook.png')
white_bishop = pygame.image.load('w_bishop.png')
white_knight = pygame.image.load('w_knight.png')
white_pawn = pygame.image.load('w_pawn.png')
white_images = [white_pawn, white_queen, white_king, white_knight, white_rook, white_bishop]
black_images = [black_pawn, black_queen, black_king, black_knight, black_rook, black_bishop]    
piece_list = ['pawn', 'queen', 'king', 'knight', 'rook', 'bishop']

# 0 - whites turn no selection: 1-whites turn piece selected: 2- black turn no selection, 3 - black turn piece selected
turn_step = 0
selection = 100
valid_moves = []

def DrawBoard():
    colors = itertools.cycle((WHITE, BLACK))
    tile_size = 60
    width, height = 8*tile_size, 8*tile_size
    background = pg.Surface((width, height))

    for y in range(0, height, tile_size):
        for x in range(0, width, tile_size):
            rect = (x, y, tile_size, tile_size)
            pg.draw.rect(background, next(colors), rect)
        next(colors)

    screen.fill((20, 70, 90))
    screen.blit(background, (63, 60))

    pg.display.flip()
    clock.tick(30)



def DrawPieces():
        for i in range(len(white_pieces)):
            if white_pieces[i] == "pawn":
                for i in range(8):
                    screen.blit(white_pawn, (i * 60, 1))
            

def main():
    pg.init()
    global screen
    screen = pg.display.set_mode((600, 600))
    global clock
    clock = pg.time.Clock()
    DrawBoard()
    DrawPieces()
    running = True
    
    while running:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False

        clock.tick(60)
        pg.display.flip()

if __name__ == "__main__":
    main()