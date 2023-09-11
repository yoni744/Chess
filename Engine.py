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
        
        self.whiteToMove = True
        self.moveLog = []


    def MakeMove(self, move):
        self.board[move.startRow][move.startCollum] = "--"
        self.board[move.endRow][move.endCollum] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

    def GetValidMoves(self):    # All moves, with check
        return self.GetAllPossibleMoves()

    def GetAllPossibleMoves(self):    #All possible moves
        moves = []
        for r in range(len(self.board)): # num of rows
            for c in range(len(self.board[r])): # num of colls in row
                turn = self.board[r][c][0]
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1] # Taking piece's name from given square
                    if piece == "p":
                        self.GetPawnMoves(r, c, moves)
                        print(moves)
                    elif piece == "R":
                        self.GetRookMoves(r, c, moves)
        return moves

    def GetPawnMoves(self, r, c, moves):
        if self.whiteToMove: #White pawn moves
            if self.board[r - 1][c] == "--": # 1 sq pawn move
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--":# 2 sq pawn move
                    moves.append(Move((r, c), (r-2, c), self.board))


    def GetRookMoves(self, r, c, moves):
        pass



class Move():
    rankToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                    "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in rankToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                    "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCollum = startSq[1]
        self.endRow = endSq[0]
        self.endCollum = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCollum]
        self.pieceCaptured = board[self.endRow][self.endCollum]
        self.moveID = self.startRow * 1000 + self.startCollum * 100 + self.endRow * 10 + self.endCollum #Creating a uniqe move ID for every move 1,1 to 1,2 = 1112


        # Overriding the equals method
        def __eq__(self, other):
            if isinstance(other, Move):
                return self.moveID == other.moveID
            return False

    
    def getChessNotation(self):
        return self.GetRankFile(self.startRow, self.startCollum) + self.GetRankFile(self.endRow, self.endCollum)

    def GetRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    