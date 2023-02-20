from ai.neuralnet import Network
from ai.tree import *
from game.tictactoe import TicTacToe
from game.ultimatettt import UltimateTTT
import torch

network = Network()
game = UltimateTTT()
root = Node(game, None, 0, None)

value, prior = network(root.game.get_features())
moves = root.game.get_possible_moves()

"""
total_move_board = []
for row in root.game.board:
    row_board = []
    for b in row:
        moved_board = np.where(b.board == ' ', 1, 0)
        row_board.append(moved_board)
    total_move_board.append(np.hstack(row_board))
print(np.vstack(total_move_board))
print(prior[0][torch.LongTensor(root.game.get_possible_moves())])
"""

# Mask the prior with only the possible moves
masked_prior = torch.zeros(81)
masked_prior[torch.LongTensor(root.game.get_possible_moves())] = prior[0][torch.LongTensor(root.game.get_possible_moves())]
masked_normalized_prior = masked_prior / torch.sum(masked_prior)

root.expand(masked_prior)

mcts_simulation(game, network, 250)
