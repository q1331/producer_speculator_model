import random
import math
import time
from mesa import Agent


class Strategy():

    def __init__(self, decision, pattern):
        self.score = 0
        self.decision = decision
        self.pattern = pattern

    def update_score(self, price_change):
        # 0 for increase 1 for decrease
        # 0 for sell 1 for buy
        self.score += 1 if self.decision == price_change else -1

    def make_decision(self):
        return self.decision


class StrategyManager():

    def __init__(self, model, memory_size):
        self.memory_size = memory_size
        format_string = '0' + str(memory_size) + 'b'
        self.strategies = {format(i, format_string) + str(j): Strategy(j, format(i, format_string))
                           for i in range(int(math.pow(2, memory_size))) for j in range(2)}
        self.model = model

    def pick_strategy(self):
        random.seed(time.time())
        format_string = '0' + str(self.memory_size + 1) + 'b'
        return self.strategies[format(random.getrandbits(self.memory_size + 1), format_string)]

    def update_strategy_scores(self):
        last_price = self.model.last_price
        price = self.model.price
        for strategy in self.strategies.values():
            # 0 for increase 1 for decrease
            price_change = -1 if last_price == price else 0 if last_price < price else 1
            strategy.update_score(price_change)

    def step(self):
        self.update_strategy_scores()
