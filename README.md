# Four-node NEM Capacity Expansion model

A simple, four node model of NEM to demonstrate the basic workflow of a capacity expansion modelling excercise, using PyPSA. 

This simplified model aims to introduce some of the basic concepts, and allow relatively quick exploration of the problem, by reducing the complexity.  In this case, we look at capacity expansion for (only) the year 2030, and consider only a handful of generators at each node (a mix of existing coal generators, and potential candidates for new capacity), and simplified interconnectors between the regions. 

## Installation and running the model

Recommended to install and run this project using [uv](https://docs.astral.sh/uv/getting-started/installation/). 

```
git clone  https://github.com/dylanjmcconnell/four-node-nem
uv sync
uv run jupter notebook
```