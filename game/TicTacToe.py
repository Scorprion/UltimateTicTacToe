import numpy as np
from copy import deepcopy
import torch

class TicTacToe(object):
    def __init__(self, board=None) -> None:
        """Creates a TicTacToe object

        Parameters
        ----------
        board : array, optional
            The current board state. If left unspecified, a new board will be created. By default None
        """

        if board is not None:
            self.board = np.asarray(board)
        else:
            self.board = np.full((3, 3), ' ')

        self.move_list = np.argwhere(self.board.flatten() == ' ').flatten().tolist()

        # TODO: Remove this after testing
        self.turn = 'O'

    def get_possible_moves(self) -> list:
        return self.move_list if self.get_result() is None else []

    @staticmethod
    def determine_ttt_winner(board, move_list):
        # Check rows
        for row in board:
            unique = list(set(row))
            if len(unique) == 1 and not ' ' in unique:
                return unique[0]

        # Check vertical
        for col in board.T:
            unique = list(set(col))
            if len(unique) == 1 and not ' ' in unique:
                return unique[0]

        # Check diagonals
        main_diag = np.diag(board)
        unique = list(set(main_diag))
        if len(unique) == 1 and not ' ' in unique:
            return unique[0]

        opp_diag = np.diag(np.fliplr(board))
        unique = list(set(opp_diag))
        if len(unique) == 1 and not ' ' in unique:
            return unique[0]

        # Check for a tie
        if len(move_list) == 0:
            return '-'
        return None

    def get_result(self) -> str:
        return TicTacToe.determine_ttt_winner(self.board, self.move_list)

    def move(self, move, turn=None) -> None:
        # Ensure the move is valid
        assert(move in self.get_possible_moves())

        # Put the move on the board
        self.board[move // 3][move % 3] = self.turn if turn is None else turn

        # Remove the move from the "possible move" list (it doesn't update dynamically to save some resources)
        self.move_list.remove(move)

        # Make it the next player's turn if playing the classic way (not a subboard of a UTTT game)
        if turn is None:
            self._switch_turn()

    def _switch_turn(self):
        self.turn = 'X' if self.turn == 'O' else 'O'

    def __str__(self):
        return str(self.board)

    def copy(self):
        return deepcopy(self)
    
    def get_features(self):
        row_x_board = []
        row_o_board = []
        for row in self.board:
            x_board = np.where(row == 'X', 1, 0)
            o_board = np.where(row == 'O', 1, 0)
            row_x_board.append(x_board)
            row_o_board.append(o_board)
        
        if self.turn == 'O':
            return torch.from_numpy(np.expand_dims(np.stack((np.vstack(row_x_board), np.vstack(row_o_board)), axis=0), axis=0)).float()
        return torch.from_numpy(np.expand_dims(np.stack((np.vstack(row_o_board), np.vstack(row_x_board)), axis=0), axis=0)).float()