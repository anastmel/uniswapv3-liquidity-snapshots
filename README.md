# uniswapv3-liquidity-snapshots
### A python module, by Kaiko
The `research_module.py` module provides functions for easily retrieving, charting, and aggregating Uniswap V3 liquidity pool data provided by Kaiko.

## Installation 
The module containing all the functions is named `research_module.py`. To use its functions, place it in your working directory and import it into your scripts.
```python
import research_module as kk
```

## Example
A sample script is included in this repository and named `example.py`. It demonstrates how to use each function within the `research_module.py` module.

### Example 1: Retrieving Liquidity Distribution Data for the APE-WETH 0.3% Liquidity Pool on Uniswap V3
```python
import research_module as kk

# Step 1 : Select parameters 
my_api_key = 'paste_your_api_key_here' # To get an API Key, contact kaiko.com
pool_address='0xac4b3dacb91461209ae9d41ec517c2b9cb1b7daf' # all characters should be in lower case
price_range = 0.2 # 0.2 stands for +/-20% with respect to the block's current price
start_time = '2023-01-03T14:00:00.000Z' 
end_time = '2023-02-03T23:00:00.000Z'

# Step 2 : Get the data
snapshots_data = kk.get_usp3_liquidity(api_key = my_api_key,
                                        pool_address=pool_address,
                                        start_time = start_time,
                                        end_time = end_time,
                                        price_range = price_range)
```

## Documentation 
Original API data documentation can be found at https://docs.kaiko.com/#uniswap-v3-liquidity-snapshots. Contact Kaiko to request a trial or to purchase this data.
