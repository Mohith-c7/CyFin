"""
Trading Bot Runner - Connects market stream to trading algorithm
"""

import sys
sys.path.append('..')

from data_stream.data_loader import load_market_data
from data_stream.replay_engine import stream_market_data
from trading_bot.trading_algorithm import TradingAlgorithm


class TradingBotRunner:
    """Orchestrates market data consumption and trading execution."""
    
    def __init__(self, symbol="AAPL", period="1d", interval="1m", 
                 delay=0.5, window_size=5, initial_balance=10000):
        """
        Initialize trading bot runner.
        
        Args:
            symbol: Stock ticker
            period: Historical data period
            interval: Data resolution
            delay: Seconds between ticks
            window_size: SMA window size
            initial_balance: Starting cash
        """
        self.symbol = symbol
        self.period = period
        self.interval = interval
        self.delay = delay
        self.trading_algo = TradingAlgorithm(window_size, initial_balance)
        
    def run(self):
        """Start the trading bot with live market stream."""
        print("=" * 70)
        print("TRADING BOT - STEP 2")
        print("=" * 70)
        print(f"Symbol: {self.symbol}")
        print(f"Initial Balance: ${self.trading_algo.balance}")
        print(f"SMA Window: {self.trading_algo.window_size}")
        print("-" * 70)
        
        try:
            # Load market data
            data = load_market_data(self.symbol, self.period, self.interval)
            
            # Process each tick
            tick_count = 0
            for tick in stream_market_data(data, self.symbol, self.delay):
                tick_count += 1
                
                # Process tick through trading algorithm
                decision = self.trading_algo.process_tick(tick)
                
                # Display trading decision
                self._display_decision(decision, tick_count)
            
            # Show final summary
            self._display_summary()
            
        except KeyboardInterrupt:
            print("\n\nTrading interrupted by user")
            self._display_summary()
        except Exception as e:
            print(f"\nError: {e}")
            raise
    
    def _display_decision(self, decision, tick_count):
        """Display trading decision in formatted way."""
        action = decision["action"]
        
        # Color coding for actions (using simple text markers)
        if action == "BUY":
            marker = "🟢 BUY "
        elif action == "SELL":
            marker = "🔴 SELL"
        elif action == "WAIT":
            marker = "⏳ WAIT"
        else:
            marker = "⚪ HOLD"
        
        print(f"\nTick #{tick_count}")
        print(f"  {marker} | Price: ${decision['price']:.2f} | SMA: {decision['sma']}")
        print(f"  Reason: {decision['reason']}")
        print(f"  Balance: ${decision['balance']} | Position: {decision['position']} shares")
        print(f"  Portfolio Value: ${decision['portfolio_value']}")
    
    def _display_summary(self):
        """Display final trading performance summary."""
        summary = self.trading_algo.get_performance_summary()
        
        print("\n" + "=" * 70)
        print("TRADING PERFORMANCE SUMMARY")
        print("=" * 70)
        print(f"Total Trades: {summary['total_trades']}")
        print(f"Final Balance: ${summary['final_balance']}")
        print(f"Final Position: {summary['position']} shares")
        
        if summary['trades']:
            print("\nTrade History:")
            for i, trade in enumerate(summary['trades'], 1):
                print(f"  {i}. {trade['action']} {trade['shares']} shares @ ${trade['price']:.2f}")
        
        print("=" * 70)


if __name__ == "__main__":
    bot = TradingBotRunner(
        symbol="AAPL",
        period="1d",
        interval="1m",
        delay=0.5,
        window_size=5,
        initial_balance=10000
    )
    bot.run()
