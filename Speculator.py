from mesa import Agent


class Speculator(Agent):
    def __init__(self, unique_id, model, money, memory_size, prudent_factor, strategy_manager):
        super().__init__(unique_id, model)
        self.wealth = money
        self.strategy = None
        self.memory_size = memory_size
        self.strategy_manager = strategy_manager
        self.pick_new_strategy()
        self.last_decision = 0
        self.join_time = 0
        self.last_order = 0
        self.money = money
        self.stocks = 0
        self.prudent_factor = prudent_factor
        self.participating = False

    def pick_new_strategy(self):
        self.strategy = self.strategy_manager.pick_strategy()
        self.join_time = self.model.schedule.steps

    def randomize_strategy(self):
        self.strategy = self.strategy_manager.pick_strategy()

    def calc_wealth(self):
        self.wealth = self.money + self.stocks * self.model.price

    def invest(self):
        delta_amount = self.prudent_factor * (2 * self.strategy.make_decision(self.model) - 1)
        if self.model.demand > self.model.offer and delta_amount > 0:
            delta_amount = delta_amount * self.model.offer / self.model.demand
        if self.model.demand < self.model.offer and delta_amount < 0:
            delta_amount = delta_amount * self.model.demand / self.model.offer
        self.last_order = delta_amount
        self.money -= delta_amount * self.model.price
        self.stocks += delta_amount

    def step(self):
        if (self.strategy.crazy or self.strategy.pattern == self.model.memory) and \
        (self.join_time == 0 or self.strategy.score / self.join_time > 0.05) and \
                self.wealth > 0:
            self.participating = True
            self.invest()
            self.calc_wealth()
        else:
            self.participating = False
