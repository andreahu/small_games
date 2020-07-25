"""
Tic Tac Toe Player
"""

import math
import copy

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
    for i in range(3):
        for j in range(3):
            if board[i][j] == X:
                xCount +=1
    for i in range(3):
        for j in range(3):
            if board[i][j] == O:
                oCount +=1
    if xCount > oCount:
        return O
    else:
        return X



def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """

    validActions = set()
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == EMPTY:
                action = (i,j)
                validActions.add(action)
    return validActions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    i = action[0]
    j = action[1]
    currentPlayer = player(board)
    newBoard = copy.deepcopy(board)
    newBoard[i][j] = currentPlayer
    return newBoard


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    win_state = [
        [board[0][0], board[0][1], board[0][2]],
        [board[1][0], board[1][1], board[1][2]],
        [board[2][0], board[2][1], board[2][2]],
        [board[0][0], board[1][0], board[2][0]],
        [board[0][1], board[1][1], board[2][1]],
        [board[0][2], board[1][2], board[2][2]],
        [board[0][0], board[1][1], board[2][2]],
        [board[2][0], board[1][1], board[0][2]]
    ]

    if [X, X, X] in win_state:
        return X
    elif [O, O, O] in win_state:
        return O
    else:
        return None
        

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """

    if utility(board) == 0:
        for i in range(3):
            for j in range(3):
                if board[i][j] == EMPTY:
                    return False
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """

    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    best = (None, None)
    if player(board) == X:
        v = -math.inf
        for action in actions(board):
            currentV = minValue(result(board,action))
            if currentV > v:
                v = currentV
                best = action
    elif player(board) == O:
        v = math.inf
        for action in actions(board):
            currentV = maxValue(result(board,action))
            if currentV < v:
                v = currentV
                best = action
    return best


def maxValue(board):
    """
    Returns the max score that could achieve from the next move 
    """

    if terminal(board):
        return utility(board)
    v = -math.inf
    for action in actions(board):
        v = max(v, minValue(result(board,action)))
    return v


def minValue(board):
    """
    Returns the minimum score that could achieve from the next move 
    """

    if terminal(board):
        return utility(board)
    v = math.inf
    for action in actions(board):
        v = min(v, maxValue(result(board,action)))
    
    return v


