# Technical Analysis Backtesting Module

The Technical Analysis Backtesting App is a Python-based tool designed to help you backtest and evaluate the performance of trading strategies using various technical indicators. This tool supports several technical indicators, such as Bollinger Bands (BB), Exponential Moving Averages (EMA), Moving Average Convergence Divergence (MACD), Relative Strength Index (RSI), Simple Moving Averages (SMA), and Stochastic Oscillator (SO). In the future I will be adding multiple custom strategies, along with price action based backtesting.

## Usage

To use this tool, you need to import the relevant backtester classes for the specific technical indicators you want to test. Here's how you can set up and utilize the app:

1. Import the technical indicators you wish to test:

```python
import BBBacktester
import EMABacktester
import MACDBacktester
import RSIBacktester
import SMABacktester
import SOBacktester
```

2. Create an instance of the `Backtester` class, providing essential parameters:

```python
backtester = Backtester(symbol, strategy, start_date, end_date, granularity, **options)
```

- `symbol`: The ticker symbol to work with.
- `strategy`: The name of the trading strategy (e.g., "BB," "EMA," "MACD," "RSI," "SMA," or "SO").
- `start_date`: The start date for data retrieval.
- `end_date`: The end date for data retrieval.
- `granularity`: The time window for data sampling.
- `options`: A dictionary of strategy-specific options, which vary depending on the chosen strategy.

3. Set up the strategy:

```python
backtester.strategy_setup(strategy)
```

This step configures the specific strategy you selected and fetches the necessary data.

4. Retrieve strategy results:

```python
results = backtester.strategy_results(strategy)
```

This function runs the backtesting process for the selected strategy and returns the results.

5. To optimize strategy parameters, use the `optimize_parameters` function, passing a strategy and keyword arguments for parameter ranges:

```python
optimized_params = backtester.optimize_parameters(strategy, **kwargs)
```

This function performs brute-force optimization of strategy parameters within specified ranges.

6. Visualize the strategy's performance:

```python
backtester.plot_results()
```

This function plots the cumulative returns of your strategy compared to a simple buy and hold approach.

## Supported Strategies

The app supports the following trading strategies, each implemented in its respective Backtester class:

- Bollinger Bands (BB)
- Exponential Moving Averages (EMA)
- Moving Average Convergence Divergence (MACD)
- Relative Strength Index (RSI)
- Simple Moving Averages (SMA)
- Stochastic Oscillator (SO)
- Fibonacci (coming soon)
- Price Action (coming soon)
- Custom (coming soon)

## Customization

You can customize each trading strategy by adjusting the strategy-specific options in the `options` dictionary when creating a `Backtester` instance. These options may include parameters like period lengths, thresholds, and transaction costs.

## Example

Here's a sample usage of the app to test the Bollinger Bands (BB) strategy:

```python
import BBBacktester

# Create a Backtester instance
backtester = Backtester("AAPL", "BB", "2023-01-01", "2023-12-31", "D", SMA=20, DEV=2.0)

# Set up the strategy
backtester.strategy_setup("BB")

# Retrieve strategy results
results = backtester.strategy_results("BB")

# Optimize strategy parameters
optimized_params = backtester.optimize_parameters("BB", SMA_RANGE=(10, 30, 5), DEV_RANGE=(1, 3, 1))

# Visualize strategy performance
backtester.plot_results()
```

## Disclaimer

This app is intended for educational and research purposes. It is important to note that past performance does not guarantee future results, and trading involves risks.

## License

This Technical Indicator Backtesting App is available under the [MIT License](LICENSE).

Feel free to explore and use this app to evaluate your trading strategies and adapt it to your specific needs.

Happy backtesting! 📈🤖📉

---

For further details and examples, refer to the code and comments in the Python script containing the `Backtester` class and the relevant strategy-specific backtester classes.
