import pygame as p
import Engine

WIDTH = HEIGHT = 512
DIMENSION = 8 # board is 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 #for animations
IMAGES = {}

def LoadImages():
    pieces = ["wp", "wR", "wN", "wB", "wK", "wQ", "bp", "bR", "bN", "bB", "bK", "bQ",]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(piece + ".png"), (SQ_SIZE, SQ_SIZE))
        IMAGES['wp']


def DrawGameState(screen, gs):
    DrawBoard(screen) # Draw the actual board no pieces
    DrawPieces(screen, gs.board) # Drawing pieces

def DrawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)] # if (r + c) % 2 = 0 then its a white sq, else black.
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def DrawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": #Not empty square
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = Engine.GameState()
    validMoves = gs.GetValidMoves()
    LoadImages() # Only doing this once.
    sqSelected = ()
    playerClicks = []
    moveMade = False
    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() # x, y locations of mouse
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if sqSelected == (row, col):
                    sqSelected = ()
                    playerClicks = []

                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)
                
                if len(playerClicks) == 2:
                    move = Engine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(f"{len(validMoves)}: Len") # Debugging
                    print(gs.whiteToMove, " True = White, False = black") # Debugging
                    for i in range(len(validMoves)):
                        print(validMoves[i].getChessNotation() + " Valid") # Debugging
                        if move.getChessNotation() in (validMoves[i].getChessNotation()):
                            gs.MakeMove(move)
                            moveMade = True
                            sqSelected = () # reseting both vars
                            playerClicks = []
                            print(move.getChessNotation())
                            break
                        else:
                            playerClicks = [sqSelected]

        if moveMade:
            validMoves = gs.GetValidMoves()
            moveMade = False
                    
        DrawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


if __name__ == '__main__':
    main()
    