import pygame as p
import Engine
import time
import threading

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

def DrawGameState(screen, board):
    DrawBoard(screen) # Draw the actual board no pieces
    DrawPieces(screen, board) # Drawing pieces

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

def SetupConnection(comms):
    socket = comms.setup_network_mode()
    print(socket)
    comms.connection_established.wait()

def UpdateSpectatorWindow(screen, clock, comms):
    while True: # //TODO: Figure out why it won't update the window.
        if comms.recive_flag:
            print("INSIDE THAY LOOP")
            print(f"ENGINE.GET_CURRENT_BOARD: {Engine.get_current_board()}")
            DrawGameState(screen, Engine.get_current_board())
            clock.tick(MAX_FPS)
            p.display.flip()
            comms.recive_flag = False

def main():
    comms = Engine.Communication()
    SetupConnection(comms)
    addr = None # Socket addres
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = Engine.GameState()
    playerOne = Engine.get_server_state() # If server is playing this will be True. else, False
    if not playerOne: # If it's black need to make sure to generate moves for black not white.
        gs.whiteToMove = not gs.whiteToMove
        validMoves = gs.GetValidMoves()
        gs.whiteToMove = not gs.whiteToMove
    else: # If white do normally.
        validMoves = gs.GetValidMoves()
    LoadImages() # Only doing this once.
    sqSelected = ()
    playerClicks = []
    moveMade = False
    running = True
    gameOver = False
    shortWhiteCastle = [(7, 4), (7, 7)] # King and rook locations
    longWhiteCastle = [(7, 4), (7, 1)]
    shortBlackCastle = [(0, 4), (0, 7)]
    longBlackCastle = [(0, 4), (0, 1)]
    print(playerOne, " PlayerOne")
    client_socket = Engine.get_client_socket()
    print(f"CLIENT SOCKET 0: {client_socket}")
    server_socket = Engine.get_server_socket()
    time.sleep(1) # Need to wait for Engine.get_clients() to update

    if not Engine.get_clients()[client_socket]:
        DrawGameState(screen, Engine.get_current_board()) # Drawing the board for the first time without moves.
        clock.tick(MAX_FPS)
        p.display.flip()
        spectator_thread = threading.Thread(target=UpdateSpectatorWindow, args=(screen, clock, comms))
        spectator_thread.daemon = True
        spectator_thread.start()
        

    while running:
        if comms.recive_flag:
            gs.whiteToMove = not gs.whiteToMove
            validMoves = gs.GetValidMoves()
            comms.recive_flag = False
        serverTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and not playerOne)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos() # x, y locations of mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col):
                        sqSelected = ()
                        playerClicks = []

                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    
                    if len(playerClicks) == 2 and serverTurn:
                        move = Engine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(f"{len(validMoves)}: Len") # Debugging
                        
                        if playerClicks == shortWhiteCastle or playerClicks == longWhiteCastle or playerClicks == shortBlackCastle or playerClicks == longBlackCastle: # Castle
                                for i in range(len(validMoves)):
                                    string = str(validMoves[i])
                                    if "O-O" in string: # Casteling.
                                        if "w" in string: # If white can castle
                                            if string == "wO-O": # If its short castle
                                                gs.CastleFlag = True
                                                gs.board[7][4] = "--"
                                                gs.board[7][5] = "wR"
                                                gs.board[7][6] = "wK"
                                                gs.board[7][7] = "--"
                                                gs.whiteKingLocation = (7, 6) # Need to change king's location for gs.InCheck().
                                                if gs.CastleCheck((7, 5)) == False: # If casteling causes check/threatens rook, make sure you won't be able to.
                                                    gs.board[7][4] = "wK"
                                                    gs.board[7][5] = "--"
                                                    gs.board[7][6] = "--"
                                                    gs.board[7][7] = "wR"
                                                    gs.whiteKingLocation = (7, 4) # Changing king's location back.
                                                    gs.whiteToMove = not gs.whiteToMove
                                                moveMade = move

                                            if string == "wO-O-O": # If its long castle
                                                gs.CastleCheck = True
                                                gs.board[7][4] = "--"
                                                gs.board[7][3] = "wR"
                                                gs.board[7][2] = "wK"
                                                gs.board[7][1] = "--"
                                                gs.board[7][0] = "--"
                                                gs.whiteKingLocation = (7, 2)
                                                if gs.CastleCheck((7, 3)) == False:
                                                    gs.board[7][4] = "wK"
                                                    gs.board[7][3] = "--"
                                                    gs.board[7][2] = "--"
                                                    gs.board[7][1] = "--"
                                                    gs.board[7][0] = "wR"
                                                    gs.whiteKingLocation = (7, 4)
                                                    gs.whiteToMove = not gs.whiteToMove
                                                moveMade = move
                                        else:
                                            if string == "bO-O": # Short for black
                                                gs.CastleFlag = True
                                                gs.board[0][4] = "--"
                                                gs.board[0][5] = "bR"
                                                gs.board[0][6] = "bK"
                                                gs.board[0][7] = "--"
                                                gs.blackKingLocation = (0, 6)
                                                if gs.CastleCheck((0, 5)) == False:
                                                    gs.board[0][4] = "wK"
                                                    gs.board[0][5] = "--"
                                                    gs.board[0][6] = "--"
                                                    gs.board[0][7] = "wR"
                                                    gs.blackKingLocation = (0, 4)
                                                    gs.whiteToMove = not gs.whiteToMove
                                                moveMade = move

                                            if string == "bO-O-O": # Long for black
                                                gs.CastleFlag = True
                                                gs.board[0][4] = "--"
                                                gs.board[0][3] = "bR"
                                                gs.board[0][2] = "bK"
                                                gs.board[0][1] = "--"
                                                gs.board[0][0] = "--"
                                                gs.blackKingLocation = (0, 2)
                                                if gs.CastleCheck((0, 3)) == False:
                                                    gs.board[0][4] = "wK"
                                                    gs.board[0][3] = "--"
                                                    gs.board[0][2] = "--"
                                                    gs.board[0][1] = "--"
                                                    gs.board[0][0] = "wR"
                                                    gs.blackKingLocation = (0, 4)
                                                    gs.whiteToMove = not gs.whiteToMove
                                        validMoves.remove(validMoves[i])
                                        gs.whiteToMove = not gs.whiteToMove
                                        break
                        
                        for x in range(len(validMoves)):
                            try:
                                print(validMoves[x].getChessNotation() + " Valid") # Debugging
                            except:
                                validMoves.remove(validMoves[x])
                                x -= 1

                            if move.getChessNotation() in (validMoves[x].getChessNotation()):
                                gs.MakeMove(move)
                                moveMade = move
                                sqSelected = () # reseting both vars
                                playerClicks = []
                                break
                            else:
                                playerClicks = [sqSelected]
                        if len(validMoves) == 0:
                            gs.checkMate = True
                            winner = "White"
                            if gs.whiteToMove: # If whiteToMove = True then white has no moves which means black won.
                                winner = "Black"

                        elif gs.checkForStalemate():
                            gs.Draw = True
                            print("Stalemate")

        if moveMade != False and "O-O" not in str(moveMade): # Promotion.
            if not gs.whiteToMove:
                validMoves = gs.GetValidMoves()
                location = ((Engine.Move.filesToCols[Engine.Move.getChessNotation(moveMade)[2]]), int(Engine.Move.getChessNotation(moveMade)[3]))
                if location[1] == 8: # Top of gs.board is zero bottom is seven.
                    location = ((location[0], 0))
                if gs.GetPieceName(list(location))[1] == "p" and (location[1] == 0): # If it's a pawn and it's at the top(y = 0) 7 is bottom(y = 7)
                    gs.board[location[1]][location[0]] = (f"{gs.board[location[1]][location[0]][0]}Q") # Make it a queen
                    gs.promotionFlag = True
                moveMade = False
                try:
                    addr = client_socket.getpeername()
                except:
                    print("discconeted")
                    print(addr, " ADDRESS")
                comms.SendMessage(client_socket, gs.board, addr)
                
            else:
                validMoves = gs.GetValidMoves()
                location = ((Engine.Move.filesToCols[Engine.Move.getChessNotation(moveMade)[2]]), int(Engine.Move.getChessNotation(moveMade)[3]))
                if location[1] == 1: # Top of gs.board is zero bottom is seven.
                    location = ((location[0], 7)) 
                if gs.GetPieceName(list(location))[1] == "p" and (location[1] == 7): # If it's a pawn and it's at the top(y = 0) 7 is bottom(y = 7)
                    gs.board[location[1]][location[0]] = (f"{gs.board[location[1]][location[0]][0]}Q") # Make it a queen
                    gs.promotionFlag = True
                moveMade = False
                try:
                    addr = client_socket.getpeername()
                except:
                    print("discconeted")
                    print(f"CLIENT_SOCKET: {client_socket}")
                comms.SendMessage(client_socket, gs.board, addr)
            
        if "O-O" in str(moveMade):
            validMoves = gs.GetValidMoves()
            moveMade = False
            comms.SendMessage(client_socket, gs.board, addr)

        if gs.promotionFlag == True: # Make sure promotion moves count as check.
            validMoves = gs.PromotionCheck()
            moveMade = False
            comms.SendMessage(client_socket, gs.board, addr)
        
        if gs.Draw or gs.checkMate:
            gameOver = True # Make it nicer looking

        DrawGameState(screen, Engine.get_current_board())
        clock.tick(MAX_FPS)
        p.display.flip()


if __name__ == '__main__':
    main()