"""
System Runner - Complete end-to-end demonstration
"""

import sys
sys.path.append('..')

from data_stream.data_loader import load_market_data
from data_stream.replay_engine import stream_market_data
from integrity_monitor.data_manipulator import DataManipulator
from integrated_system.protected_trading_bot import ProtectedTradingBot


class SystemRunner:
    """Runs the complete integrated system demonstration."""
    
    def __init__(self, symbol="AAPL", period="1d", interval="1m", delay=0.3,
                 inject_attacks=True, attack_probability=0.15, attack_type="spike"):
        """
        Initialize system runner.
        
        Args:
            symbol: Stock ticker
            period: Historical period
            interval: Data resolution
            delay: Seconds between ticks
            inject_attacks: Whether to inject attacks
            attack_probability: Attack probability
            attack_type: Type of attack
        """
        self.symbol = symbol
        self.period = period
        self.interval = interval
        self.delay = delay
        
        # Initialize protected trading bot
        self.bot = ProtectedTradingBot(
            window_size=5,
            initial_balance=10000,
            monitor_window=20,
            contamination=0.1,
            initial_trust=100.0,
            decay_rate=15.0,
            recovery_rate=3.0
        )
        
        # Initialize data manipulator if needed
        self.manipulator = None
        if inject_attacks:
            self.manipulator = DataManipulator(attack_probability, attack_type)
    
    def run(self):
        """Run the complete system."""
        self._print_header()
        
        try:
            # Load market data
            data = load_market_data(self.symbol, self.period, self.interval)
            
            tick_count = 0
            for tick in stream_market_data(data, self.symbol, self.delay):
                tick_count += 1
                
                # Potentially inject attack
                was_attacked = False
                if self.manipulator:
                    tick, was_attacked = self.manipulator.manipulate(tick)
                
                # Process through protected trading bot
                result = self.bot.process_tick(tick)
                
                # Display results
                self._display_tick(result, tick_count, was_attacked)
                
                # Critical alert
                if result["trust_level"] == "CRITICAL":
                    self._display_critical_alert()
            
            # Final summary
            self._display_summary()
            
        except KeyboardInterrupt:
            print("\n\nSystem interrupted by user")
            self._display_summary()
        except Exception as e:
            print(f"\nError: {e}")
            raise
    
    def _print_header(self):
        """Print system header."""
        print("=" * 90)
        print("NATIONAL MARKET DATA INTEGRITY MONITORING & PROTECTION SYSTEM")
        print("=" * 90)
        print(f"Symbol: {self.symbol}")
        print(f"Initial Balance: ${self.bot.trading_algo.balance}")
        print(f"Attack Mode: {'ENABLED' if self.manipulator else 'DISABLED'}")
        if self.manipulator:
            print(f"Attack Type: {self.manipulator.attack_type}")
            print(f"Attack Probability: {self.manipulator.attack_probability:.1%}")
        print("-" * 90)
    
    def _display_tick(self, result, tick_count, was_attacked):
        """Display tick results."""
        # Status indicators
        anomaly_icon = "🔴" if result["is_anomaly"] else "🟢"
        trust_icons = {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🟠", "CRITICAL": "🔴"}
        trust_icon = trust_icons.get(result["trust_level"], "⚪")
        
        # Action indicators
        action_icons = {
            "BUY": "🟢 BUY ",
            "SELL": "🔴 SELL",
            "BLOCKED": "🚫 BLOCKED",
            "HOLD": "⚪ HOLD",
            "WAIT": "⏳ WAIT"
        }
        action_icon = action_icons.get(result["final_action"], "⚪")
        
        attack_marker = " [⚠️ ATTACK INJECTED]" if was_attacked else ""
        
        print(f"\n{'='*90}")
        print(f"Tick #{tick_count}{attack_marker}")
        print(f"{'='*90}")
        print(f"Price: ${result['price']:.2f} | SMA: {result['sma']}")
        print(f"{anomaly_icon} Data Status: {'ANOMALY' if result['is_anomaly'] else 'NORMAL'}")
        print(f"{trust_icon} Trust: {result['trust_score']:.1f}/100 ({result['trust_level']}) | {result['recommendation']}")
        print(f"{action_icon} Trading: {result['final_action']}")
        
        if result["blocked"]:
            print(f"   ⚠️  Trade blocked due to low trust score!")
            print(f"   Intended: {result['intended_action']} → Blocked for safety")
        
        print(f"Balance: ${result['balance']:.2f} | Position: {result['position']} shares | Portfolio: ${result['portfolio_value']:.2f}")
    
    def _display_critical_alert(self):
        """Display critical trust alert."""
        print("\n" + "!" * 90)
        print("🚨 CRITICAL ALERT: TRUST SCORE CRITICALLY LOW - ALL TRADING HALTED")
        print("!" * 90)
    
    def _display_summary(self):
        """Display final system summary."""
        summary = self.bot.get_summary()
        
        print("\n" + "=" * 90)
        print("SYSTEM PERFORMANCE SUMMARY")
        print("=" * 90)
        
        print("\n📊 DATA INTEGRITY:")
        print(f"  Total Ticks Processed: {summary['total_ticks']}")
        print(f"  Anomalies Detected: {summary['total_anomalies']}")
        print(f"  Anomaly Rate: {summary['anomaly_rate']:.2f}%")
        print(f"  Final Trust Score: {summary['trust_score']:.2f}/100")
        
        print("\n💰 TRADING PERFORMANCE:")
        print(f"  Trades Executed: {summary['executed_trades']}")
        print(f"  Trades Blocked: {summary['blocked_trades']}")
        print(f"  Final Balance: ${summary['final_balance']:.2f}")
        print(f"  Final Position: {summary['final_position']} shares")
        
        if self.manipulator:
            attack_stats = self.manipulator.get_stats()
            print("\n⚠️  ATTACK STATISTICS:")
            print(f"  Attacks Injected: {attack_stats['attack_count']}")
            print(f"  Attack Type: {attack_stats['attack_type']}")
            
            if attack_stats['attack_count'] > 0:
                detection_rate = (summary['total_anomalies'] / attack_stats['attack_count']) * 100
                print(f"  Detection Rate: {detection_rate:.1f}%")
        
        if summary['trade_history']:
            print("\n📈 TRADE HISTORY:")
            for i, trade in enumerate(summary['trade_history'], 1):
                print(f"  {i}. {trade['action']} {trade['shares']} shares @ ${trade['price']:.2f}")
        
        print("\n" + "=" * 90)
        print("✓ System demonstration complete")
        print("=" * 90)


if __name__ == "__main__":
    runner = SystemRunner(
        symbol="AAPL",
        period="1d",
        interval="1m",
        delay=0.3,
        inject_attacks=True,
        attack_probability=0.15,
        attack_type="spike"
    )
    runner.run()
