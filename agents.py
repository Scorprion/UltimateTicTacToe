import random

class MiniMax:
    def __init__(self, depth, n_sims=100, verbose=False):
        self.depth = depth
        self.n_sims = n_sims
        self.verbose = verbose
        self.win_percent = 0.5

    def get_move(self, board):
        # _, move = self.search(board, self.depth, board.turn == 1)
        val, move = self.alpha_beta_search(board, self.depth, alpha=float('-inf'), beta=float('inf'), maximizing=board.turn == 1)
        self.win_percent = (val + self.n_sims) / (2 * self.n_sims)
        self.win_percent = self.win_percent if board.turn == 1 else 1 - self.win_percent
        if self.verbose:
            print('Change of winning: {:.1%}'.format(self.win_percent if board.turn == 1 else 1 - self.win_percent))

        return move

    def search(self, board, depth, maximizing):
        # For each possible move, compute its value
        # Choose the min of the values to continue searching
        if depth <= 0 or board.is_finished():
            return self._heuristic(board), None
        if maximizing:
            moves = board.get_legal_moves(board.current_board)
            max_move = moves[0]
            max_val, _ = self.search(board, depth - 1, not maximizing)
            for move in moves[1:]:
                board.play(*move)
                new_val, _ = self.search(board, depth - 1, not maximizing)
                board.undo_play()
                if max_val < new_val:
                    max_val = new_val
                    max_move = move
            return max_val, max_move
        else:
            moves = board.get_legal_moves(board.current_board)
            min_move = moves[0]
            min_val, _ = self.search(board, depth - 1, not maximizing)
            for move in moves[1:]:
                board.play(*move)
                new_val, _ = self.search(board, depth - 1, not maximizing)
                board.undo_play()
                if min_val > new_val:
                    min_val = new_val
                    min_move = move
            return min_val, min_move

    def alpha_beta_search(self, board, depth, alpha, beta, maximizing):
        """
        Optimization of naive minimax search that utilizes early stopping
        Key Idea: if we find that a branch has a path that yields a result
        better than one we have already seen for the opposing player, we know already
        we're not going to ever pick that branch, so we can stop evaluating it
        """
        if depth <= 0 or board.is_finished():
            return self._heuristic(board), None
        if maximizing:
            max_move = None
            max_val = float('-inf')
            for move in board.get_legal_moves(board.current_board):
                board.play(*move)
                new_val, _ = self.alpha_beta_search(board, depth - 1, alpha, beta, not maximizing)
                board.undo_play()
                if max_val <= new_val:
                    max_val = new_val
                    max_move = move
                alpha = max(max_val, alpha)

                # if the branch you're currently searching has a value better than the value in some other branch,
                # the min player would never pick this one
                if alpha >= beta:
                    break
            return max_val, max_move
        else:
            min_move = None
            min_val = float('inf')

            for move in board.get_legal_moves(board.current_board):
                board.play(*move)
                new_val, _ = self.alpha_beta_search(board, depth - 1, alpha, beta, not maximizing)
                board.undo_play()

                if min_val >= new_val:
                    min_val = new_val
                    min_move = move
                beta = min(min_val, beta)
                if beta <= alpha:
                    break
            return min_val, min_move



    def _heuristic(self, board):
        def helper(board):
            if board.is_finished():
                return board.result * 100
            move = random.choice(board.get_legal_moves(board.current_board))
            board.play(*move)
            val = helper(board)
            board.undo_play()
            return val

        res = 0
        for _ in range(self.n_sims):
            res += helper(board)
        return res / self.n_sims

    def _heuristic2(self, board):
        # Difference between X's boards and O's boards, infinity for game outcomes, 0 for draws
        if board.result is not None:
            return board.result * float('100')
        
        res = 0
        if board.lazy_eval:
            board.is_finished()
        for pattern in board.WINNING_POS:
            # Add the number of boards that align with the winning patterns
            res += (board.total_board & pattern).bit_count()  
            res -= ((board.total_board >> 9) & pattern).bit_count()
        return res

class Random:
    def __init__(self):
        pass

    def get_move(self, board):
        return random.choice(board.get_legal_moves(board.current_board))

class Human:
    def __init__(self):
        pass
    
    def get_move(self, board):
        print(board.to_string())
        print(board.get_legal_moves(board.current_board))
        move = input("Your move: ")
        return (int(i) for i in move.split(' '))
