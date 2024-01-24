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

    
    def undoMove(self):
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
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        if(move.pieceMoved == "wK"):
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif(move.pieceMoved == "bK"):
            self.blackKingLocation = (move.endRow, move.endCol)


    def GetValidMoves(self):    # All moves, with check
        self.moves = self.GetAllPossibleMoves()
        validMoves = []

        if self.InCheck():
            i = 0
            validMoves = []
            location = self.GetPieceLocation(self.moveLog)
            blockingMoves = self.GetBlockingMovesBishop(location)
            for move in blockingMoves:
                if self.whiteToMove:
                    if (Move.filesToCols[move.getChessNotation()[0]] != self.whiteKingLocation[1]): # Check if BlockingMoves doesn't contain king moves(can't block with the king)
                        validMoves.append(move)
                else:
                    if(Move.filesToCols[move.getChessNotation()[0]] != self.blackKingLocation[1]): # Check if BlockingMoves doesn't contain king moves(can't block with the king)
                        print(Move.filesToCols[move.getChessNotation()[0]], self.blackKingLocation[0], " LOCATION")
                        validMoves.append(move)

        else:
            validMoves = self.moves
        
        
        return validMoves



    def GetAllPossibleMoves(self):    #All possible moves
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
        for move in log:
            print(move.getChessNotation())
        loc = log.pop().getChessNotation()
        return ((Move.filesToCols[loc[2]], Move.rankToRows[loc[3]]))

    def GetBlockingMovesBishop(self, location):
        blockingMoves = []
        newLocation = location

        if self.whiteToMove:
            if location[0] < self.whiteKingLocation[1] and location[1] > self.whiteKingLocation[0]: # If king is on a lower collum and higher row then bishop
                name = self.GetPieceName(newLocation)
                while name[1] != "K": #w/b K, Only take note of the K(for king).
                    newLocation = list(newLocation)
                    if newLocation[0] < 8:
                        newLocation[0] += 1
                    
                    if newLocation[1] > 0:
                        newLocation[1] -= 1

                    if not (0 <= newLocation[0] < 8 and 0 <= newLocation[1] < 8):
                        break

                    name = self.GetPieceName(newLocation)

                    for move in self.moves:
                        if (move.getChessNotation())[2] == newLocation[0] and (move.getChessNotation())[1] == newLocation[1]:
                            blockingMoves.append(move)

            if location[0] > self.whiteKingLocation[1] and location[1] > self.whiteKingLocation[0]: # X is bigger Y is smaller(bishop is on the right and below king)
                name = self.GetPieceName(newLocation)
                while name[1] != "K":
                    newLocation = list(newLocation)
                    if newLocation[0] < 8: # Check if Y is in bounds
                        newLocation[0] += 1

                    if newLocation[1] < 0:
                        newLocation[1] -= 1
                    
                    if not (0 <= newLocation[0] < 8 and 0 <= newLocation[1] < 8):
                        break

                    name = self.GetPieceName(newLocation)

                    for move in self.moves:
                        if move.endRow == newLocation[1] and move.endCol == newLocation[0]:
                            blockingMoves.append(move)

                
            if location[0] > self.whiteKingLocation[1] and location[1] < self.whiteKingLocation[0]: # X is bigger Y is smaller(bishop is on the right and above king)
                name = self.GetPieceName(newLocation)
                while name[1] != "K":
                    newLocation = list(newLocation)
                    if newLocation[1] < 8: # Check if Y is in bounds
                        newLocation[1] += 1

                    if newLocation[0] > 0: # Check if X is in bounds
                        newLocation[0] -= 1
                    
                    if not (0 <= newLocation[0] < 8 and 0 <= newLocation[1] < 8):
                        break

                    name = self.GetPieceName(newLocation)

                    for move in self.moves:
                        if move.endRow == newLocation[1] and move.endCol == newLocation[0]:
                            blockingMoves.append(move)

        if location[0] > self.whiteKingLocation[1] and location[1] < self.whiteKingLocation[0]: # X is bigger Y is smaller(bishop is on the right and above king) above means closer to black(In code it's switched)
                name = self.GetPieceName(newLocation)
                while name[1] != "K":
                    newLocation = list(newLocation)
                    if newLocation[1] < 8: # Check if Y is in bounds
                        newLocation[1] += 1

                    if newLocation[0] > 0: # Check if X is in bounds
                        newLocation[0] -= 1
                    
                    if not (0 <= newLocation[0] < 8 and 0 <= newLocation[1] < 8):
                        break

                    name = self.GetPieceName(newLocation)

                    for move in self.moves:
                        if move.endRow == newLocation[1] and move.endCol == newLocation[0]:
                            blockingMoves.append(move)


        if location[0] < self.whiteKingLocation[1] and location[1] < self.whiteKingLocation[0]: # X is smaller Y is smaller(bishop is on the left and below king) above means closer to black(In code it's switched)
                name = self.GetPieceName(newLocation)
                while name[1] != "K":
                    newLocation = list(newLocation)
                    if newLocation[1] < 8: # Check if Y is in bounds
                        newLocation[1] += 1

                    if newLocation[0] > 0: # Check if X is in bounds
                        newLocation[0] -= 1
                    
                    if not (0 <= newLocation[0] < 8 and 0 <= newLocation[1] < 8):
                        break

                    name = self.GetPieceName(newLocation)

                    for move in self.moves:
                        if move.endRow == newLocation[1] and move.endCol == newLocation[0]:
                            blockingMoves.append(move)
        
        else:
            if location[0] < self.blackKingLocation[1] and location[1] > self.blackKingLocation[0]: # If king is on a lower collum and higher row then bishop
                name = self.GetPieceName(newLocation)
                while name[1] != "K": #w/b K, Only take note of the K(for king).
                    newLocation = list(newLocation)
                    if newLocation[0] < 8:
                        newLocation[0] += 1
                    
                    if newLocation[1] > 0:
                        newLocation[1] -= 1

                    if not (0 <= newLocation[0] < 8 and 0 <= newLocation[1] < 8):
                        break
                    
                    name = self.GetPieceName(newLocation) 

                    for move in self.moves:
                        if move.endRow == newLocation[1] and move.endCol == newLocation[0]:
                            blockingMoves.append(move)

            if location[0] > self.blackKingLocation[1] and location[1] > self.blackKingLocation[0]: # X is bigger Y is bigger(bishop is on the right and below king)
                name = self.GetPieceName(newLocation)
                while name[1] != "K":
                    newLocation = list(newLocation)
                    if newLocation[1] < 8: # Check if Y is in bounds
                        newLocation[1] -= 1

                    if newLocation[0] > 0: # Check if X is in bounds
                        newLocation[0] -= 1
                    
                    if not (0 <= newLocation[0] < 8 and 0 <= newLocation[1] < 8):
                        break

                    name = self.GetPieceName(newLocation)

                    for move in self.moves:
                        if move.endRow == newLocation[1] and move.endCol == newLocation[0]:
                            blockingMoves.append(move)

            
            if location[0] > self.blackKingLocation[1] and location[1] < self.blackKingLocation[0]: # X is bigger Y is smaller(bishop is on the right and above king) above means closer to black(In code it's switched)
                name = self.GetPieceName(newLocation)
                while name[1] != "K":
                    newLocation = list(newLocation)
                    if newLocation[1] < 8: # Check if Y is in bounds
                        newLocation[1] += 1

                    if newLocation[0] > 0: # Check if X is in bounds
                        newLocation[0] -= 1
                    
                    if not (0 <= newLocation[0] < 8 and 0 <= newLocation[1] < 8):
                        break

                    name = self.GetPieceName(newLocation)

                    for move in self.moves:
                        if move.endRow == newLocation[1] and move.endCol == newLocation[0]:
                            blockingMoves.append(move)


            if location[0] < self.blackKingLocation[1] and location[1] < self.blackKingLocation[0]: # X is smaller Y is smaller(bishop is on the left and above king) above means closer to black(In code it's switched)
                name = self.GetPieceName(newLocation)
                while name[1] != "K":
                    newLocation = list(newLocation)
                    if newLocation[1] < 8: # Check if Y is in bounds
                        newLocation[1] += 1

                    if newLocation[0] > 0: # Check if X is in bounds
                        newLocation[0] -= 1
                    
                    if not (0 <= newLocation[0] < 8 and 0 <= newLocation[1] < 8):
                        break

                    name = self.GetPieceName(newLocation)

                    for move in self.moves:
                        if move.endRow == newLocation[1] and move.endCol == newLocation[0]:
                            blockingMoves.append(move)

            

        return blockingMoves

                     
    def GetPawnMoves(self, r, c, moves):
        if self.whiteToMove: #White pawn moves
            if self.board[r - 1][c] == "--": # 1 sq pawn move
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--":# 2 sq pawn move
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0: # Capture to the left
                if self.board[r - 1][c - 1][0] == "b": # enemey piece to capture
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
            if c + 1 <= 7: # Capture to the right
                if self.board[r - 1][c + 1][0] == "b":
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
        
        else: # black pawn moves
            if self.board[r + 1][c] == "--": # 1 sq pawn move
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":# 2 sq pawn move
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0: # Capture to the left
                if self.board[r + 1][c - 1][0] == "w": # enemey piece to capture
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
            if c + 1 <= 7: # Capture to the right
                if self.board[r + 1][c + 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))


    def GetRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) # Up, left, down, right
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": # no piece
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor: # enemy piece
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    else: # same color piece
                        break 
                else: # off board
                    break


    def GetKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allayColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allayColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))


    def GetBishopMoves(self, r, c, moves):
        directions = ((1, 1), (1, -1), (-1, -1), (-1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": # no piece
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    else: # same color piece
                        break 
                else: # off board
                    break


    def GetQueenMoves(self, r, c, moves):
        self.GetRookMoves(r, c, moves)
        self.GetBishopMoves(r, c, moves)


    def GetKingMoves(self, r, c, moves):
        kingMoves = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, -1))
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))




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