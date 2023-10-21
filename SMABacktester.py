import os
import numpy as np
import pandas as pd
import seaborn as sns
from oandapyV20 import API
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from scipy.optimize import brute
import oandapyV20.endpoints.instruments as instruments
import Backetester as bt

load_dotenv()
oanda_api_key = os.getenv('OANDA_API_KEY')

class SMABacktester:
    ''' Class for the vectorized backtesting of SMA-based trading strategies.
    
    Attributes
    ==========
    symbol: str
        ticker symbol with which to work with
    SMA_S: int
        time window in days for shorter SMA
    SMA_L: int
        time window in days for longer SMA  
    start: str
        start date for data retrieval
    end: str
        end date for data retrieval
    granularity: str
        time window for data sampling, e.g. 'D' for daily
    tc: float
        proportional transaction costs per trade

    Methods
    =======
    get_data:
        retrieves and prepares the data
    
    set_parameters:
        sets one or two new SMA parameters

    test_strategy:
        runs the backtest for the SMA-based strategy
    
    plot_results:
        plots the performance of the strategy compared to buy and hold

    update_and_run:
        updates SMA parameters and returns the negative absolute performance (for minimization algorithm)
    
    optimize_parameters:
        implements a brute force optimization for the two SMA parameters
    '''
   
    def __init__(self, symbol, SMA_S, SMA_L, start, end, granularity, tc=0.0):
        self.symbol = symbol
        self.SMA_S = SMA_S
        self.SMA_L = SMA_L
        self.start = start
        self.end = end
        self.granularity = granularity
        self.tc = tc
        self.results = None 
        self.data = None
        self.get_data()

        
    def __repr__(self):
        return "SMABacktester(symbol = {}, SMA_S = {}, SMA_L = {}, start = {}, end = {})".format(self.symbol, self.SMA_S, self.SMA_L, self.start, self.end)
        
    def get_data(self):
        ''' Retrieves and prepares the data from Oanda.
        '''

        client = API(access_token= oanda_api_key)

        # Define the request parameters
        params = {
            "from": self.start,
            "to": self.end,
            "granularity": self.granularity,  # Daily granularity, adjust as needed
        }
        
        # Fetch historical forex data from OANDA
        request = instruments.InstrumentsCandles(instrument=self.symbol, params=params)
        client.request(request)
        response = request.response

        # Isolate candlestick data from API response
        candles = response['candles']
        data_list = []

        for candle in candles:
            time = pd.to_datetime(candle['time'])
            open_price = float(candle['mid']['o'])
            high_price = float(candle['mid']['h'])
            low_price = float(candle['mid']['l'])
            close_price = float(candle['mid']['c'])
            volume = int(candle['volume'])

            data_list.append([time, open_price, high_price, low_price, close_price, volume])

        # Create a pandas DataFrame
        columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        data = pd.DataFrame(data_list, columns=columns)

        # Set the 'Date' column as the index
        data.set_index('Date', inplace=True)

        # Calculate returns, SMA_S, and SMA_L
        
        data["returns"] = np.log(data['Close'] / data['Close'].shift(1))
        data["SMA_S"] = data['Close'].rolling(self.SMA_S).mean()
        data["SMA_L"] = data['Close'].rolling(self.SMA_L).mean()

        self.data = data
        
        
        
        
    def set_parameters(self, SMA_S = None, SMA_L = None):
        ''' Updates SMA parameters and resp. time series.
        '''
        if SMA_S is not None:
            self.SMA_S = SMA_S
            self.data["SMA_S"] = self.data["Close"].rolling(self.SMA_S).mean()
        if SMA_L is not None:
            self.SMA_L = SMA_L
            self.data["SMA_L"] = self.data["Close"].rolling(self.SMA_L).mean()
            
    def test_strategy(self):
        ''' Backtests the trading strategy.
        '''
        data = self.data.copy().dropna()
        data["position"] = np.where(data["SMA_S"] > data["SMA_L"], 1, -1)
        data["strategy"] = data["position"].shift(1) * data["returns"]
        data.dropna(inplace=True)
        data["creturns"] = data["returns"].cumsum().apply(np.exp)
        data["cstrategy"] = data["strategy"].cumsum().apply(np.exp)
        self.results = data
        
        # absolute performance of the strategy
        perf = data["cstrategy"].iloc[-1]
        # out-/underperformance of strategy
        outperf = perf - data["creturns"].iloc[-1]

        return [perf, outperf, self.results]
    
    def plot_results(self):
        ''' Plots the cumulative performance of the trading strategy
        compared to buy and hold.
        '''
        if self.results is None:
            print("No results to plot yet. Run a strategy.")
        else:
            title = "{} | SMA_S = {} | SMA_L = {}".format(self.symbol, self.SMA_S, self.SMA_L)
            self.results[["creturns", "cstrategy"]].plot(title=title, figsize=(12, 8))
        
    def update_and_run(self, SMA):
        ''' Updates SMA parameters and returns the negative absolute performance (for minimization algorithm).

        Parameters
        ==========
        SMA: tuple
            SMA parameter tuple
        '''
        self.set_parameters(int(SMA[0]), int(SMA[1]))
        return -self.test_strategy()[0]
    
    def optimize_parameters(self, SMA1_range, SMA2_range):
        ''' Finds global maximum given the SMA parameter ranges.

        Parameters
        ==========
        SMA1_range, SMA2_range: tuple
            tuples of the form (start, end, step size)
        '''
        opt = brute(self.update_and_run, (SMA1_range, SMA2_range), finish=None)
        return opt, -self.update_and_run(opt)



if __name__ == "__main__":
    test = SMABacktester("USD_CAD", 50, 200, "2017-01-30", "2020-12-31", "D")
    test.test_strategy()
    test.plot_results()
