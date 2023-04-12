import usp3_kaiko as kk

######################################################################################
# GET Uniswap V3 Liquidity Pool data over time 
# Using Kaiko Uniswap V3 Liquidity Snapshots Data
######################################################################################

# Step 1 : Select parameters 
my_api_key = 'paste_your_api_key_here' # To get an API Key, contact kaiko.com
pool_address='0xac4b3dacb91461209ae9d41ec517c2b9cb1b7daf' # all characters should be in lower case
price_range = 0.2 # 0.2 stands for +/-20% with respect to the block's current price
start_time = '2023-02-03T14:00:00.000Z' 
end_time = '2023-02-03T23:00:00.000Z'

# Step 2 : Get the data
snapshots_data = kk.get_usp3_liquidity(api_key = my_api_key,
                                        pool_address=pool_address,
                                        start_time = start_time,
                                        end_time = end_time,
                                        price_range = price_range)

snapshots_data.to_csv('univ3_snapshots.csv')

######################################################################################
# CHART Uniswap V3 Liquidity Distribution
# Generates a GIF that is saved in your working directory
######################################################################################
kk.generate_gif(pool_address=pool_address, df=snapshots_data)


######################################################################################
# Aggregate the liquidity snapshots data 
# and deduce the TVL within the selected range
######################################################################################
tvl = kk.get_tvl(snapshots_data)

tvl.to_csv('tvl_univ3.csv')


######################################################################################
# Plot the TVL within the selected price range
######################################################################################
kk.plot_tvl(tvl)
