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
    clock.tick(30)



def DrawPieces():
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
            

def CheckClick():
    left = pg.mouse.get_pressed()
    pg.mouse.get_rel()
    global redSquare, colour, x, y
    pos = 0
    x = 0
    y = 0
    if left[0]:
        if redSquare == -1:
            pos = pg.mouse.get_pos()
            x = pos[0] // 60
            y = pos[1] // 60
            colour = (255, 0, 0)
            pg.draw.rect(screen, colour, pg.Rect(x * 60, y * 60, 60, 60))
            redSquare = x, y
            #print(redSquare)
            DrawPieces()
        
        #if redSquare != -1:
        else:
            print(redSquare)
            pos = pg.mouse.get_pos()
            x = pos[0] // 60
            y = pos[1] // 60
            pg.draw.rect(screen, colour, pg.Rect(x * 60, y * 60, 60, 60))
            DrawPieces()
            
            if (redSquare[0] + redSquare[1]) % 2 == 0:
                print("== 0")
                #DrawBoard()
                pg.draw.rect(screen, (255, 255, 255), pg.Rect(redSquare[0] * 60, redSquare[1] * 60, 60, 60))
                DrawPieces()
                
            #if (redSquare[0] + redSquare[1]) % 2 != 0:
            else:
                print("!= 0")
                #DrawBoard()
                pg.draw.rect(screen, (200,200,200), pg.Rect(redSquare[0] * 60, redSquare[1] * 60, 60, 60))
                DrawPieces()

            redSquare = -1

            

            


def main():
    pg.init()
    global screen
    screen = pg.display.set_mode((600, 600))
    global clock
    clock = pg.time.Clock()
    DrawBoard()
    DrawPieces()
    running = True
    global redSquare
    redSquare = -1
    
    while running:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
            
            else:
                CheckClick()
                

        clock.tick(60)
        pg.display.flip()

if __name__ == "__main__":
    main()