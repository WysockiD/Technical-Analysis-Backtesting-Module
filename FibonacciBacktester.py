import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from oandapyV20 import API
from dotenv import load_dotenv
import oandapyV20.endpoints.instruments as instruments

load_dotenv()
oanda_api_key = os.getenv('OANDA_API_KEY')

class FibonacciBacktester():
    def __init__(self, symbol, start, end, granularity):
        self.symbol = symbol
        self.start = start
        self.end = end
        self.granularity = granularity
        self.data = None

    def __repr__(self):
        return "FibonacciBacktester(symbol={}, start={}, end={}, granularity={})".format(self.symbol, self.start, self.end, self.granularity)

    def get_data(self):
        client = API(access_token=oanda_api_key)

        params = {
            "from": self.start,
            "to": self.end,
            "granularity": self.granularity,
        }

        request = instruments.InstrumentsCandles(instrument=self.symbol, params=params)
        client.request(request)
        response = request.response

        candles = response['candles']
        data_list = []

        for candle in candles:
            time = pd.to_datetime(candle['time'])
            close_price = float(candle['mid']['c'])

            data_list.append([time, close_price])

        columns = ['Date', 'Close']
        data = pd.DataFrame(data_list, columns=columns)
        data.set_index('Date', inplace=True)

        data["returns"] = np.log(data["Close"] / data["Close"].shift(1))
        self.data = data

    def find_local_highs_lows(self):
        if self.data is None:
            print("No data available for finding local highs and lows. Use get_data() to fetch data.")
            return

        data = self.data.copy()
        data["local_high"] = False
        data["local_low"] = False

        for i in range(1, len(data) - 1):
            if data["Close"][i] > data["Close"][i - 1] and data["Close"][i] > data["Close"][i + 1]:
                data.at[data.index[i], "local_high"] = True
            elif data["Close"][i] < data["Close"][i - 1] and data["Close"][i] < data["Close"][i + 1]:
                data.at[data.index[i], "local_low"] = True

        self.data = data

    def plot_results(self):
        if self.data is None:
            print("No data available for plotting. Use get_data() to fetch data.")
            return

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(self.data.index, self.data['Close'], label='Price')

        local_highs = self.data[self.data['local_high']]
        local_lows = self.data[self.data['local_low']]
        ax.scatter(local_highs.index, local_highs['Close'], marker='^', color='red', label='Local High')
        ax.scatter(local_lows.index, local_lows['Close'], marker='v', color='green', label='Local Low')

        ax.set_title(f"Local Highs and Lows for {self.symbol}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")

        ax.legend()

        # Manually calculate and plot Fibonacci retracement levels
        price_data = self.data['Close'].to_numpy()
        data_length = len(price_data)
        fib_levels = {}
        for level in [0.236, 0.382, 0.618]:
            index = int(data_length * level)
            fib_levels[level] = price_data.max() - (price_data.max() - price_data.min()) * level
            ax.axhline(fib_levels[level], color='blue', linestyle='--', label=f'Fib {level}')

        plt.show()


