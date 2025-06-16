"""
Tic Tac Toe Player
"""

import copy
import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    # X gets the first move
    o_count = sum(row.count(O) for row in board)
    x_count = sum(row.count(X) for row in board)
    if o_count >= x_count:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    # initialize actions set
    actions = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                actions.add((i, j))
    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    valid_actions = actions(board)
    (i, j) = action
    if (i, j) not in valid_actions:
        raise ValueError
    new_board = copy.deepcopy(board)  # clone the board so board is left intact
    new_board[i][j] = player(board)
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Check rows
    for row in board:
        if row[0] == row[1] == row[2] and row[0] != EMPTY:
            return row[0]

    # Check columns
    for j in range(3):
        if board[0][j] == board[1][j] == board[2][j] and board[0][j] != EMPTY:
            return board[0][j]

    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != EMPTY:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] != EMPTY:
        return board[0][2]

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # If there is a winner return True
    if winner(board) != None:
        return True

    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                return False

    # If all cells have been filled return True
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    # this function will only be called if terminal(board) is True
    win = winner(board)
    if win == X:
        return 1
    if win == O:
        return -1
    return 0


def max_value(board, alpha=-math.inf, beta=math.inf):
    if terminal(board):
        return utility(board)
    v = -math.inf
    for action in actions(board):
        v = max(v, min_value(result(board, action), alpha, beta))
        if v >= beta:
            return v
        alpha = max(alpha, v)
    return v


def min_value(board, alpha=-math.inf, beta=math.inf):
    if terminal(board):
        return utility(board)
    v = math.inf
    for action in actions(board):
        v = min(v, max_value(result(board, action), alpha, beta))
        if v <= alpha:
            return v
        beta = min(beta, v)
    return v


def minimax(board):
    """
    Returns the optimal action for the current player on the board using alpha-beta pruning.
    """
    if terminal(board):
        return None
    current_player = player(board)
    valid_actions = actions(board)
    optimal_action = None

    if current_player == X:
        v = -math.inf
        alpha = -math.inf
        beta = math.inf
        for action in valid_actions:
            temp_v = min_value(result(board, action), alpha, beta)
            if temp_v > v:
                v = temp_v
                optimal_action = action
            alpha = max(alpha, v)
    else:
        v = math.inf
        alpha = -math.inf
        beta = math.inf
        for action in valid_actions:
            temp_v = max_value(result(board, action), alpha, beta)
            if temp_v < v:
                v = temp_v
                optimal_action = action
            beta = min(beta, v)
    return optimal_action
