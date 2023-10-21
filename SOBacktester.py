import os
import numpy as np
import pandas as pd
import seaborn as sns
from oandapyV20 import API
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from scipy.optimize import brute
import oandapyV20.endpoints.instruments as instruments

load_dotenv()
oanda_api_key = os.getenv('OANDA_API_KEY')

class SOBacktester(): 
    ''' Class for the vectorized backtesting of SO-based trading strategies.

    Attributes
    ==========
    symbol: str
        ticker symbol with which to work with
    periods: int
        time window in days for rolling low/high
    D_mw: int
        time window in days for %D line
    start: str
        start date for data retrieval
    end: str
        end date for data retrieval
    tc: float
        proportional transaction costs per trade
        
        
    Methods
    =======
    get_data:
        retrieves and prepares the data
        
    set_parameters:
        sets one or two new SO parameters
        
    test_strategy:
        runs the backtest for the SO-based strategy
        
    plot_results:
        plots the performance of the strategy compared to buy and hold
        
    update_and_run:
        updates SO parameters and returns the negative absolute performance (for minimization algorithm)
        
    optimize_parameters:
        implements a brute force optimization for the two SO parameters
    '''
    
    def __init__(self, symbol, periods, D_mw, start, end, granularity, tc):
        self.symbol = symbol
        self.periods = periods
        self.D_mw = D_mw
        self.start = start
        self.end = end
        self.granularity = granularity
        self.tc = tc
        self.results = None 
        self.get_data()
        
    def __repr__(self):
        return "SOBacktester(symbol = {}, periods = {}, D_mw = {}, start = {}, end = {})".format(self.symbol, self.periods, self.D_mw, self.start, self.end)
        
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

        data["returns"] = np.log(data.Close / data.Close.shift(1))
        data["roll_low"] = data.Low.rolling(self.periods).min()
        data["roll_high"] = data.High.rolling(self.periods).max()
        data["K"] = (data.Close - data.roll_low) / (data.roll_high - data.roll_low) * 100
        data["D"] = data.K.rolling(self.D_mw).mean()
        self.data = data
        
    def set_parameters(self, periods = None, D_mw = None):
        ''' Updates SO parameters and resp. time series.
        '''
        if periods is not None:
            self.periods = periods
            self.data["roll_low"] = self.data.Low.rolling(self.periods).min()
            self.data["roll_high"] = self.data.High.rolling(self.periods).max()
            self.data["K"] = (self.data.Close - self.data.roll_low) / (self.data.roll_high - self.data.roll_low) * 100
            self.data["D"] = self.data.K.rolling(self.D_mw).mean() 
        if D_mw is not None:
            self.D_mw = D_mw
            self.data["D"] = self.data.K.rolling(self.D_mw).mean()
            
    def test_strategy(self):
        ''' Backtests the trading strategy.
        '''
        data = self.data.copy().dropna()
        data["position"] = np.where(data["K"] > data["D"], 1, -1)
        data["strategy"] = data["position"].shift(1) * data["returns"]
        data.dropna(inplace=True)
        
        # determine when a trade takes place
        data["trades"] = data.position.diff().fillna(0).abs()
        
        # subtract transaction costs from return when trade takes place
        data.strategy = data.strategy - data.trades * self.tc
        
        data["creturns"] = data["returns"].cumsum().apply(np.exp)
        data["cstrategy"] = data["strategy"].cumsum().apply(np.exp)
        self.results = data
        
        perf = data["cstrategy"].iloc[-1] # absolute performance of the strategy
        outperf = perf - data["creturns"].iloc[-1] # out-/underperformance of strategy
        return [perf, outperf, self.results]
    
    def plot_results(self):
        ''' Plots the cumulative performance of the trading strategy
        compared to buy and hold.
        '''
        if self.results is None:
            print("No results to plot yet. Run a strategy.")
        else:
            title = "{} | periods = {}, D_mw = {} | TC = {}".format(self.symbol, self.periods, self.D_mw, self.tc)
            self.results[["creturns", "cstrategy"]].plot(title=title, figsize=(12, 8))
        
    def update_and_run(self, SO):
        ''' Updates SO parameters and returns the negative absolute performance (for minimization algorithm).

        Parameters
        ==========
        SO: tuple
            SO parameter tuple
        '''
        self.set_parameters(int(SO[0]), int(SO[1]))
        return -self.test_strategy()[0]
    
    def optimize_parameters(self, periods_range, D_mw_range):
        ''' Finds global maximum given the SO parameter ranges.

        Parameters
        ==========
        periods_range, D_mw_range: tuple
            tuples of the form (start, end, step size)
        '''
        opt = brute(self.update_and_run, (periods_range, D_mw_range), finish=None)
        return opt, -self.update_and_run(opt)
    
    