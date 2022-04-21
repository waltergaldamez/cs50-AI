"""
Tic Tac Toe Player
"""

import math
import copy
from operator import ne

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    xCount = 0
    oCount = 0

    for row in board:
        for cell in row:
            if cell == X:
                xCount += 1
            elif cell == O: 
                oCount +=1

    return X if xCount == oCount else O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    moves = set()

    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] is EMPTY:
                moves.add((row, col))
    return moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    newBoard = copy.deepcopy(board)
    playerTurn = player(board)
    if terminal(board):
        return board

    if board[action[0]][action[1]] is not EMPTY:
        raise Exception("cant play that move")
    
    newBoard[action[0]][action[1]] = playerTurn

    return newBoard


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    row = None
    for i in range(3):
        row = board
        if board[i][0] == board[i][1] and board[i][1] == board[i][2]:
            return board[i][0]
        if row[0][i] == row[1][i] and row[1][i] == row[2][i]:
            return row[0][i]
    
    if row[0][0] == row[1][1] and row[1][1] == row[2][2]:
        return row[0][0]
    
    if row[2][0] == row[1][1] and row[1][1] == row[0][2]:
        return row[2][0]
    
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True
    
    for row in board:
        for cell in row:
            if cell == EMPTY:
                return False
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    w = winner(board)
    mapper = {X: 1, O: -1, EMPTY: 0}

    return mapper[w]

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    retMove = None
    playerTurn = player(board)
    possibleMoves = actions(board)

    for move in possibleMoves:
        newBoard = result(board, move)
        score = minValue(newBoard) if playerTurn == X else maxValue(newBoard)
        if score == 1 and playerTurn == X:
            return move
        elif score == -1 and playerTurn == O:
            return move
        elif score == 0:
            retMove = move
    
    return possibleMoves.pop() if retMove is None else retMove

def maxValue(board):
    score = -100
    if terminal(board):
        return utility(board)
        
    possibleMoves = actions(board)

    for move in possibleMoves:
        newBoard = result(board, move)
        score = max(score, minValue(newBoard))
    
    return score

def minValue(board):
    score = 100
    if terminal(board):
        return utility(board)
    possibleMoves = actions(board)

    for move in possibleMoves:
        newBoard = result(board, move)
        score = min(score, maxValue(newBoard))
    
    return score
    

