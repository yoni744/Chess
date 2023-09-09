import itertools
import pygame as pg
import pygame
import chess
import threading
import time

BLACK = pg.Color('grey')
WHITE = pg.Color('white')


board = chess.Board()
print(board.legal_moves)

#Setup(loading images, making lists.)
white_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']

locations = {"(1, 1)": "b_rook",
                    "(2, 1)": "b_knight",
                    "(3, 1)": "b_bishop",
                    "(4, 1)": "b_king", 
                    "(5, 1)": "b_queen",
                    "(6, 1)": "b_bishop",
                    "(7, 1)": "b_knight",
                    "(8, 1)": "b_rook",
                    "(1, 2)": "b_pawn",
                    "(2, 2)": "b_pawn", 
                    "(3, 2)": "b_pawn",
                    "(4, 2)": "b_pawn",
                    "(5, 2)": "b_pawn",
                    "(6, 2)": "b_pawn",
                    "(7, 2)": "b_pawn",
                    "(8, 2)": "b_pawn",
                    "(1 ,3)": "w_sqaure",
                    "(2 ,3)": "b_sqaure",
                    "(3 ,3)": "w_sqaure",
                    "(4 ,3)": "b_sqaure",
                    "(5 ,3)": "w_sqaure",
                    "(6 ,3)": "b_sqaure",
                    "(7 ,3)": "w_sqaure",
                    "(8 ,3)": "b_sqaure",
                    "(1, 4)": "b_sqaure",
                    "(2, 4)": "w_sqaure",
                    "(3, 4)": "b_sqaure",
                    "(4, 4)": "w_sqaure",
                    "(5, 4)": "b_sqaure",
                    "(6, 4)": "w_sqaure",
                    "(7, 4)": "b_sqaure",
                    "(8, 4)": "w_sqaure",
                    "(1, 5)": "w_square",
                    "(2, 5)": "b_square",
                    "(3, 5)": "w_square",
                    "(4, 5)": "b_square",
                    "(5, 5)": "w_square",
                    "(6, 5)": "b_square",
                    "(7, 5)": "w_square",
                    "(8, 5)": "b_square",
                    "(1, 6)": "b_square",
                    "(2, 6)": "w_square",
                    "(3, 6)": "b_square",
                    "(4, 6)": "w_square",
                    "(5, 6)": "b_square",
                    "(6, 6)": "w_square",
                    "(7, 6)": "b_square",
                    "(8, 6)": "w_square",
                    "(1, 7)": "w_square",
                    "(2, 7)": "b_square",
                    "(3, 7)": "w_square",
                    "(4, 7)": "b_square",
                    "(5, 7)": "w_square",
                    "(6, 7)": "b_square",
                    "(7, 7)": "w_square",
                    "(8, 7)": "b_square",
                    "(1, 8)": "w_rook",
                    "(2, 8)": "w_knight",
                    "(3, 8)": "w_bishop",
                    "(4, 8)": "w_queen", 
                    "(5, 8)": "w.king",
                    "(6, 8)": "w_bishop",
                    "(7, 8)": "w_knight",
                    "(8, 8)": "w_rook",
                    "(1, 7)": "w_pawn",
                    "(2, 7)": "w_pawn", 
                    "(3, 7)": "w_pawn",
                    "(4, 7)": "w_pawn",
                    "(5, 7)": "w_pawn",
                    "(6, 7)": "w_pawn",
                    "(7, 7)": "w_pawn",
                    "(8, 7)": "w_pawn"}

black_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']

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
    global colors
    colors = itertools.cycle((WHITE, BLACK))
    tile_size = 60
    width, height = 8*tile_size, 8*tile_size
    global background
    background = pg.Surface((width, height))

    for y in range(0, height, tile_size):
        for x in range(0, width, tile_size):
            rect = (x, y, tile_size, tile_size)
            pg.draw.rect(background, next(colors), rect)
        next(colors)

    screen.fill((20, 70, 90))
    screen.blit(background, (60, 60))

    pg.display.flip()
    clock.tick(60)

class DrawPieces():
    def DrawStart():
        for i in range(len(black_pieces)):
            if black_pieces[i] == "pawn":
                for i in range(9):
                    if i == 0:
                        i = 1
                        screen.blit(black_pawn, (i * 60, 120,))
                        i = 0
                    
                    else:
                        screen.blit(black_pawn, (i * 60, 120,))

            else:
                if black_pieces[i] == "rook":
                    screen.blit(black_rook, (480, 60))
                    screen.blit(black_rook, (60, 60))

                if black_pieces[i] == "knight":
                    screen.blit(black_knight, (120, 60))
                    screen.blit(black_knight, (420, 60))

                if black_pieces[i] == "bishop":
                    screen.blit(black_bishop, (180, 60))
                    screen.blit(black_bishop, (360, 60))

                if black_pieces[i] == "king":
                    screen.blit(black_king, (240, 60))

                if black_pieces[i] == "queen":
                    screen.blit(black_queen, (302, 60))


        for i in range(len(white_pieces)):
            if white_pieces[i] == "pawn":
                for i in range(9):
                    if i == 0:
                        i = 1
                        screen.blit(white_pawn, (i * 60, 420,))
                        i = 0
                    
                    else:
                        screen.blit(white_pawn, (i * 60, 420,))

            else:
                if white_pieces[i] == "rook":
                    screen.blit(white_rook, (480, 480))
                    screen.blit(white_rook, (60, 480))

                if white_pieces[i] == "rook":
                    screen.blit(white_rook, (480, 480))
                    screen.blit(white_rook, (60, 480))

                if white_pieces[i] == "knight":
                    screen.blit(white_knight, (120, 480))
                    screen.blit(white_knight, (420, 480))

                if white_pieces[i] == "bishop":
                    screen.blit(white_bishop, (180, 480))
                    screen.blit(white_bishop, (360, 480))

                if white_pieces[i] == "king":
                    screen.blit(white_king, (240, 480))

                if white_pieces[i] == "queen":
                    screen.blit(white_queen, (300, 480))
    
    def DrawBPawn(location):
        screen.blit(black_pawn, (location[0] * 60, location[1] * 60))

    def DrawBRook(location):
        screen.blit(black_rook, (location[0] * 60, location[1] * 60))

    def DrawBBishop(location):
        screen.blit(black_bishop, (location[0] * 60, location[1] * 60))

    def DrawBKnight(location):
        screen.blit(black_knight, (location[0] * 60, location[1] * 60))

    def DrawBQueen(location):
        screen.blit(black_queen, (location[0] * 60, location[1] * 60))

    def DrawBKing(location):
        screen.blit(black_king, (location[0] * 60, location[1] * 60))

    
    def DrawWPawn(location):
        screen.blit(white_pawn, (location[0] * 60, location[1] * 60))

    def DrawWRook(location):
        screen.blit(white_rook, (location[0] * 60, location[1] * 60))

    def DrawWBishop(location):
        screen.blit(white_bishop, (location[0] * 60, location[1] * 60))

    def DrawWKnight(location):
        screen.blit(white_knight, (location[0] * 60, location[1] * 60))

    def DrawWQueen(location):
        screen.blit(white_queen, (location[0] * 60, location[1] * 60))

    def DrawWKing(location):
        screen.blit(white_king, (location[0] * 60, location[1] * 60))

            


def main():
    pg.init()
    global screen
    screen = pg.display.set_mode((600, 600))
    global clock
    clock = pg.time.Clock()
    DrawBoard()
    DrawPieces.DrawStart()
    running = True
    squareSelected = () # Where player clicked after clicking a piece
    playerClicks = [] # keep track of clicks, piece location and where to move piece to
    
    while running:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
            
            elif e.type == pg.MOUSEBUTTONDOWN:
                location = pg.mouse.get_pos() # [0] = x | [1] = y
                collum = location[0] // 60
                row = location[1] // 60
                if squareSelected == (row, collum): # user clicked same square twice, reseting var
                    squareSelected = ()
                    playerClicks = []
                else:
                    pass
                # add dict with all sqaures(8x8 and check by piece that way)
        
                else:
                    squareSelected = (row, collum)
                    playerClicks.append(squareSelected) # append for both clicks(1 and 2)
                
                if len(playerClicks) == 2:
                    Move


                

        clock.tick(60)
        pg.display.flip()

if __name__ == "__main__":
    main()
