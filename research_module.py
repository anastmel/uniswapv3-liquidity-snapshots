# by: Anastasia Melachrinos
# date: Feb 2023

import requests
import pandas as pd
from datetime import datetime
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

########################################################################################
#GET UNISWAP V3 LIQUIDITY SNAPSHOTS DATA 
#Documentation available here https://docs.kaiko.com/#uniswap-v3-liquidity-snapshots 
#For API KEY contact Kaiko.com 
########################################################################################

def get_usp3_liquidity(api_key, pool_address, start_time, end_time, price_range):
    headers_dict = {'Accept': 'application/json',
                    'X-Api-Key':api_key}
    url = 'https://eu.market-api.kaiko.io/v2/data/liquidity.v1/snapshots/usp3'
    params_dict = {
                    'start_time':start_time,
                    'end_time':end_time,
                    'price_range':price_range,
                    'pool_address':pool_address, 
                    'page_size':100
                }
    # Make the initial API request
    res = requests.get(url, headers=headers_dict, params=params_dict).json()
    # Create a dataframe from the initial API response
    df = pd.DataFrame(res['data'])
    # Use a while loop to iterate through subsequent pages of the API response
    while 'next_url' in res.keys():
        res = requests.get(res['next_url'], headers=headers_dict).json()
        df = pd.concat([df, pd.DataFrame(res['data'])], ignore_index=True)
    # Convert the timestamp in the 'datetime' column to a datetime object and add it to a new 'date' column
    df['date'] = df['datetime'].apply(lambda x: datetime.fromtimestamp(x))
    #Explode the snapshots column and normalize the json data
    df = df.explode('snapshots')
    df = df.reset_index()
    df = df.drop("index", axis='columns')
    snaps = pd.json_normalize(df['snapshots'])
    final_df = pd.merge(df, snaps, left_index=True, right_index=True)
    final_df = final_df.drop("snapshots", axis='columns')
    return final_df

########################################################################################
# Chart Uniswap V3 Liquidity Distribution over time 
# GIF creation
########################################################################################

def generate_gif(pool_address, df):
    def get_ref_data(pool: str):
        url = 'https://reference-data-api.kaiko.io/v1/pools'
        params_dict = {'address': pool}
        resp = requests.get(url, params=params_dict)
        json_data = resp.json()
        df = pd.DataFrame(json_data['data'])
        return df
    
    reference = get_ref_data(pool_address)
    
    def get_decimals(reference):
        # Flatten the data in the 'tokens' column
        flattened_ref = pd.json_normalize(reference['tokens'])
        # Concatenate the original dataframe with the flattened data
        flattened_df = flattened_ref.rename(columns={0: 'column1', 1: 'column2'})
        my_ref_data = pd.concat([reference, flattened_df], axis=1)
        # flattening column1
        token1_metadata = pd.json_normalize(my_ref_data['column1'])
        decimals1 = token1_metadata.iloc[0]['decimals']
        token2_metadata = pd.json_normalize(my_ref_data['column2'])
        decimals2 = token2_metadata.iloc[0]['decimals']
    
        decimals1 = int(decimals1)
        decimals2 = int(decimals2)
        return decimals1,decimals2
    
    decimals1,decimals2 = get_decimals(reference)
    
    interval = 50
    
    TICK_BASE = 1.0001
    DECIMALS = decimals1-decimals2
    
    def tick_to_price(tick):
        return (TICK_BASE**tick) * (10**DECIMALS)
    
    df['lower_price'] = df['lower_tick'].apply(tick_to_price)
    
    blocks = df.block_number.unique()
    
    last_data = []
    for i, block in enumerate(blocks):
        data = df.loc[df.block_number == block].amount.values
        if (len(data) == len(last_data)):
            if (data == last_data).all():
                df = df[df.block_number != block]
        last_data = data
    
    df.reset_index(inplace=True, drop=True)
    blocks = df.block_number.unique()
    
    figure = plt.figure(figsize=(10, 8))
    ax = plt.gca()
    plt.grid(True)
    # plt.gcf().subplots_adjust(bottom=0.2)
    
    with Image.open(r'Kaiko_logo.jpg') as im:
        width, height = im.size
        mult=2
        new_width = int(width/mult)
        new_height = int(height/mult)
        im = im.resize((new_width, new_height))
        figure.figimage(im, 504, 280, alpha=.35)
    
    line, = ax.plot([df.lower_price.min(), df.lower_price.max()], [0, df.amount.max()], lw=2)
    ax.set_title("Evolution of the usp3 liquidity", fontsize = 15, fontname = 'Arial', fontweight='light')
    price_line = ax.axvline(df.lower_price.min(), color='red')
    
    def animate(i):
        block = df.block_number.sort_values().unique()[i]
        ax.set_title(f"Evolution of the usp3 liquidity at block {block}", fontsize = 15, fontname = 'Arial', fontweight='light')
        line.set_data(df[df.block_number == block].lower_price, df[df.block_number == block].amount)
        cur_price = df[df.block_number == block].current_price.max()
        price_line.set_data([cur_price, cur_price], [0, 1])
        return line
    
    plt.xlabel('Price', fontsize = 14, fontname = 'Arial', fontweight='light')
    plt.ylabel('Liquidity', fontsize = 14, fontname = 'Arial', fontweight='light')
    plt.show()
    ani = FuncAnimation(figure, func = animate, frames = range(len(blocks)), interval = interval, repeat = False)
    
    ani.save(pool_address + '.gif', dpi=80, writer='imagemagick', fps=60)

########################################################################################
# Get TVL data within the selected Price Range
########################################################################################

def get_tvl(df):
    # grouping and aggregating the data
    df2 = df.groupby(['block_number', 'date', 'current_price']).agg({'amount0': 'sum', 'amount1': 'sum'})
    # resetting the index
    df2 = df2.reset_index()
    return df2
 
########################################################################################
# Get TVL data of each token in the pool, over time
########################################################################################
def plot_tvl(df):
    # plot the first y-axis (amount0_c and amount1)
    fig, ax1 = plt.subplots()
    ax1.plot(df['date'], df['amount0'], 'darkblue', label='amount0')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Amount0')
    ax1.tick_params(axis='y')

    # rotate x-axis labels
    plt.xticks(rotation=60)
    
    # plot the secondary y-axis (current_price)
    ax2 = ax1.twinx()
    ax2.plot(df['date'], df['amount1'], 'orange', label='amount1')
    ax2.set_ylabel('Amount1')
    ax2.tick_params(axis='y')

    # Create a single legend for the entire figure
    fig.legend(labels=['amount0', 'amount1'])

    # Add a title to the chart
    plt.title('Amount of token0 and 1 over time')
    # show the plot
    plt.show()
