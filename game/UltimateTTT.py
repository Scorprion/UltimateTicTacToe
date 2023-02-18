from game.tictactoe import TicTacToe
import numpy as np
import random
from copy import deepcopy
import torch

class UltimateTTT(object):
    def __init__(self) -> None:
        self.board = np.array([TicTacToe() for _ in range(9)]).reshape(3, 3)
        self.possible_boards = np.arange(9)
        self.turn = 'O'

    def get_possible_moves(self):
        # No possible move if the game is done
        if not self.get_result() is None:
            return [], []

        possible_moves = []
        for b in self.possible_boards:
            for move in self.board.flatten()[b].get_possible_moves():
                possible_moves.append(b * 9 + move)
        return possible_moves

    def get_abstract_board(self):
        return np.asarray([' ' if b.get_result() is None else b.get_result() for b in self.board.flatten()]).reshape(3, 3)

    def get_result(self):
        abstract_board = self.get_abstract_board()

        # Only using the "next board" array to check if there is a possible move
        return TicTacToe.determine_ttt_winner(abstract_board, self.possible_boards)

    def move(self, move):
        # Ensure the given move is playable on the selected board
        assert(move in self.get_possible_moves())

        # Make the move
        board = int(move / 9)
        move_in_subboard = move - board * 9
        self.board.flatten()[board].move(move_in_subboard, self.turn)

        # Switch the turn to the other player
        self._switch_turn()

        # Per UTTT rules, the next board is the one the player moved at, unless it's already completed in which case the next move can be anywhere
        if self.board.flatten()[board].get_result() is None:
            self.possible_boards = np.array([move_in_subboard])
        else:
            self.possible_boards = np.argwhere(self.get_abstract_board().flatten() == ' ').flatten()

    def _switch_turn(self):
        self.turn = 'X' if self.turn == 'O' else 'O'

    def print_board(self):
        # Get 3 boards at a time
        for full_board_row in self.board:

            # Concatenate the 3 boards together
            boards_row = np.hstack([b.board for b in full_board_row])

            # Print each row of the 3 concatenated boards
            for row in boards_row:

                # Split each board (every 3 characters) and separate them by dividers '|'
                split_row = [row[i:i+3] for i in range(0, len(row), 3)]
                for segment in split_row:
                    print('|' + ' '.join(segment) + '|', end='')

                # Create a new line to separate each row
                print('')

            # Create a horizontal divider to separate each "full_board_row" (3 boards)
            print('---------------------')

    def get_features(self):
        total_x_board = []
        total_o_board = []
        for row in self.board:
            row_x_board = []
            row_o_board = []
            for b in row:
                x_board = np.where(b.board == 'X', 1, 0)
                o_board = np.where(b.board == 'O', 1, 0)
                row_x_board.append(x_board)
                row_o_board.append(o_board)
            total_x_board.append(np.hstack(row_x_board))
            total_o_board.append(np.hstack(row_o_board))
        if self.turn == 'O':
            return torch.from_numpy(np.expand_dims(np.stack((np.vstack(total_o_board),
                np.vstack(total_x_board)), axis=0), axis=0)).float()
        return torch.from_numpy(np.expand_dims(np.stack((np.vstack(total_x_board), np.vstack(total_o_board)),
                axis=0), axis=0)).float()

    def copy(self):
        return deepcopy(self)
        
"""
test = UltimateTTT()

while test.get_result() is None:
    test.print_board()
    possible_boards, possible_moves = test.get_possible_moves()
    print(possible_boards, possible_moves)
    board_idx = random.randint(0, len(possible_boards) - 1)
    move = random.choice(possible_moves[board_idx])
    test.move(possible_boards[board_idx], move)
    # board, move = input('Board: {} Move: {} \nInput your move:'.format(*test.get_possible_moves())).split()
    # test.move(int(board), int(move))
test.print_board()
print(test.get_features())
print('On top is the %s board' % test.turn)
print(test.get_abstract_board(), test.get_result())
"""

