from copy import deepcopy
from operator import attrgetter
import numpy as np
import random
import math
import torch
from torch import nn

class Node(object):
    def __init__(self, game, move, node_prior, parent_node=None) -> None:
        self.game = game.copy()
        self.parent_node = parent_node

        self.move = move
        self.visits = 0
        self.value_sum = 0
        self.node_prior = node_prior

        self.children = []

    def is_expanded(self):
        return len(self.children) != 0

    def expand(self, prior):
        """Expands the current node given the prior

        Parameters
        ----------
        prior : 2d array
            A 2d array prior distribution over the possible board and positions
            (assumed to be pre-masked and pre-normalized)
        """
        moves = self.game.get_possible_moves()

        for m in moves:
            temp_board = self.game.copy()
            temp_board.move(m)
            self.children.append(Node(temp_board, m, prior[m], self))


    def value(self):
        return self.value_sum / self.visits if self.visits != 0 else 0

    def update(self, value):
        self.value_sum += value
        self.visits += 1

    def copy(self):
        return deepcopy(self)


def mcts_ucb(potential_node):
    # Factors in the neural network prior and the number of times the potential node was visited compared to the number of times its parent was visited
    # NOTE: I personally modified the denominator to ensure that all nodes are visited at least once
    prior_score = potential_node.node_prior * math.sqrt(potential_node.parent_node.visits) / (potential_node.visits + 1e-6)

    # Factors in the value of the potential node. We consider the negative version 
    # since we are in the perspective of the opposing player to the node in question
    value_score = -potential_node.value()
    return value_score + prior_score

# A recursive function that runs a single depth first search (computes a single
# trajectory and updates it)
def mcts_trajectory(node, c_puct, neural_net):

    if not node.game.get_result() is None:
        # In the event of a tie, the value of the position is 0
        if node.game.get_result() == '-':
            node.update(0)
            return 0

        # In the event that the next player to play wins, the previous move was a game LOSING move
        # Hence return -1 since that was the move that lost
        if node.game.get_result() == node.game.turn:
            node.update(1)
            return -1
        
        # This only executes if the winner of the game is not the current player, hence the previous move was a game WINNING move
        # Hence return 1 since that was the move that won
        node.update(-1)
        return 1

    if not node.is_expanded():
        value, prior = neural_net(node.game.get_features())
        masked_prior = torch.zeros(81)
        masked_prior[torch.LongTensor(node.game.get_possible_moves())] = prior[0][torch.LongTensor(node.game.get_possible_moves())]
        masked_normalized_prior = masked_prior / torch.sum(masked_prior)
        node.update(value)
        node.expand(masked_normalized_prior)
        return -value

    # Select the best child node based on the MCTS_UCB function (prior, visit count, and observed node value) 
    next_node = max(node.children, key=mcts_ucb)
    result = mcts_trajectory(next_node, c_puct, neural_net)
    node.update(result)
    return -result

def mcts_search(node, simulations, c_puct, neural_net):
    for _ in range(simulations):
        mcts_trajectory(node, c_puct, neural_net)

def mcts_simulation(init_board, network, simulations_per_move):
    value, prior = network(init_board.get_features())
    masked_prior = torch.zeros(81)
    masked_prior[torch.LongTensor(init_board.get_possible_moves())] = prior[0][torch.LongTensor(init_board.get_possible_moves())]
    masked_normalized_prior = masked_prior / torch.sum(masked_prior)

    # Creates the root node for the simulations
    current_node = Node(init_board, None, 0, None)
    current_node.expand(masked_normalized_prior)

    policies = []
    values = []

    # Run until we reach a terminal node
    while current_node.game.get_result() is None:

        # Traverse to the next best node based on Monte Carlo simulations and UCB selection
        mcts_search(current_node, simulations_per_move, c_puct=1, neural_net=network)

        # Create weights for each child based on their number of visits
        # If we're playing competitively, we would use the node that has the maximum number of visits
        # current_node = max(current_node.children, key=attrgetter('visits'))
        print([child.visits for child in current_node.children])
        total_visit_weights = [child.visits for child in current_node.children]
        current_node = random.choices(current_node.children, weights=total_visit_weights)[0]
        current_node.game.print_board()
        print()
    
    print(current_node.game.get_abstract_board())
    print(current_node.game.get_result())


        
        

