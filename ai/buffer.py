import os
import torch
import random
from operator import itemgetter
from datetime import datetime
import glob

class PlayerBuffer(object):
    def __init__(self, save_dir):
        self.save_dir = save_dir
        self.players = []

    def store(self, network):
        now = datetime.now()
        torch.save(network.state_dict(), self.save_dir + now.strftime('%m_%d_%Y_%H%M%S') + '.pt')
        self._update_players()
    
    def _update_players(self):
        self.players = [file for file in glob.glob('*.pt', root_dir=self.save_dir)]

    def retrieve(self, batch_size, replacement):
        return random.choices(self.players, k=batch_size, replacement=replacement)


class DataBuffer(object):
    def __init__(self):
        self.states = []
        self.policies = []
        self.values = []

    def store(self, states, policies, values):
        self.states.extend(states)
        self.policies.extend(policies)
        self.values.extend(values)

    def retrieve(self, batch_size):
        total_list = list(zip(self.states, self.policies, self.values))
        random.shuffle(total_list)
        s, p, v = zip(*total_list)
        for i in range(0, len(self.states), batch_size):
            yield s[i:i+batch_size], p[i:i+batch_size], v[i:i+batch_size]

    def clear(self):
        self.states = []
        self.policies = []
        self.values = []