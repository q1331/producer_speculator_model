from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import CanvasGrid, BarChartModule, PieChartModule, TextElement
from mesa.visualization.modules import ChartModule
from tabulate import tabulate


from MoneyModel import *

gird_height = 50
gird_width = 50
canvas_height = 500
canvas_width = 500
chart_canvas_width = 500
chart_canvas_height = 200

model_params = {"Ns": UserSettableParameter("slider", "Number of speculators", value=1000, min_value=1, max_value=5000),
                "Np": UserSettableParameter("slider", "Number of producers", value=50, min_value=1, max_value=5000),
                "influx": UserSettableParameter("slider", "Periodic money influx to producers(η)", value=0.001, min_value=0, max_value=1,step=0.001),
                "fluctuation_factor": UserSettableParameter("slider", "Price fluctuation factor(α)", value=0.02, min_value=0.001,step=0.001, max_value=1),
                "amplitude": UserSettableParameter("slider", "Amplitude of producer investment(ε)", value=0.01, min_value=0.001,step=0.001, max_value=1),
                "producer_money": UserSettableParameter("slider", "Initial producer cash", value=1, min_value=1, max_value=100),
                "initial_price": UserSettableParameter("slider", "Initial Price", value=1, min_value=1, max_value=100),
                "bias_factor": UserSettableParameter("slider", "Bias factor(λ)", value=0.01, min_value = 0.001, max_value=1,step=0.001, description="The parameter λ measures the strength of the bias caused by the intrinsic value of the commodity."),
                "memory_size": UserSettableParameter("slider", "Speculator memory size", value=10, min_value = 1, max_value=20, description="Length of the bit string."),
                "speculator_money": UserSettableParameter("slider", "Initial speculator money", value=1, min_value=1, max_value=100),
                "prudent_factor": UserSettableParameter("slider", "Speculator prudent factor(δ)", value=0.001, min_value=0.001, max_value=1, step=0.001),
                "crazy": UserSettableParameter("checkbox", "Crazy Speculators", value=False),
                "width": gird_width,
                "height": gird_height}


def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "r": 1}
    if agent.participating:
        if agent.last_order > 0:
            if isinstance(agent, Producer):
                portrayal["Color"] = "orange"
            else:
                portrayal["Color"] = "red"
        else:
            if isinstance(agent, Producer):
                portrayal["Color"] = "blue"
            else:
                portrayal["Color"] = "green"
        portrayal["Layer"] = 0
        portrayal["r"] = 1
    else:
        if isinstance(agent, Producer):
            portrayal["Color"] = "black"
        else:
            portrayal["Color"] = "grey"
        portrayal["Layer"] = 0
        portrayal["r"] = 1
    return portrayal


grid = CanvasGrid(agent_portrayal, grid_height=gird_height, grid_width=gird_width,
                  canvas_height=canvas_height, canvas_width=canvas_width)
chart = ChartModule([{"Label": "Average Producer Wealth", "Color": "red"},
                     {"Label": "Average Speculator Wealth", "Color": "green"}
                     ],
                    canvas_width=chart_canvas_width,
                    canvas_height=chart_canvas_height,
                    data_collector_name='datacollector')
wealth_chart = ChartModule([{"Label": "Max Speculator Wealth", "Color": "red"},
                            {"Label": "Min Speculator Wealth", "Color": "greed"},
                            {"Label": "Min Producer Wealth", "Color": "blue"},
                                  {"Label": "Max Producer Wealth", "Color": "orange"}],
                                 canvas_width=chart_canvas_width,
                                 canvas_height=chart_canvas_height,
                                 data_collector_name='datacollector')
price_chart = ChartModule([{"Label": "Price",
                            "Color": "black"}],
                          data_collector_name='datacollector')

participation_chart = ChartModule([{"Label": "Speculator Participation Rate", "Color": "red"},
                                   {"Label": "Producer Participation Rate", "Color": "green"}
                                   ],
                                  data_collector_name='datacollector')
max_score_chart = ChartModule([{"Label": "Strategies Max Score",
                                    "Color": "orange"},
                               {"Label": "Strategies Min Score",
                                    "Color": "blue"}
                               ],
                                  data_collector_name='datacollector')

fluctuation_chart = ChartModule([{"Label": "Fluctuation",
                                "Color": "purple"}],
                              data_collector_name='datacollector')

agent_bar = BarChartModule([{"Label": "Wealth", "Color": "blue"}], scope="agent")

producer_pie_chart = PieChartModule([
                            {"Label": "Good Producer", "Color": "red"},
                            {"Label": "Bad Producer", "Color": "green"}])

speculator_pie_chart = PieChartModule([
    {"Label": "Good Speculator", "Color": "red"},
    {"Label": "Bad Speculator", "Color": "green"}])

strategy_pie_chart = PieChartModule([
    {"Label": "Good Strategy", "Color": "red"},
    {"Label": "Neutral Strategy", "Color": "grey"},
    {"Label": "Bad Strategy", "Color": "green"}])

class ScoreTable(TextElement):
    '''
    Display a text count of how many happy agents there are.
    '''
    def __init__(self):
        super().__init__()

    def render(self, model):
        result = tabulate([[int(k[:-1],2), v.score] for k, v in model.strategy_manager.strategies.items()])
        return result

class WealthTable(TextElement):
    '''
    Display a text count of how many happy agents there are.
    '''
    def __init__(self):
        super().__init__()

    def render(self, model):
        result = tabulate([[i, v.wealth] for i, v in enumerate(model.schedule.agents)])
        return result

score_table = ScoreTable()
wealth_table = WealthTable()

server = ModularServer(MoneyModel,
                       [grid, chart, price_chart, participation_chart, wealth_chart,
                        max_score_chart, fluctuation_chart,
                        producer_pie_chart, strategy_pie_chart, speculator_pie_chart,
                        ],
                       "Minority game with producers and speculators",
                       model_params)
server.port = 8521
server.launch()
