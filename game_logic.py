class UltimateTicTacToe:
    def __init__(self):
        self.x_board = [0] * 9  # Bit boards: each int represents 1 board. Pieces are stored based on the binary of the integer
        self.o_board = [0] * 9
        self.total_board = 0  # First 9 bits is the x_board, next 9 bits is the o_board
        self.lazy_eval = set()  # List of boards we need to recalculate
        self.result = None
        self.turn = 1  # 1 for 'X' and -1 for 'O'

        self.board_stack = [None]  # for undoing moves
        self.move_stack = [None]

        # Constants for the winning positions (row major order)
        self.WINNING_POS = [
            0b111000000,  # top row
            0b000111000,  # middle row
            0b000000111,  # bottom row
            0b100100100,  # left col
            0b010010010,  # middle col
            0b001001001,  # right col
            0b100010001,  # diagonal
            0b001010100   # other diagonal
        ]

        self.RESULTS = [
            0b10,  # X won
            0b01,  # O won
            0b11   # draw
        ]

    def play(self, board_num, pos):
        # Ensure the move is legal
        #if (board_num, pos) not in self.get_legal_moves(self.current_board):
        #    raise ValueError(f"Cannot move at pos {pos} on board {board_num}")

        # Shift a 1 to the corresponding position to play
        move_bit = 1 << (8 - pos)

        # Play on the corresponding board
        if self.turn == 1:
            self.x_board[board_num] |= move_bit
            board = self.x_board
        else:
            self.o_board[board_num] |= move_bit
            board = self.o_board

        # Check for a win or draw
        draw = (self.x_board[board_num] | self.o_board[board_num]) == 0b111111111
        win = any([pattern & board[board_num] == pattern for pattern in self.WINNING_POS]) 
        if win:
            # If there was a win, mark the board as complete
            # A board is complete if the 10th and/or 11th bits are set
            if self.turn == 1:
                self.x_board[board_num] |= (0b10 << 10)
                self.o_board[board_num] |= (0b10 << 10)
            else:
                self.x_board[board_num] |= (0b01 << 10)
                self.o_board[board_num] |= (0b01 << 10)
            
            # there was a new winning board, so we need to update the total board eventually
            self.lazy_eval.add(board_num)
        elif draw:
            self.x_board[board_num] |= (0b11 << 10)
            self.o_board[board_num] |= (0b11 << 10)
            # there was a new board that tied, so we need to update the total board again
            self.lazy_eval.add(board_num)

        self.turn = -self.turn  # flip turn
        current_board = pos if ((self.x_board[pos] >> 10) & 1) == 0 else None  # the new board to play at is position, if you can play there, otherwise it is anywhere
        self.board_stack.append(current_board)
        self.move_stack.append((board_num, pos))

    @property
    def current_board(self):
        return self.board_stack[-1]

    def undo_play(self):
        if len(self.board_stack) <= 1:
            raise ValueError("Attempted to undo from starting board")

        self.board_stack.pop()
        (undo_board, undo_pos) = self.move_stack.pop()

        move_bit = ~((0b11 << 10) | (1 << (8 - undo_pos)))

        # Play on the corresponding board
        self.x_board[undo_board] &= move_bit
        self.o_board[undo_board] &= move_bit

        self.lazy_eval.add(undo_board)

        self.turn = -self.turn

    def get_result(self):
        if self.lazy_eval:
            self.is_finished()
        return self.result
        
    def is_board_complete(self, board):
        return (self.x_board[board] >> 10 & 0b11) > 0

    def get_legal_moves(self, board):
        """
        # No legal moves if the game is done
        if self.is_finished():
            return []
        """
        
        if board is None or self.is_board_complete(board):
            # Any board can be played on
            boards_to_check = range(9)
        else:
            # Only the "self.current_board" can be played on
            boards_to_check = [board]
        

        # For each board we can play on, find all of the 0s and return the list
        # Store moves as (board_num, pos)
        moves = []
        for b in boards_to_check:
            # If board is done, there are no possible moves
            if self.is_board_complete(b):
                continue
            curr_board = self.x_board[b] | self.o_board[b]
            for pos in range(9):
                if (curr_board >> (8 - pos) & 1) == 0:
                    moves.append((b, pos))
        return moves

    def get_turn(self):
        return self.turn

    def get_board_features(self):
        pass

    def is_finished(self):
        # If the total board has been updated, we need to refresh the total_board
        if len(self.lazy_eval) != 0:
            self.result = None
            while self.lazy_eval:
                i = self.lazy_eval.pop()
                board = self.x_board[i]
                i = 8 - i
                self.total_board &= ~(1 << i | 1 << (i + 9) | 1 << (i + 18))
                if ((board >> 10) & 0b11) > 0:
                    if ((board >> 10) & 0b11) == 0b10:
                        self.total_board |= (1 << i)  # x_board
                    elif ((board >> 10) & 0b11) == 0b01:
                        self.total_board |= (1 << (i + 9))  # o_board
                    else:
                        self.total_board |= (1 << (i + 18))  # draw board

            for pattern in self.WINNING_POS:
                if (pattern & self.total_board == pattern):
                    self.result = 1
                    return True
                if (pattern & (self.total_board >> 9)) == pattern:
                    self.result = -1
                    return True

            mask = (1 << 9) - 1
            draw = ((self.total_board & mask) | ((self.total_board >> 9) & mask) | ((self.total_board >> 18) & mask)) == mask
            if draw:
                self.result = 0
        return self.result is not None

    def to_string(self):
        """
        Print all 9 boards in a 3x3 Ultimate TicTacToe grid with separators.
        boards_x: List of 9 integers representing X's bitboards for each local board.
        boards_o: List of 9 integers representing O's bitboards for each local board.
        """
        def local_board_to_rows(x_board, o_board, i):
            """Convert a single local board into 3 rows of strings."""
            rows = []
            pos = 8
            for _ in range(3):
                row = ""
                for j in range(3):
                    if x_board & (1 << pos):  # X's position
                        row += "X "
                    elif o_board & (1 << pos):  # O's position
                        row += "O "
                    #elif i == self.current_board:
                     #   row += f"{8 - pos} "
                    else:
                        row += ". "
                    pos -= 1
                rows.append(row)
            return rows

        # Collect all rows for the 9 local boards
        all_board_rows = [local_board_to_rows(self.x_board[i], self.o_board[i], i) for i in range(9)]
        
        # Build the Ultimate TicTacToe grid
        result = ""
        for i in range(3):  # Iterate over the 3 groups of local boards (rows)
            for row in range(3):  # For each row in a local board
                result += " | ".join(all_board_rows[i * 3 + j][row] for j in range(3))  # Combine 3 boards horizontally
                result += "\n"
            if i < 2:  # Add horizontal divider between groups of 3 boards
                result += "-------+--------+--------\n"
        return result

    def completed_boards(self):
        if self.lazy_eval:
            self.is_finished()
        res = []
        pos = 8
        for i in range(3):
            for j in range(3):
                if self.total_board & (1 << pos):  # X's position
                    res.append((1, 8 - pos))
                elif (self.total_board >> 9) & (1 << pos):  # O's position
                    res.append((-1, 8 - pos))
                elif (self.total_board >> 18) & (1 << pos):
                    res.append((0, 8 - pos))
                pos -= 1
        return res
    
    def total_to_string(self):
        if self.lazy_eval:
            self.is_finished()
        rows = []
        pos = 8
        for i in range(3):
            row = ""
            for j in range(3):
                if self.total_board & (1 << pos):  # X's position
                    row += "X "
                elif (self.total_board >> 9) & (1 << pos):  # O's position
                    row += "O "
                elif (self.total_board >> 18) & (1 << pos):
                    row += "- "
                else:
                    row += ". "
                pos -= 1
            rows.append(row)
        result = ""
        for row in rows:
            result += row + '\n'
        return result
