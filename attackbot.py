import random
import game
import copy
import math
import time
import numpy as np
from bitboard import NUM_BOARDS, BOARD_ROWS, BOARD_COLS, pos_to_index, index_to_pos

# Precomputed piece values (indices 1..15, with 0 for empty)
piece_values_arr = np.array([0, 1, 5, 8, 5, 2.5, 4.5, 4, 9, 11, 10000, 10, 1, 3, 4, 2], dtype=np.float64)

# Move flag constants (must match those in your move generators)
QUIET     = 0
CAPTURE   = 1
AFAR      = 2
AMBIGUOUS = 3
THREED    = 4

def board_state_hash(state):
    board, turn_flag = state
    # Fast hash using Python’s built‑in hash on the board’s bytes and turn flag.
    return hash((board.tobytes(), turn_flag))

# Import the Numba‑compiled move generators (they work on positions expressed as 1D indices)
from game import move_generators

def get_all_moves(state, color):
    """
    Given a state (board, turn_flag) where board is a flat NumPy array and
    color is 1 for Gold or -1 for Scarlet, return all legal moves.
    Each move is a triple (from_index, to_index, flag).
    Moves are ordered so that captures (or "afar" moves) come first.
    """
    board, _ = state
    moves = []
    for idx in range(board.size):
        piece = board[idx]
        if piece != 0 and (color * piece > 0):
            pos = index_to_pos(idx)
            abs_code = abs(piece)
            gen_func = move_generators.get(abs_code)
            if gen_func is not None:
                candidate_moves = gen_func(pos, board, color)
                for move in candidate_moves:
                    from_idx, to_idx, flag = move
                    # For QUIET moves, the destination must be empty.
                    if flag == QUIET and board[to_idx] != 0:
                        continue
                    # For CAPTURE/AFAR moves, destination must hold an enemy.
                    elif flag in (CAPTURE, AFAR):
                        if board[to_idx] == 0 or (color * board[to_idx] > 0):
                            continue
                    if check_move(move):
                            moves.append(move)
    return moves

def check_move(move):
    from_idx, to_idx, flag = move
    moving_piece = game.board[from_idx]  
    target_piece = game.board[to_idx]

    if game.target_piece != 0 and ((game.moving_piece > 0 and game.target_piece < 0) or (game.moving_piece < 0 and game.target_piece > 0)):
            return True
            #this is taking a target piece (from the enemy)
        
# --- Custom AI using Heuristic ---
class CustomAI:
    """
    A simple minimax AI with alpha–beta pruning, iterative deepening, and a 5‑second
    time limit. The board is stored as a flat NumPy array, so move indices are integers.
    """
    def __init__(self, game, color):
        self.game = game
        self.color = color  # "Gold" or "Scarlet"

    def choose_move(self):
        turn = self.game.current_turn  # "Gold" or "Scarlet"
        turn_flag = 1 if turn == "Gold" else -1
        # Our game.board is a flat NumPy array.
        state = (self.game.board.copy(), turn_flag)
        history = self.game.state_history
        # Use 1 if "Gold", -1 if "Scarlet" for my_color.
        my_color_flag = 1 if self.color == "Gold" else -1
        moves = get_all_moves(state, state[1])
        if len(moves)==0: 
            all_moves = self.game.get_all_moves()
            return random.choice(all_moves)
        else: 
            return random.choice(moves)

