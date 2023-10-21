import BBBacktester
import EMABacktester
import MACDBacktester
import RSIBacktester
import SMABacktester
import SOBacktester

class Backtester:
    ''' Class for the vectorized backtesting of trading strategies.

    Attributes
    ==========
    symbol: str
        ticker symbol with which to work with
    strategy: str
        name of the strategy
    start: str
        start date for data retrieval
    end: str
        end date for data retrieval
    granularity: str
        time window for data sampling
    options: dict
        dictionary of strategy-specific options (listed below)

    
    Methods
    =======
    strategy_setup:
        sets up the strategy

    strategy_results:
        returns the results for the strategy

    optimize_parameters:
        implements a brute force optimization for the strategy
        
    plot_results:
        plots the performance of the strategy compared to buy and hold
    '''

    
    def __init__(self, symbol, strategy, start, end, granularity, **kwargs):
        self.symbol = symbol
        self.strategy = strategy
        self.start = start
        self.end = end
        self.granularity = granularity
        self.results = None 
        self.data = None
        self.options = {
            "DEV": kwargs.get("DEV", None),
            "EMA_S": kwargs.get("EMA_S", None),
            "EMA_L": kwargs.get("EMA_L", None),
            "MACD_signal": kwargs.get("MACD_signal", None),
            "RSI_periods": kwargs.get("RSI_periods", None),
            "RSI_upper": kwargs.get("RSI_upper", None),
            "RSI_lower": kwargs.get("RSI_lower", None),
            "SMA": kwargs.get("SMA", None),
            "SMA_S": kwargs.get("SMA_S", None),
            "SMA_L": kwargs.get("SMA_L", None),
            "SO_periods": kwargs.get("SO_periods", None),
            "SO_D_mw": kwargs.get("SO_D_mw", None),
            "TC": kwargs.get("TC", 0.0),
            "SMA_RANGE": kwargs.get("SMA_RANGE", None),
            "DEV_RANGE": kwargs.get("DEV_RANGE", None),
            "EMA_1_RANGE": kwargs.get("EMA_S_RANGE", None),
            "EMA_2_RANGE": kwargs.get("EMA_L_RANGE", None),
            "EMA_S_RANGE": kwargs.get("EMA_S_RANGE", None),
            "EMA_L_RANGE": kwargs.get("EMA_L_RANGE", None),
            "SIGNAL_MW_RANGE": kwargs.get("MACD_SIGNAL_RANGE", None),
            "RSI_PERIODS_RANGE": kwargs.get("RSI_PERIODS_RANGE", None),
            "RSI_UPPER_RANGE": kwargs.get("RSI_UPPER_RANGE", None),
            "RSI_LOWER_RANGE": kwargs.get("RSI_LOWER_RANGE", None),
            "SMA_1_RANGE": kwargs.get("SMA_S_RANGE", None),
            "SMA_2_RANGE": kwargs.get("SMA_L_RANGE", None),



            }
        self.strategy_setup(strategy)
    
        
    def __repr__(self):
        return "SMABacktester(symbol = {}, strategy = {}, start = {}, end = {})".format(self.symbol, self.strategy, self.start, self.end)
    
    def strategy_setup(self, strategy):
        switch = {
            "BB": lambda: BBBacktester.BBBacktester(self.symbol, self.options["SMA"], self.options["DEV"], self.start, self.end, self.granularity, self.options["TC"]),
            "EMA": lambda: EMABacktester.EMABacktester(self.symbol, self.options["EMA_S"], self.options["EMA_L"], self.start, self.end, self.granularity, self.options["TC"]),  
            "MACD": lambda: MACDBacktester.MACDBacktester(self.symbol, self.options["EMA_S"], self.options["EMA_L"], self.options["MACD_signal"], self.start, self.end, self.granularity, self.options["TC"]),
            "RSI": lambda: RSIBacktester.RSIBacktester(self.symbol, self.options["RSI_periods"], self.options["RSI_upper"], self.options["RSI_lower"], self.start, self.end, self.granularity, self.options["TC"]),
            "SMA": lambda: SMABacktester.SMABacktester(self.symbol, self.options["SMA_S"], self.options["SMA_L"], self.start, self.end, self.granularity, self.options["TC"]),
            "SO": lambda: SOBacktester.SOBacktester(self.symbol, self.options["SO_periods"], self.options["SO_D_mw"], self.start, self.end, self.granularity, self.options["TC"]),
        }
        self.data = switch[strategy]().data
    
    def strategy_results(self, strategy):
        switch = {
            "BB": lambda: BBBacktester.BBBacktester(self.symbol, self.options["SMA"], self.options["DEV"], self.start, self.end, self.granularity, self.options["TC"]).test_strategy(),
            "EMA": lambda: EMABacktester.EMABacktester(self.symbol, self.options["EMA_S"], self.options["EMA_L"], self.start, self.end, self.granularity, self.options["TC"]).test_strategy(),
            "MACD": lambda: MACDBacktester.MACDBacktester(self.symbol, self.options["EMA_S"], self.options["EMA_L"], self.options["MACD_signal"], self.start, self.end, self.granularity, self.options["TC"]).test_strategy(),
            "RSI": lambda: RSIBacktester.RSIBacktester(self.symbol, self.options["RSI_periods"], self.options["RSI_upper"], self.options["RSI_lower"], self.start, self.end, self.granularity, self.options["TC"]).test_strategy(),
            "SMA": lambda: SMABacktester.SMABacktester(self.symbol, self.options["SMA_S"], self.options["SMA_L"], self.start, self.end, self.granularity, self.options["TC"]).test_strategy(),
            "SO": lambda: SOBacktester.SOBacktester(self.symbol, self.options["SO_periods"], self.options["SO_D_mw"], self.start, self.end, self.granularity, self.options["TC"]).test_strategy(),
        }
        self.results = switch[strategy]()[-1]
        return self.results
    
    
    def optimize_parameters(self, strategy, **kwargs):
        switch = {
            "BB": lambda: BBBacktester.BBBacktester(self.symbol, self.options["SMA"], self.options["DEV"], self.start, self.end, self.granularity, self.options["TC"]).optimize_parameters(kwargs.get("SMA_RANGE", None), kwargs.get("DEV_RANGE", None)),
            "EMA": lambda: EMABacktester.EMABacktester(self.symbol, self.options["EMA_S"], self.options["EMA_L"], self.start, self.end, self.granularity, self.options["TC"]).optimize_parameters(kwargs.get("EMA_1_RANGE", None), kwargs.get("EMA_2_RANGE", None)),
            "MACD": lambda: MACDBacktester.MACDBacktester(self.symbol, self.options["EMA_S"], self.options["EMA_L"], self.options["MACD_signal"], self.start, self.end, self.granularity, self.options["TC"]).optimize_parameters(kwargs.get("EMA_S_RANGE", None), kwargs.get("EMA_L_RANGE", None), kwargs.get("SIGNAL_MW_RANGE", None)),
            "RSI": lambda: RSIBacktester.RSIBacktester(self.symbol, self.options["RSI_periods"], self.options["RSI_upper"], self.options["RSI_lower"], self.start, self.end, self.granularity, self.options["TC"]).optimize_parameters(kwargs.get("RSI_PERIODS_RANGE", None), kwargs.get("RSI_UPPER_RANGE", None), kwargs.get("RSI_LOWER_RANGE", None)),
            "SMA": lambda: SMABacktester.SMABacktester(self.symbol, self.options["SMA_S"], self.options["SMA_L"], self.start, self.end, self.granularity, self.options["TC"]).optimize_parameters(kwargs.get("SMA_1_RANGE", None), kwargs.get("SMA_2_RANGE", None)),
            "SO": lambda: SOBacktester.SOBacktester(self.symbol, self.options["SO_periods"], self.options["SO_D_mw"], self.start, self.end, self.granularity, self.options["TC"]).optimize_parameters(kwargs.get("SO_PERIODS_RANGE", None), kwargs.get("SO_D_MW_RANGE", None)),
        }
        return switch[strategy]()
    
    def plot_results(self):
        if self.results is None:
            print("No strategy results to plot yet. Run a strategy first.")
        else:
            title = "{} | {} | {} | {} | {}".format(self.symbol, self.strategy, self.start, self.end, self.granularity)
            self.results[["creturns","cstrategy"]].plot(title = title, figsize = (12, 8))

 