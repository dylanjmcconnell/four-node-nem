import pypsa 
import pandas as pd
from pypsa.common import annuity

#List of regions to model by default
REGIONS = ["VIC", "SA", "QLD", "NSW"]

REGION_DICT = {"NSW":  {"x":151.20, "y":-33.87},
               "QLD":  {"x":153.03, "y":-27.47},
               "SA":   {"x": 138.63, "y":-34.93},
               "VIC":   {"x": 145.01, "y":-37.81},
                }

CARRIERS = {
    "solar": "#F8E71C", #"gold",
    "wind": "#417505", #"green",
    "gas": "#F48E1B", #"orange"
    "brown_coal": "#8B572A", #brown
    "black_coal": "black",
    "load": "slategrey",
    "AC": "violet"
    }

#capacity and marginal cost for existing plants
EXISTING_COAL = {"NSW": {"tech":"black", "capacity":4000, "marginal": 60},
                 "QLD": {"tech":"black", "capacity":5000, "marginal": 60},
                 "VIC": {"tech":"brown", "capacity":3000, "marginal": 20}}

#capex for new capacity
NEW_CAPACITY = {"wind": 2_800_000,
                "solar":1_100_000,
                 "gas": 2_000_000 }

GAS_MARGINAL = 120

LINKS = {"VIC-SA": {"bus0": "VIC", "bus1": "SA", "p_nom":1000},
         "VIC-NSW": {"bus0": "VIC", "bus1": "NSW", "p_nom":2500},
         "NSW-QLD": {"bus0": "NSW", "bus1": "QLD", "p_nom":1500}}

def create_network():
    network = pypsa.Network(name="four-node-nem")

    for name in REGIONS:
        network.add("Bus", name=name, **REGION_DICT[name])

    add_carriers(network)
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
            p_set=df_load[REGIONS].clip(lower=0), 
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
    df_wind = wind_data()
    add_vre(network, df_wind, "wind", capex=NEW_CAPACITY["wind"])

    df_solar = solar_data()
    add_vre(network, df_solar, "solar", capex=NEW_CAPACITY["solar"])

    add_gas(network, capex=NEW_CAPACITY["gas"], marginal=GAS_MARGINAL)

    for region in REGIONS:
        if region != "SA":
            add_coal(network=network, region=region, **EXISTING_COAL[region])

def add_links(network):


    for name, attrs in LINKS.items():
        if attrs["bus0"] in REGIONS and attrs["bus1"] in REGIONS:
                network.add(
                        "Link",
                        name,
                        carrier="AC",
                        p_min_pu=-1,  #bidirectional 
                        **attrs
                    )
                
def build_full_problem():
    network = create_network()
    add_snapshots_and_loads(network)
    add_generators(network)
    add_links(network)
    return network