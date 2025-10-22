import pypsa 
import pandas as pd
from pypsa.common import annuity

REGIONS = ["VIC"]
#As implemented, must match Bus names and df columns

def create_network():
    network = pypsa.Network(name="four-node-nem")

    #Add nodes
    #network.add("Bus", name="NSW", x=151.20, y=-33.87)
    #network.add("Bus", name="QLD", x=153.03, y=-27.47)
    #network.add("Bus", name="SA", x=138.63, y=-34.93)
    network.add("Bus", name="VIC", x=145.01, y=-37.81)
    return network

def load_data():
    return pd.read_csv("demand.csv", index_col=0, parse_dates=True)

def solar_data():
    return pd.read_csv("solar.csv", index_col=0, parse_dates=True)

def wind_data():
    return pd.read_csv("wind.csv", index_col=0, parse_dates=True)

def add_snapshots_and_loads(network):

    df_load = pd.read_csv("node-demand.csv", index_col=0, parse_dates=True)

    network.set_snapshots(df_load.index)

    network.add("Load", 
            REGIONS,
            suffix="_load", 
            bus=REGIONS, 
            p_set=df_load[REGIONS], 
            carrier="load")

def add_vre(network, df, tech, capex, marginal):
    network.add(
        "Generator",
        REGIONS,
        suffix=f"_{tech}",
        bus=REGIONS,
        p_max_pu=df[REGIONS],
        p_nom_extendable=True,
        capital_cost=annuity(0.05, 30) * capex,
        carrier=tech)
    
def add_generators(network):
    df_wind = wind_data()
    add_vre(network, df_wind, "wind", capex=2_000_000)

    df_solar = solar_data()
    add_vre(network, df_solar, "solar", capex=700_000)

    

    