import pygame as p 
import Engine

WIDTH = HEIGHT = 512
DIMENSION = 8 # board is 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 #for animations
IMAGES = {}
currentMove = ""

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
                    for i in range(len(validMoves)):
                        #print(validMoves[i].getChessNotation() + " Valid") # Debugging
                        string = str(validMoves[i])
                        if "O-O" in string: # Casteling.
                            if "w" in string: # If white can castle
                                if string == "wO-O": # If its short castle
                                    moveMade = move
                                    gs.board[7][4] = "--"
                                    gs.board[7][5] = "wR"
                                    gs.board[7][6] = "wK"
                                    gs.board[7][7] = "--"

                                if string == "wO-O-O": # If its long castle
                                    moveMade = move
                                    gs.board[7][4] = "--"
                                    gs.board[7][3] = "wR"
                                    gs.board[7][2] = "wK"
                                    gs.board[7][1] = "--"
                                    gs.board[7][0] = "--"
                            else:
                                if string == "bO-O": # Short for black
                                    moveMade = move
                                    gs.board[0][4] = "--"
                                    gs.board[0][5] = "wR"
                                    gs.board[0][6] = "wK"
                                    gs.board[0][7] = "--"

                                if string == "bO-O-O": # Long for black
                                    moveMade = move
                                    gs.board[0][4] = "--"
                                    gs.board[0][3] = "wR"
                                    gs.board[0][2] = "wK"
                                    gs.board[0][1] = "--"
                                    gs.board[0][0] = "--"
                            break


                        if move.getChessNotation() in (validMoves[i].getChessNotation()):
                            gs.MakeMove(move)
                            moveMade = move
                            sqSelected = () # reseting both vars
                            playerClicks = []
                            break
                        else:
                            playerClicks = [sqSelected]
                    if len(validMoves) == 0: # Check if no valid moves(Can also be draw do not account for that for now)
                        gs.checkMate = True
                        winner = "White"
                        if gs.whiteToMove: # If whiteToMove = True then white has no moves which means black won.
                            winner = "Black"
                        print(f"Check mate! {winner} Wins!")


        if moveMade != False and "O-O" not in str(moveMade): # Promotion.
            validMoves = gs.GetValidMoves()
            location = ((Engine.Move.filesToCols[Engine.Move.getChessNotation(moveMade)[2]]), int(Engine.Move.getChessNotation(moveMade)[3]))
            if location[1] == 8: # Top of gs.board is zero bottom is eight.
                location = ((location[0], 0))
            if gs.GetPieceName(list(location))[1] == "p" and location[1] == 0: # If it's a pawn and it's at the top(y = 0)
                gs.board[location[1]][location[0]] = (f"{gs.board[location[1]][location[0]][0]}Q") # Make it a queen
            moveMade = False
        
        if "O-O" in str(moveMade):
            validMoves = gs.GetValidMoves()
            moveMade = False

                    
        DrawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


if __name__ == '__main__':
    main()