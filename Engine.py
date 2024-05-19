import socket
import random
import queue
import json
import tkinter as tk
from tkinter import simpledialog
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot
from threading import Thread, Event
import ChessMain
import time
import rsa
from cryptography.fernet import Fernet
from base64 import b64decode, b64encode

#   //TODO: Plan for Multi-Client Able Server:
#   1. Create a dict, address will be the key, board for each game/client will be the data.
#   2. When getting a message from said address, pass it through the dict to get the board, update it, and send it back. 

isServer = None
client_socket = None
server_socket = None
current_board = None
whiteToMove = True
clients = [] # A list of the port to use for game_states
game_states = {} # A dict of boards with ports as keys

def set_server_state(server):
    global isServer
    isServer = server

def get_server_state():
    global isServer
    return isServer

def set_client_socket(socket):
    global client_socket
    client_socket = socket

def get_client_socket():
    global client_socket
    return client_socket

def set_server_socket(socket):
    global server_socket
    server_socket = socket

def get_server_socket():
    global server_socket
    return server_socket

def set_current_board(board):
    global current_board
    current_board = board

def get_current_board():
    global current_board
    return current_board

def set_whiteToMove(turn):
    global whiteToMove
    whiteToMove = turn

def get_whiteToMove():
    global whiteToMove
    return whiteToMove

def assign_board(addr):
    gs = GameState()
    game_states.update({addr: gs.board})

class Move():
    rankToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                    "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in rankToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                    "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol #Creating a uniqe move ID for every move 1,1 to 1,2 = 1112

        # Overriding the equals method
        def __eq__(self, other):
            if isinstance(other, Move):
                return self.moveID == other.moveID
            return False
                
    def getChessNotation(self):
        return self.GetRankFile(self.startRow, self.startCol) + self.GetRankFile(self.endRow, self.endCol)

    def GetRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"], # Making an 8x8 board, N = knight, K = King, -- = blank space.
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]

        self.moveFunctions = {"p": self.GetPawnMoves, "R": self.GetRookMoves, "B": self.GetBishopMoves,
                            "N": self.GetKnightMoves, "Q": self.GetQueenMoves, "K": self.GetKingMoves}
        
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.moves = []
        self.checkMate = False
        self.Draw = False
        self.shortCastleRightWhite = True
        self.longCastleRightWhite = True
        self.shortCastleRightBlack = True
        self.longCastleRightBlack = True
        self.CastleFlag = False # A flag to know when you castled.
        self.promotionFlag = False # A flag to know when you promoted
        self.server = True # If you will be a server it will be True, client is false. Server is always white.

    def UndoMoves(self):
        if get_current_board() != None:
            self.board = get_current_board()
        if len(self.moveLog) != 0: #make sure there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if(move.pieceMoved == "wK"):
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif(move.pieceMoved == "bK"):
                self.blackKingLocation = (move.startRow, move.startCol)

    def MakeMove(self, move):
        if get_current_board() != None:
            self.board = get_current_board()
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        if(move.pieceMoved == "wK"):
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif(move.pieceMoved == "bK"):
            self.blackKingLocation = (move.endRow, move.endCol)
        set_current_board(self.board)

    def CastleRights(self):
        if get_current_board() != None:
            self.board = get_current_board()
        validMoves = []

        if self.whiteToMove:
            for move in self.moveLog:
                if self.GetPieceName(self.GetPieceLocation(self.moveLog))[1] == "K": # If the king moved 
                    self.shortCastleRightWhite = False
                    self.longCastleRightWhite = False
                
                if "h1" in ((move.getChessNotation()[0], move.getChessNotation()[1])): # Check which rook moved
                    self.shortCastleRightWhite = False

                if "a1" in ((move.getChessNotation()[0], move.getChessNotation()[1])):
                    self.longCastleRightWhite = False
            
            if self.shortCastleRightWhite == True:
                if self.board[7][5] != "--": # Check there are no pieces between king and rook
                    self.shortCastleRightWhite = False
        
                if self.board[7][6] != "--": # Check there are no pieces between king and rook
                    self.shortCastleRightWhite = False

            if self.longCastleRightWhite == True:
                if self.board[7][3] != "--":
                    self.longCastleRightWhite = False
                
                if self.board[7][2] != "--":
                    self.longCastleRightWhite = False
                
                if self.board[7][1] != "--":
                    self.longCastleRightWhite = False
            
            if self.shortCastleRightWhite == True:
                validMoves.append("wO-O")
                print("wO-O")
            
            if self.longCastleRightWhite == True:
                validMoves.append("wO-O-O")
                print("wO-O-O")

        else:
            for move in self.moveLog:
                if self.GetPieceName(self.GetPieceLocation(self.moveLog))[1] == "K":
                    self.shortCastleRightBlack = False
                    self.longCastleRightBlack = False
                
                if "h1" in ((move.getChessNotation()[0], move.getChessNotation()[1])):
                    self.shortCastleRightBlack = False
                
                if "a1" in ((move.getChessNotation()[0], move.getChessNotation()[1])):
                    self.longCastleRightBlack = False
            
            if self.shortCastleRightBlack == True:
                if self.board[0][5] != "--": # Check there are no pieces between king and rook
                    self.shortCastleRightBlack = False

                if self.board[0][6] != "--": # Check there are no pieces between king and rook
                    self.shortCastleRightBlack = False
            
            if self.longCastleRightBlack == True:
                if self.board[0][3] != "--": # Check there are no pieces between king and rook
                    self.longCastleRightBlack = False

                if self.board[0][2] != "--": # Check there are no pieces between king and rook
                    self.longCastleRightBlack = False

                if self.board[0][1] != "--": # Check there are no pieces between king and rook
                    self.longCastleRightBlack = False
            
            if self.shortCastleRightBlack == True:
                validMoves.append("bO-O")
                print("bO-O")
            
            if self.longCastleRightBlack == True:
                validMoves.append("bO-O-O")
                print("bO-O-O")

        self.shortCastleRightWhite = True
        self.longCastleRightWhite = True
        self.shortCastleRightBlack = True
        self.longCastleRightBlack = True
        return validMoves

    def CastleCheck(self, rookLocation): # To make sure you can't castle into check
        if self.CastleFlag == True:
            if self.InCheck() or self.SquareUnderAttack(rookLocation[0], rookLocation[1]): # if an opp piece threatens rook/king after castle, make sure you won't be able to.
                self.CastleFlag = False
        return self.CastleFlag

    def PromotionCheck(self): # To make sure a promotion move counts as a check.
        validMoves = []
        if self.promotionFlag == True:
            print(self.whiteToMove, " WHITE TO MOVE")
            validMoves = self.GetValidMoves()
            self.promotionFlag = False
            return validMoves

    def GetValidMoves(self):    # All moves, with check 
        if get_current_board() != None:
            self.board = get_current_board()
        self.moves = self.GetAllPossibleMoves()
        validMoves = []
        # //TODO: Fix check after promotion

        if self.InCheck():
            i = 0
            validMoves = []
            location = self.GetPieceLocation(self.moveLog)
            
            if self.GetPieceName(location)[1] == "B": # Bishop is B
                blockingMoves = self.GetBlockingMovesBishop(location)
            
            if self.GetPieceName(location)[1] == "R": # Rook is R
                blockingMoves = self.GetBlockingMovesRook(location)
            
            if self.GetPieceName(location)[1] == "Q" or self.promotionFlag == True: # Queen is just Rook + Bishop.
                blockingMoves = self.GetBlockingMovesRook(location) + self.GetBlockingMovesBishop(location)
            
            if self.GetPieceName(location)[1] == "N": #Knight is N
                blockingMoves = self.GetBlockingMovesKnight(location)
            
            if self.GetPieceName(location)[1] == "p": # pawn in p
                blockingMoves = self.GetBlockingMovesPawn(location)


            for move in self.moves: # For every possible move make it, then check if you're in check
                self.MakeMove(move)
                self.whiteToMove = not self.whiteToMove
                if not self.InCheck():
                   validMoves.append(move) # Only add moves that do not walk into/cause check.
                self.whiteToMove = not self.whiteToMove
                self.UndoMoves()

            for move in blockingMoves:
                if self.whiteToMove:
                    if (Move.filesToCols[move.getChessNotation()[0]] != self.whiteKingLocation[1]): # Check if BlockingMoves doesn't contain king moves(can't block with the king)
                        validMoves.append(move)

                else:
                    if(Move.filesToCols[move.getChessNotation()[0]] != self.blackKingLocation[1]): # Check if BlockingMoves doesn't contain king moves(can't block with the king)
                        validMoves.append(move)
                       
        else:
            for move in self.moves: # For every possible move make it, then check if you're in check
                self.MakeMove(move)
                self.whiteToMove = not self.whiteToMove
                if not self.InCheck():
                    validMoves.append(move) # Only add moves that do not walk into check/cause check.
                self.whiteToMove = not self.whiteToMove
                self.UndoMoves()

        for move in self.CastleRights(): # Add legal castle moves
            validMoves.append(move)
        
        return validMoves

    def GetAllPossibleMoves(self):    #All possible moves
        if get_current_board() != None:
            self.board = get_current_board()
        moves = []
        for r in range(len(self.board)): # num of rows
            for c in range(len(self.board[r])): # num of colls in row
                turn = self.board[r][c][0]
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1] # Taking piece's name from given square
                    self.moveFunctions[piece](r, c, moves)
        return moves

    def InCheck(self):
        if self.whiteToMove:
            return self.SquareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        return self.SquareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def checkForStalemate(self):
        if not self.GetValidMoves() and not self.InCheck():
            return True
        return False

    def SquareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.GetAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                    return True
        return False

    def GetPieceName(self, location):
        return self.board[location[1]][location[0]]

    def GetPieceLocation(self, movelog):
        log = movelog.copy()
        loc = log.pop().getChessNotation()
        return ((Move.filesToCols[loc[2]], Move.rankToRows[loc[3]]))

    def GetBlockingMovesBishop(self, location):
        if get_current_board() != None:
            self.board = get_current_board()
        blockingMoves = []
        newLocation = location

        if self.whiteToMove:
            if location[0] < self.whiteKingLocation[1] and location[1] > self.whiteKingLocation[0]: # If king is on a lower collum and higher row then bishop
                name = self.GetPieceName(newLocation)
                while name[1] != "K": #w/b K, Only take note of the K(for king).
                    newLocation = list(newLocation)

                    for move in self.moves:
                        if (move.getChessNotation())[2] == newLocation[0] and (move.getChessNotation())[1] == newLocation[1]:
                            blockingMoves.append(move)
                            
                    if newLocation[0] < 8:
                        newLocation[0] += 1
                    
                    if newLocation[1] > 0:
                        newLocation[1] -= 1

                    if not (0 <= newLocation[0] < 8 and 0 <= newLocation[1] < 8):
                        break

                    name = self.GetPieceName(newLocation)

            if location[0] > self.whiteKingLocation[1] and location[1] > self.whiteKingLocation[0]: # X is bigger Y is smaller(bishop is on the right and below king)
                name = self.GetPieceName(newLocation)
                while name[1] != "K":
                    newLocation = list(newLocation)

                    for move in self.moves:
                        if move.endRow == newLocation[1] and move.endCol == newLocation[0]:
                            blockingMoves.append(move)

                    if newLocation[0] < 8: # Check if Y is in bounds
                        newLocation[0] += 1

                    if newLocation[1] < 0:
                        newLocation[1] -= 1
                    
                    if not (0 <= newLocation[0] < 8 and 0 <= newLocation[1] < 8):
                        break

                    name = self.GetPieceName(newLocation)

                    
                
            if location[0] > self.whiteKingLocation[1] and location[1] < self.whiteKingLocation[0]: # X is bigger Y is smaller(bishop is on the right and above king)
                name = self.GetPieceName(newLocation)
                while name[1] != "K":
                    newLocation = list(newLocation)

                    for move in self.moves:
                        if move.endRow == newLocation[1] and move.endCol == newLocation[0]:
                            blockingMoves.append(move)

                    if newLocation[1] < 8: # Check if Y is in bounds
                        newLocation[1] += 1

                    if newLocation[0] > 0: # Check if X is in bounds
                        newLocation[0] -= 1
                    
                    if not (0 <= newLocation[0] < 8 and 0 <= newLocation[1] < 8):
                        break

                    name = self.GetPieceName(newLocation)

            if location[0] > self.whiteKingLocation[1] and location[1] < self.whiteKingLocation[0]: # X is bigger Y is smaller(bishop is on the right and above king) above means closer to black(In code it's switched)
                    name = self.GetPieceName(newLocation)
                    while name[1] != "K":
                        newLocation = list(newLocation)

                        for move in self.moves:
                            if move.endRow == newLocation[1] and move.endCol == newLocation[0]:
                                blockingMoves.append(move)


                        if newLocation[1] < 8: # Check if Y is in bounds
                            newLocation[1] += 1

                        if newLocation[0] > 0: # Check if X is in bounds
                            newLocation[0] -= 1
                        
                        if not (0 <= newLocation[0] < 8 and 0 <= newLocation[1] < 8):
                            break

                        name = self.GetPieceName(newLocation)


            if location[0] < self.whiteKingLocation[1] and location[1] < self.whiteKingLocation[0]: # X is smaller Y is smaller(bishop is on the left and below king) above means closer to black(In code it's switched)
                    name = self.GetPieceName(newLocation)
                    while name[1] != "K":
                        newLocation = list(newLocation)

                        for move in self.moves:
                            if move.endRow == newLocation[1] and move.endCol == newLocation[0]:
                                blockingMoves.append(move)
        

                        if newLocation[1] < 8: # Check if Y is in bounds
                            newLocation[1] += 1

                        if newLocation[0] > 0: # Check if X is in bounds
                            newLocation[0] -= 1
                        
                        if not (0 <= newLocation[0] < 8 and 0 <= newLocation[1] < 8):
                            break

                        name = self.GetPieceName(newLocation)

                        
        else:
            if location[0] < self.blackKingLocation[1] and location[1] > self.blackKingLocation[0]: # If king is on a lower collum and higher row then bishop
                name = self.GetPieceName(newLocation)
                while name[1] != "K": #w/bK, Only take note of the K(for king).
                    newLocation = list(newLocation)
                    
                    for move in self.moves:
                        if move.endRow == newLocation[1] and move.endCol == newLocation[0]:
                            blockingMoves.append(move)
                    
                    if newLocation[0] < 8:
                        newLocation[0] += 1
                    
                    if newLocation[1] > 0:
                        newLocation[1] -= 1

                    if not (0 <= newLocation[0] < 8 and 0 <= newLocation[1] < 8):
                        break
                    
                    name = self.GetPieceName(newLocation) 

                    

            if location[0] > self.blackKingLocation[1] and location[1] > self.blackKingLocation[0]: # X is bigger Y is bigger(bishop is on the right and below(below means closer to white) king)
                name = self.GetPieceName(newLocation)
                while name[1] != "K":
                    newLocation = list(newLocation)

                    for move in self.moves:
                        if move.endRow == newLocation[1] and move.endCol == newLocation[0]:
                            blockingMoves.append(move)

                    if newLocation[1] < 8: # Check if Y is in bounds
                        newLocation[1] -= 1

                    if newLocation[0] > 0: # Check if X is in bounds
                        newLocation[0] -= 1
                    
                    if not (0 <= newLocation[0] < 8 and 0 <= newLocation[1] < 8):
                        break

                    name = self.GetPieceName(newLocation)

                    
            
            if location[0] > self.blackKingLocation[1] and location[1] < self.blackKingLocation[0]: # X is bigger Y is smaller(bishop is on the right and above king) above means closer to black(In code it's switched)
                name = self.GetPieceName(newLocation)
                while name[1] != "K":
                    newLocation = list(newLocation)
                    
                    for move in self.moves:
                        if move.endRow == newLocation[1] and move.endCol == newLocation[0]:
                            blockingMoves.append(move)


                    if newLocation[1] < 8: # Check if Y is in bounds
                        newLocation[1] += 1

                    if newLocation[0] > 0: # Check if X is in bounds
                        newLocation[0] -= 1
                    
                    if not (0 <= newLocation[0] < 8 and 0 <= newLocation[1] < 8):
                        break

                    name = self.GetPieceName(newLocation)

            if location[0] < self.blackKingLocation[1] and location[1] < self.blackKingLocation[0]: # X is smaller Y is smaller(bishop is on the left and above king) above means closer to black(In code it's switched)
                name = self.GetPieceName(newLocation)
                while name[1] != "K":
                    newLocation = list(newLocation)

                    for move in self.moves:
                        if move.endRow == newLocation[1] and move.endCol == newLocation[0]:
                            blockingMoves.append(move)

                    if newLocation[1] < 8: # Check if Y is in bounds
                        newLocation[1] += 1

                    if newLocation[0] > 0: # Check if X is in bounds
                        newLocation[0] -= 1
                    
                    if not (0 <= newLocation[0] < 8 and 0 <= newLocation[1] < 8):
                        break

                    name = self.GetPieceName(newLocation)
        return blockingMoves

    def GetBlockingMovesRook(self, location): 
        if get_current_board() != None:
            self.board = get_current_board()
        blockingMoves = []
        newLocation = location
        if self.whiteToMove:
            if location[0] > self.whiteKingLocation[1] and location[1] == self.whiteKingLocation[0]: # If rook is to the right(x > king's x) of the king
                name = self.GetPieceName(newLocation)
                while name[1] != "K":
                    newLocation = list(newLocation)

                    for move in self.moves:
                        if move.endRow == newLocation[1] and move.endCol == newLocation[0]:
                            blockingMoves.append(move)

                    if newLocation[0] > 0: # Check if X is in bounds
                        newLocation[0] -= 1
                    
                    if not (0 <= newLocation[0] < 8 and 0 <= newLocation[1] < 8):
                        break

                    name = self.GetPieceName(newLocation)


            if location[0] < self.whiteKingLocation[1] and location[1] == self.whiteKingLocation[0]: # If rook is to the left(x < king's x) of the king
                name = self.GetPieceName(newLocation)
                while name[1] != "K":
                    newLocation = list(newLocation)

                    for move in self.moves:
                        if move.endRow == newLocation[1] and move.endCol == newLocation[0]:
                            blockingMoves.append(move)

                    if newLocation[0] < 8: # Check if X is in bounds
                        newLocation[0] += 1
                    
                    if not (0 <= newLocation[0] < 8 and 0 <= newLocation[1] < 8):
                        break

                    name = self.GetPieceName(newLocation)


            if location[0] == self.whiteKingLocation[1] and location[1] > self.whiteKingLocation[0]: # If rook is below king(y > king's y(Top of board is zero))
                name = self.GetPieceName(newLocation)
                while name[1] != "K":
                    newLocation = list(newLocation)

                    for move in self.moves:
                        if move.endRow == newLocation[1] and move.endCol == newLocation[0]:
                            blockingMoves.append(move)

                    if newLocation[1] < 8: # Check if Y is in bound
                        newLocation[1] += 1

                    
                    if not (0 <= newLocation[0] < 8 and 0 <= newLocation[1] < 8):
                        break

                    name = self.GetPieceName(newLocation)


            if location[0] == self.whiteKingLocation[1] and location[1] > self.whiteKingLocation[0]: # If rook is above king(y < king's y(Top of board is zero))
                name = self.GetPieceName(newLocation)
                while name[1] != "K":
                    newLocation = list(newLocation)

                    for move in self.moves:
                        if move.endRow == newLocation[1] and move.endCol == newLocation[0]:
                            blockingMoves.append(move)

                    if newLocation[1] > 0: # Check if Y is in bound
                        newLocation[1] -= 1

                    if not (0 <= newLocation[0] < 8 and 0 <= newLocation[1] < 8):
                        break

                    name = self.GetPieceName(newLocation)

            
        else:
            if location[0] > self.blackKingLocation[1] and location[1] == self.blackKingLocation[0]: # If rook is to the right(x > king's x) of the king
                name = self.GetPieceName(newLocation)
                while name[1] != "K":
                    newLocation = list(newLocation)

                    for move in self.moves:
                        if move.endRow == newLocation[1] and move.endCol == newLocation[0]:
                            blockingMoves.append(move)

                    if newLocation[0] > 0: # Check if X is in bounds
                        newLocation[0] -= 1
                    
                    if not (0 <= newLocation[0] < 8 and 0 <= newLocation[1] < 8):
                        break

                    name = self.GetPieceName(newLocation)
            

            if location[0] < self.blackKingLocation[1] and location[1] == self.blackKingLocation[0]: # If rook is to the left(x < king's x) of the king
                name = self.GetPieceLocation(newLocation)
                while name[1] != "K":
                    newLocation = list(newLocation)

                    for move in self.moves:
                        if move.endRow == newLocation[1] and move.endCol == newLocation[0]:
                            blockingMoves.append(move)

                    if newLocation[0] > 8: # Check if X is in bounds
                        newLocation[0] += 1
                    
                    if not (0 <= newLocation[0] < 8 and 0 <= newLocation[1] < 8):
                        break

                    name = self.GetPieceName(newLocation)


            if location[0] == self.blackKingLocation[1] and location[1] < self.blackKingLocation[0]: # If rook is above king(y < king's y(Top of board is zero))
                name = self.GetPieceName(newLocation)
                while name[1] != "K":
                    newLocation = list(newLocation)

                    for move in self.moves:
                        if move.endRow == newLocation[1] and move.endCol == newLocation[0]:
                            blockingMoves.append(move)

                    if newLocation[1] < 8: # Check if Y is in bound
                        newLocation[1] += 1
                    
                    if not (0 <= newLocation[0] < 8 and 0 <= newLocation[1] < 8):
                        break

                    name = self.GetPieceName(newLocation)


            if location[0] == self.blackKingLocation[1] and location[1] > self.blackKingLocation[0]: # If rook is below king(y > king's y(Top of board is zero))
                name = self.GetPieceName(newLocation)
                while name[1] != "K":
                    newLocation = list(newLocation)

                    for move in self.moves:
                        if move.endRow == newLocation[1] and move.endCol == newLocation[0]:
                            blockingMoves.append(move)

                    if newLocation[1] < 0: # Check if Y is in bound
                        newLocation[1] += 1
                    
                    if not (0 <= newLocation[0] < 8 and 0 <= newLocation[1] < 8):
                        break

                    name = self.GetPieceName(newLocation)

        return blockingMoves

    def GetBlockingMovesKnight(self, location): # Not really GetBlockingMoves because you can't block a knight... 
        if get_current_board() != None:
            self.board = get_current_board()
        blockingMoves = []
        
        for move in self.moves:
            if move.endRow == location[1] and move.endCol == location[0]: # If a piece can capture the checking knight add it to blockingMoves.
                blockingMoves.append(move)
        
        return blockingMoves

    def GetBlockingMovesPawn(self, location): # Not really GetBlockingMoves because you can't block a pawn... 
        if get_current_board() != None:
            self.board = get_current_board()
        blockingMoves = []
        
        for move in self.moves: 
            if move.endRow == location[1] and move.endCol == location[0]: # If a piece can capture the checking pawn add it to blockingMoves.
                blockingMoves.append(move)
        
        return blockingMoves
                     
    def GetPawnMoves(self, r, c, moves):
        if get_current_board() != None:
            self.board = get_current_board()
        if self.whiteToMove:  # White pawn moves
            if r > 0:  # Prevent moving off the board
                if self.board[r-1][c] == "--":  # Single square move
                    moves.append(Move((r, c), (r-1, c), self.board))
                    if r == 6 and self.board[r-2][c] == "--":  # Double square move
                        moves.append(Move((r, c), (r-2, c), self.board))
                # Captures
                if c-1 >= 0:  # Capture to the left
                    if self.board[r-1][c-1][0] == 'b':  # There's a black piece to capture
                        moves.append(Move((r, c), (r-1, c-1), self.board))
                if c+1 <= 7:  # Capture to the right
                    if self.board[r-1][c+1][0] == 'b':  # There's a black piece to capture
                        moves.append(Move((r, c), (r-1, c+1), self.board))
        else:  # Black pawn moves
            if r < 7:  # Prevent moving off the board
                if self.board[r+1][c] == "--":  # Single square move
                    moves.append(Move((r, c), (r+1, c), self.board))
                    if r == 1 and self.board[r+2][c] == "--":  # Double square move
                        moves.append(Move((r, c), (r+2, c), self.board))
                # Captures
                if c-1 >= 0:  # Capture to the left
                    if self.board[r+1][c-1][0] == 'w':  # There's a white piece to capture
                        moves.append(Move((r, c), (r+1, c-1), self.board))
                if c+1 <= 7:  # Capture to the right
                    if self.board[r+1][c+1][0] == 'w':  # There's a white piece to capture
                        moves.append(Move((r, c), (r+1, c+1), self.board))

    def GetRookMoves(self, r, c, moves):
        if get_current_board() != None:
            self.board = get_current_board()
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)] # Up, down, left, right
        enemy_color = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # Check board bounds
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": # Empty space
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemy_color: # Capture enemy piece
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break # Stop checking further in this direction
                    else: # Friendly piece or king
                        break
                else: # Off the board
                    break

    def GetKnightMoves(self, r, c, moves):
        if get_current_board() != None:
            self.board = get_current_board()
        knightMoves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        ally_color = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8: # Stay on board
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != ally_color: # Empty or enemy piece
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def GetBishopMoves(self, r, c, moves):
        if get_current_board() != None:
            self.board = get_current_board()
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)] # Four diagonals
        enemy_color = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8): # Bishop can move up to 7 squares
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # Check board bounds
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": # Empty space
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemy_color: # Capture enemy piece
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break # Stop checking further in this direction
                    else: # Friendly piece blocks the path
                        break
                else: # Off the board
                    break

    def GetQueenMoves(self, r, c, moves):
        self.GetRookMoves(r, c, moves)
        self.GetBishopMoves(r, c, moves)

    def GetKingMoves(self, r, c, moves):
        if get_current_board() != None:
            self.board = get_current_board()
        kingMoves = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, -1))
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))

class Encryption():
    def __init__(self):
        self.public_key, self.private_key = rsa.newkeys(2048)
        self.partner_public_key = None
        self.symmetric_key = None
        self.cipher = None
    
    def send_public_key(self, socket):
        socket.sendall(self.public_key.save_pkcs1('PEM'))
    
    def receive_public_key(self, socket):
        key_data = socket.recv(4096)
        self.partner_public_key = rsa.PublicKey.load_pkcs1(key_data, 'PEM')
    
    def receive_data(self, socket):
        received_payload = socket.recv(4096).decode('utf-8')
        print(received_payload, " RECEIVED PAYLOAD")
        encrypted_key, encrypted_data = received_payload.split("::")
        self.symmetric_key = rsa.decrypt(b64decode(encrypted_key), self.private_key)
        self.cipher = Fernet(self.symmetric_key)
        decrypted_data = self.cipher.decrypt(b64decode(encrypted_data))
        return json.loads(decrypted_data.decode('utf-8'))

    def generate_symmetric_key(self):
        self.symmetric_key = Fernet.generate_key()
        self.cipher = Fernet(self.symmetric_key)

    def encrypt_symmetric_key(self):
        encrypted_key = rsa.encrypt(self.symmetric_key, self.partner_public_key)
        return b64encode(encrypted_key).decode('utf-8')

    def encrypt_data(self, data):
        encrypted_data = self.cipher.encrypt(data.encode('utf-8'))
        return b64encode(encrypted_data).decode('utf-8')

class Communication():
    def __init__(self):
        self.gui_queue = queue.Queue()  # Queue for GUI updates
        self.connection_established = Event()  # Event to signal successful connection
        self.recive_flag = None
        self.encrypt = Encryption()
        self.client_flag = None # A flag to alert when a new client joins

    def create_display_window(self, host, port, close_event):
        # Initialize the window once outside the loop
        window = tk.Tk()
        window.title("Server Information")
        window.geometry("300x100")

        host_var = tk.StringVar(value=f"Host: {host}")
        port_var = tk.StringVar(value=f"Port: {port}")
        tk.Label(window, textvariable=host_var).pack()
        tk.Label(window, textvariable=port_var).pack()

        def update_gui():
            # Handle GUI updates within a try-except inside the loop
            try:
                func, args = self.gui_queue.get_nowait()
                func(*args)
                self.gui_queue.task_done()
            except queue.Empty:
                pass
            if not close_event.is_set():
                window.after(100, update_gui)  # Continue updating if close_event is not set

        def check_close_event():
            if close_event.is_set():
                window.destroy()  # Close the window if close_event is set
            else:
                window.after(100, check_close_event)  # Continue checking close_event

        window.after(100, update_gui)
        window.after(100, check_close_event)
        window.mainloop()

    def handle_clients(self, addr, client_socket, server_socket):
        self.client_flag = True
        clients.append((addr[1])) # A list of the port to use for assign_board
        assign_board(addr[1]) # Only use the port as the key
        print(game_states)

        while True:
            try:
                data = self.encrypt.receive_data(client_socket)
                if not data:
                    print("Client disconnected.")
                    break
                self.recive_flag = True
                print(f"\nReceived board: {data}")
                set_current_board(data)
            except:
                raise
                client_socket.close()
                server_socket.close()

        client_socket.close()
        server_socket.close()

    def start_server(self, port=6752):
        set_server_state(True)
        host_ip = self.get_host_ip()
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        set_server_socket(server_socket)

        while True:
            try:
                server_socket.bind((host_ip, port))
                print(f"Server successfully bound to {host_ip}:{port}")
                break
            except OSError:
                print(f"Failed to bind to {host_ip}:{port}, trying a new port...")
                port = random.randint(1000, 9999)

        close_event = Event()
        gui_thread = Thread(target=self.create_display_window, args=(host_ip, port, close_event))
        gui_thread.start()
        
        server_socket.listen(5)
        print(f"Server listening on {host_ip}:{port}")

        while True:
            try:
                client_socket, addr = server_socket.accept()
                set_client_socket(client_socket)
                print(f"Received connection from {addr}")
                self.connection_established.set()
                self.encrypt.receive_public_key(client_socket)
                self.encrypt.send_public_key(client_socket)
                client_thread = Thread(target=self.handle_clients, args=(addr, client_socket, server_socket))
                client_thread.start()
            except socket.error as e:
                if e.args[0] == socket.errno.EAGAIN or e.args[0] == socket.errno.EWOULDBLOCK:
                    print("No connections are available to be accepted")
                    print("Error: ", e)
                else:
                    raise
            close_event.set()
            gui_thread.join(timeout=5)

    def start_client(self, host, port):
        set_server_state(False)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        set_client_socket(client_socket)
        print("Connected to server at {}:{}".format(host, port))
        self.connection_established.set()
        self.encrypt.send_public_key(client_socket)
        self.encrypt.receive_public_key(client_socket)

        try:
            while True:
                data = self.encrypt.receive_data(client_socket)
                if not data:
                    print("Server disconnected.")
                    break
                self.recive_flag = True
                print(f"\nReceived board: {data}")
                set_current_board(data)
        finally:
            client_socket.close()
        return client_socket

    def get_host_ip(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        return IP
    
    def SendMessage(self, socket, board, addr):
        self.encrypt.generate_symmetric_key() # Generate symmetric key
        serialized_data = json.dumps(board) # Serialize the board
        encrypted_key = self.encrypt.encrypt_symmetric_key() # Encrypt symmetric key
        encrypted_data = self.encrypt.encrypt_data(serialized_data) # Encrypt serialized board
        try:
            socket.sendall(f"{encrypted_key}::{encrypted_data}".encode('utf-8')) # Send key + board
        except Exception as e:
            raise e

    def setup_network_mode(self):
        root = tk.Tk()
        root.title("Choose Mode")
        root.geometry("200x100")

        def server():
            root.withdraw()  # Hide the window
            thread = Thread(target=self.start_server)
            thread.start()
            root.destroy()  # Destroy the window after starting the thread

        def client():
            root.withdraw()  # Hide the window
            host = simpledialog.askstring("Connect to Server", "Enter the host IP:", parent=root)
            port = simpledialog.askinteger("Connect to Server", "Enter the port:", parent=root)
            if host and port:
                thread = Thread(target=self.start_client, args=(host, port))
                thread.start()
            root.destroy()  # Destroy the window after starting the thread

        tk.Button(root, text="Server", command=server).pack(fill=tk.X)
        tk.Button(root, text="Client", command=client).pack(fill=tk.X)
        root.mainloop()