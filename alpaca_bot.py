from distutils.util import execute
from tracemalloc import start
from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit
from alpaca_trade_api.stream import Stream
import pandas_ta as ta
import math
import operator
import pandas as pd

APCA_API_KEY_ID = "ENTER YOUR API KEY HERE"
APCA_API_SECRET_KEY = "ENTER YOUR SECRET KEY HERE"
APCA_API_BASE_URL = "https://paper-api.alpaca.markets"

api = REST(key_id=APCA_API_KEY_ID, secret_key=APCA_API_SECRET_KEY, base_url=APCA_API_BASE_URL)

# supported metrics in strategy
# SMA 10,50, BBANDS, RSI, MACD (12,26)

CustomStrategy = ta.Strategy(
    name="TA Metrics",
    description="SMA 10,50 BBANDS, RSI, and MACD",
    ta=[
        {"kind": "sma", "length": 10},
        {"kind": "sma", "length": 50},
        {"kind": "bbands", "length": 20},
        {"kind": "rsi"},
        {"kind": "macd", "fast": 12, "slow": 26},
    ]
)

# can use "col_names": in TA objects to set a custom name for columns
# i.e. {"kind": "macd", "fast": 12, "slow": 26, "col_names": ("MACD", "MACD_H", "MACD_S")}

chart_df = pd.DataFrame(columns=['close', 'high', 'low', 'open', 'symbol', 'timestamp', 'trade_count', 'volume', 'vwap'])
open_position = False
open_quantity = 0

async def process_bars(b):
    global chart_df

    one_minute_bar = {
        'close': b.close,
        'high': b.high,
        'low': b.low,
        'open': b.open,
        'symbol': b.symbol,
        'timestamp': b.timestamp,
        'trade_count': b.trade_count,
        'volume': b.volume,
        'vwap': b.vwap,
    }

    bar_df = pd.DataFrame([one_minute_bar])
    chart_df = pd.concat([chart_df, bar_df])

    # Trade Execution Parameters
    # sym - ticker
    # tradable balance - amount that bot will risk per trade
    # buy - needs to be a function of metric a, b, and operator [sma, lt, cur_price] *using operator module for gt, lt operators etc.
    # sell - needs to be function of metric a, b, and operator [sma, gt, cur_price] *using operator module for gt, lt operators etc.
    execute_trade("RIOT", 50000, ["MACD_12_26_9", operator.gt, "MACDs_12_26_9"], ["MACD_12_26_9", operator.lt, "MACDs_12_26_9"])

def execute_trade(symb, starting_balance=0, buy=[], sell=[]):
    global chart_df, open_position, open_quantity

    indicator_df = chart_df.copy()
    indicator_df.ta.strategy(CustomStrategy)

    if indicator_df.empty or buy[2] not in indicator_df.columns:
        pass

    elif (pd.isnull(indicator_df.iloc[indicator_df.shape[0]-1][buy[0]]) or pd.isnull(indicator_df.iloc[indicator_df.shape[0]-1][buy[2]])):
        pass

    else:
        if buy[1](indicator_df.iloc[indicator_df.shape[0]-1][buy[0]], indicator_df.iloc[indicator_df.shape[0]-1][buy[2]]) and open_position == False:
            price = indicator_df.iloc[indicator_df.shape[0]-1]['close']
            api.submit_order(
                symbol=symb,
                qty=math.floor((starting_balance-1000)/price),
                side='buy',
                type='market',
                time_in_force='day',
            )
            open_quantity = math.floor((starting_balance-1000)/price)
            open_position = True


        elif sell[1](indicator_df.iloc[indicator_df.shape[0]-1][sell[0]], indicator_df.iloc[indicator_df.shape[0]-1][sell[2]]) and open_position == True:
            # closes position at market, could also use a qty parameter here
            # returns an order object # https://alpaca.markets/docs/api-references/trading-api/orders/

            api.close_position(symbol=symb)
            price = indicator_df.iloc[indicator_df.shape[0]-1]['close']
            open_position = False
            open_quantity = 0
            

def run_bot(symb):
    print("Running Bot...")
    # Initiate Class Instance
    stream = Stream(APCA_API_KEY_ID,
                    APCA_API_SECRET_KEY,
                    base_url="https://paper-api.alpaca.markets",
                    data_feed='iex')  # <- replace to SIP if you have PRO subscription


    # subscribing to event
    stream.subscribe_bars(process_bars, symb)

    stream.run()


# this is required for multiprocessing on windows
if __name__ == '__main__':
    run_bot("RIOT")
    
