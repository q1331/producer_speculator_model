from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule

from MoneyModel import *

gird_height = 50
gird_width = 50
canvas_height = 500
canvas_width = 500
chart_canvas_width = 500
chart_canvas_height = 200

model_params = {"Ns": UserSettableParameter("slider", "Number of speculators", value=1000, min_value=0, max_value=5000),
                "Np": UserSettableParameter("slider", "Number of producers", value=50, min_value=0, max_value=5000),
                "influx": UserSettableParameter("slider", "Periodic money influx to producers(η)", value=0.001, min_value=0, max_value=1,step=0.001),
                "fluctuation_factor": UserSettableParameter("slider", "Price fluctuation factor(α)", value=0.02, min_value=0.001,step=0.001, max_value=1),
                "amplitude": UserSettableParameter("slider", "Amplitude of producer investment(ε)", value=0.01, min_value=0.001,step=0.001, max_value=1),
                "producer_money": UserSettableParameter("slider", "Initial producer cash", value=1, min_value=1, max_value=100),
                "bias_factor": UserSettableParameter("slider", "Bias factor(λ)", value=0.01, min_value = 0.001, max_value=1,step=0.001, description="The parameter λ measures the strength of the bias caused by the intrinsic value of the commodity."),
                "memory_size": UserSettableParameter("slider", "Speculator memory size", value=2, min_value = 1, max_value=20, description="Length of the bit string."),
                "speculator_money": UserSettableParameter("slider", "Initial speculator money", value=1, min_value=1, max_value=100),
                "prudent_factor": UserSettableParameter("slider", "Speculator prudent factor(δ)", value=0.001, min_value=0.001, max_value=1, step=0.001),
                "width": gird_width,
                "height": gird_height}


def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "r": 0.1}
    if agent.participating:
        if isinstance(agent, Producer):
            portrayal["Color"] = "red"
        else:
            portrayal["Color"] = "blue"
        portrayal["Layer"] = 0
        portrayal["r"] = agent.wealth
    else:
        if isinstance(agent, Producer):
            portrayal["Color"] = "black"
        else:
            portrayal["Color"] = "grey"
        portrayal["Layer"] = 0
        portrayal["r"] = agent.wealth
    return portrayal


grid = CanvasGrid(agent_portrayal, grid_height=gird_height, grid_width=gird_width,
                  canvas_height=canvas_height, canvas_width=canvas_width)
chart = ChartModule([{"Label": "Average Agent Wealth",
                      "Color": "Black"}],
                    canvas_width=chart_canvas_width,
                    canvas_height=chart_canvas_height,
                    data_collector_name='datacollector')
price_chart = ChartModule([{"Label": "Price",
                            "Color": "black"}],
                          data_collector_name='datacollector')
offer_chart = ChartModule([{"Label": "Offer",
                            "Color": "green"}],
                          data_collector_name='datacollector')
demand_chart = ChartModule([{"Label": "Demand",
                             "Color": "red"}],
                           data_collector_name='datacollector')

participation_chart = ChartModule([{"Label": "Speculator Participation Rate",
                                    "Color": "red"}],
                                  data_collector_name='datacollector')
producer_participation_chart = ChartModule([{"Label": "Producer Participation Rate",
                                             "Color": "green"}],
                                           data_collector_name='datacollector')


server = ModularServer(MoneyModel,
                       [grid, chart, price_chart, offer_chart, demand_chart, participation_chart,
                        producer_participation_chart],
                       "Minority game with producers and speculators",
                       model_params)
server.port = 8521
server.launch()
