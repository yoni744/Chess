import chess
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

    def CheckLegalMove(self, move):
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
    
    def getChessNotation(self):
        return self.GetRankFile(self.startRow, self.startCollum) + self.GetRankFile(self.endRow, self.endCollum)

    def GetRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    