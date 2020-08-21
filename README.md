This is a prototype to demonstrate how to retrieve market data using Interactive Brokers' Python API.
# Environment Setup
## Install Python 3.6
```
conda create --name ibkr python=3.6
conda activate ibkr
```
## Install IBKR Python API
Download the API from http://interactivebrokers.github.io/downloads/twsapi_macunix.976.01.zip

Install the API:
```
cd IBJts/source/pythonclient/
python setup.py install
```
## Install other dependencies
```
conda install pandas prompt_toolkit
```
