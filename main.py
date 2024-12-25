from game_logic import UltimateTicTacToe
from agents import Human, MiniMax, Random
import random
import time

"""
seed = sys.argv[1]
random.seed(int(seed))
"""

for i in range(1):
    uttt = UltimateTicTacToe()
    agent1 = Random()
    agent2 = MiniMax(2, n_sims=250, verbose=True)
    agent3 = Human()
    curr_agent = agent2
    while not uttt.is_finished():
        move = curr_agent.get_move(uttt)
        uttt.play(*move)
        print(uttt.to_string())
        print(uttt.total_to_string())
        if curr_agent == agent2:
            curr_agent = agent3
        else:
            curr_agent = agent2
    print(uttt.to_string())
    print(uttt.total_to_string())
    print(uttt.get_result())
