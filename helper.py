import pypsa 
import pandas as pd
from pypsa.common import annuity

REGIONS = ["VIC"]#, "SA", "NSW", "QLD"]
#As implemented, must match Bus names and df columns

CARRIERS = {
    "solar": "#F8E71C", #"gold",
    "wind": "#417505", #"green",
    "gas": "#F48E1B", #"orange"
    }
    #"brown_coal": "#8B572A", #brown
    #"black_coal": "black",
    #"load": "slategrey",
    #"AC": "violet"
    #}

EXISTING_COAL = {"NSW": {"tech":"black", "capacity":4000, "marginal": 50},
                 "QLD": {"tech":"black", "capacity":5000, "marginal": 50},
                 "VIC": {"tech":"brown", "capacity":3000, "marginal": 20}}

def create_network():
    network = pypsa.Network(name="four-node-nem")

    #Add nodes
    #network.add("Bus", name="NSW", x=151.20, y=-33.87)
    #network.add("Bus", name="QLD", x=153.03, y=-27.47)
    #network.add("Bus", name="SA", x=138.63, y=-34.93)
    network.add("Bus", name="VIC", x=145.01, y=-37.81)
    return network



def add_carriers(network):
    network.add("Carrier",
        CARRIERS.keys(),
        color=CARRIERS.values(),
)

def load_data():
    return pd.read_csv("demand.csv", index_col=0, parse_dates=True)

def solar_data():
    return pd.read_csv("solar.csv", index_col=0, parse_dates=True)

def wind_data():
    return pd.read_csv("wind.csv", index_col=0, parse_dates=True)

def add_snapshots_and_loads(network):

    df_load = load_data()

    network.set_snapshots(df_load.index)

    network.add("Load", 
            REGIONS,
            suffix="_load", 
            bus=REGIONS, 
            p_set=df_load[REGIONS], 
            carrier="load")

def add_vre(network, df, tech, capex):
    network.add(
        "Generator",
        REGIONS,
        suffix=f"_{tech}",
        bus=REGIONS,
        p_max_pu=df[REGIONS],
        p_nom_extendable=True,
        capital_cost=annuity(0.05, 30) * capex,
        carrier=tech)
    
def add_coal(network, region, capacity, tech, marginal, r_up=0.1, r_down=.2):
    network.add(
        "Generator",
        region,
        suffix=f"_{tech}_coal",
        bus=region,
        p_nom = capacity,
        marginal_cost=marginal,
        ramp_limit_up=r_up,
        ramp_limit_down=r_down,
        carrier= f"{tech}_coal")

def add_gas(network, capex, marginal):
    ## Add extendable gas generation
    network.add(
        "Generator",
        REGIONS,
        suffix="_gas",
        bus=REGIONS,
        p_nom_extendable=True,
        marginal_cost=marginal,
        capital_cost=annuity(0.05, 30) * capex,
        carrier="gas")

def add_generators(network):
    #df_wind = wind_data()
    #add_vre(network, df_wind, "wind", capex=2_000_000)

    #df_solar = solar_data()
    #add_vre(network, df_solar, "solar", capex=700_000)

    add_gas(network, capex=2_500_000, marginal=120)

    #for region in REGIONS:
    #    if region != "SA":
    #        add_coal(network=network, region=region, **EXISTING_COAL[region])



    

    