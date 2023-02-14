from copy import deepcopy

class Node(object):
    def __init__(self, game, move, prior, parent_node=None) -> None:
        self.game = game.copy()
        self.parent_node = parent_node

        self.visits = 0
        self.value_sum = 0
        self.prior = prior

        self.children = {}

    def is_expanded(self):
        return len(self.children) == 0

    def expand(self, prior):
        """Expands the current node given the prior

        Parameters
        ----------
        prior : 2d array
            A 2d array prior distribution over the possible board and positions 
            (assumed to be pre-masked and pre-normalized)
        """
        boards, moves = self.game.get_possible_moves()

        for idx, board in enumerate(boards):
            for pos in moves[idx]:
                temp_board = self.game.copy()
                temp_board.move(board, pos)
                self.children[board] = Node(temp_board, (board, pos), prior[board][pos], self)


    def value(self):
        return self.value_sum / (self.visits + 1e-5)

    def copy(self):
        return deepcopy(self)


# Use a recursive function to run "simulations" number of depth-first searches essentially
def mcts_search(node, simulations, c_puct, neural_net):
    if not node.game.result() is None:
        # TODO: Create proper return once the game is over
        return 

    if not node.is_expanded():
        value, prior = neural_net(node.board.get_features())
        # TODO: Maks and renormalize the prior
        node.expand(prior)
        return -value
    
    mcts_search(node, simulations, c_puct, neural_net)
        

def mcts_simulation(init_board, network, simulations_per_move):
    current_node = None(init_board)
    prior = network(init_board.get_features())[0]
    current_node.expand(init_board, prior)

    policies = []
    values = []

    # Run until we reach a terminal node
    while current_node.game.get_result() is None:
        # Traverse to the next best node based on Monte Carlo simulations and UCB selection
        for _ in range(simulations_per_move):
            mcts_search(current_node, simulations_per_move, c_puct=1, neural_net=network)