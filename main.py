from ai.neuralnet import Network
from ai.tree import Node, mcts_simulation, mcts_search, mcts_trajectory, mcts_ucb
from ai.buffer import PlayerBuffer, DataBuffer
from game.tictactoe import TicTacToe
from game.ultimatettt import UltimateTTT
from torch import optim, nn
import torch
import os

def train(network, data_buffer: DataBuffer, batch_size, epochs):
    # Sets the proper mode for the dropout
    network.train()

    for _ in range(epochs):
        for states, policies, values in data_buffer.retrieve(batch_size=batch_size):
            # Zero'ing gradients each batch (otherwise it combines the batches)
            optimizer.zero_grad()

            batch_states = torch.cat(states, axis=0)
            batch_policies = torch.stack(policies, axis=0)
            batch_values = torch.stack(values, axis=0).view(-1, 1)

            pred_values, log_pred_policies = network(batch_states)

            loss = value_loss(pred_values, batch_values) + policy_loss(log_pred_policies, batch_policies)
            print('Loss: %.5f' % loss.item())
            loss.backward()
            optimizer.step()

N_GAMES = 3
N_EPOCHS = 25
BATCH_SIZE = 32
SIMS_PER_MOVE = 10

network = Network()
value_loss = nn.MSELoss(reduction='mean')
policy_loss = nn.CrossEntropyLoss(reduction='mean')
optimizer = optim.RMSprop(network.parameters(), lr=0.001)

game = UltimateTTT()
data = DataBuffer()
player_buffer = PlayerBuffer(save_dir=os.getcwd() + 'models\\')

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

while True:
    for _ in range(N_GAMES):
        states, policies, values = mcts_simulation(game, network, SIMS_PER_MOVE)
        data.store(states, policies, values)

    train(network, data, BATCH_SIZE, N_EPOCHS)

