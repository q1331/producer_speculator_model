import random
import math
import time
from mesa import Agent


class Strategy():

    def __init__(self, pattern):
        self.score = 1
        # randomly initialize initial decision to balance offer and demand
        self.decision = int(pattern[-1])
        self.pattern = pattern

    def update_score(self, price_change):
        # 0 for increase 1 for decrease
        # 0 for sell 1 for buy
        self.score += 1 if self.decision == price_change else -1

    def make_decision(self, model):
        information = self.pattern
        if model.schedule.steps >= model.memory_size:
            information += model.memory
        one_count = information.count("1")
        zero_count = information.count("0")
        self.decision = 1 if one_count > zero_count else 0
        return self.decision


class StrategyManager():

    def __init__(self, model, memory_size):
        self.memory_size = memory_size
        self.format_string = '0' + str(memory_size) + 'b'
        self.strategies = {format(i, self.format_string): Strategy(format(i, self.format_string))
                           for i in range(int(math.pow(2, memory_size)))}
        self.model = model

    def pick_strategy(self):
        random.seed(time.time())
        return self.strategies[format(random.getrandbits(self.memory_size), self.format_string)]

    def update_strategy_scores(self):
        last_price = self.model.last_price
        price = self.model.price
        for strategy in self.strategies.values():
            # 0 for increase 1 for decrease
            price_change = -1 if last_price == price else 0 if last_price < price else 1
            strategy.update_score(price_change)

    def step(self):
        self.update_strategy_scores()
