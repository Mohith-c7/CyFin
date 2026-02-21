# Step 2 - Trading Algorithm Simulator

## Objective

Build an automated trading decision engine that:
- ✅ Receives live market price ticks from Step 1
- ✅ Analyzes price movement
- ✅ Makes BUY / SELL / HOLD decisions
- ✅ Logs decisions
- ✅ Tracks virtual portfolio

## Why Step 2 is Critical

The hackathon story chain:
```
Market Data → Trading Algorithm → Wrong Decision → Loss
```

If trading system reacts to manipulated data → impact becomes visible.
Judges understand risk immediately.

## System Architecture

```
Market Data Stream (Step 1)
        ↓
Trading Strategy Engine
        ↓
Trade Decision Output
        ↓
Portfolio State Update
        ↓
Console Log
```

## File Structure

```
market_integrity_project/
├── trading/
│   ├── __init__.py
│   ├── strategy.py          # Trading decision logic
│   ├── portfolio.py         # Portfolio management
│   └── trading_engine.py    # Main controller
└── integration_test.py      # Step 1 + Step 2 integration
```

## Core Components

### Module A: Trading Strategy Logic
Pure decision-making rules.
- Input: current price
- Output: BUY / SELL / HOLD

### Module B: Portfolio Manager
Tracks:
- Cash balance
- Number of shares held
- Trade history

Simulates financial impact.

### Module C: Trading Engine
Connects stream → strategy → portfolio.
Acts as controller.

## Trading Strategy Design

**Percentage Change Strategy**

Decision Rules:
- If price increases > +2% → BUY
- If price decreases > -2% → SELL
- Else → HOLD

Why this works:
- Manipulated spike → large change → triggers trade → visible error
- Perfect for demo

## Implementation

### strategy.py

```python
class TradingStrategy:
    def __init__(self, threshold=2):
        self.last_price = None
        self.threshold = threshold
    
    def decide(self, price):
        if self.last_price is None:
            self.last_price = price
            return "HOLD"
        
        change = (price - self.last_price) / self.last_price * 100
        self.last_price = price
        
        if change > self.threshold:
            return "BUY"
        elif change < -self.threshold:
            return "SELL"
        else:
            return "HOLD"
```

### portfolio.py

```python
class Portfolio:
    def __init__(self, cash=10000):
        self.cash = cash
        self.shares = 0
    
    def buy(self, price):
        if self.cash >= price:
            self.shares += 1
            self.cash -= price
    
    def sell(self, price):
        if self.shares > 0:
            self.shares -= 1
            self.cash += price
    
    def value(self, current_price):
        return self.cash + self.shares * current_price
```

### trading_engine.py

```python
class TradingEngine:
    def __init__(self):
        self.strategy = TradingStrategy()
        self.portfolio = Portfolio()
    
    def process_tick(self, tick):
        price = tick["price"]
        decision = self.strategy.decide(price)
        
        if decision == "BUY":
            self.portfolio.buy(price)
        elif decision == "SELL":
            self.portfolio.sell(price)
        
        print(
            "PRICE:", round(price, 2),
            "| DECISION:", decision,
            "| CASH:", round(self.portfolio.cash, 2),
            "| SHARES:", self.portfolio.shares,
            "| VALUE:", round(self.portfolio.value(price), 2)
        )
```

## Running Step 2

```cmd
python integration_test.py
```

## Expected Output

```
PRICE: 189.4 | DECISION: HOLD | CASH: 10000 | SHARES: 0 | VALUE: 10000
PRICE: 193.1 | DECISION: BUY  | CASH: 9807 | SHARES: 1 | VALUE: 10000
PRICE: 180.2 | DECISION: SELL | CASH: 9987 | SHARES: 0 | VALUE: 9987
```

System is now reacting to data.

## Testing Requirements

Step 2 is complete when:
- ✅ Receives stream from Step 1
- ✅ Generates decisions
- ✅ Portfolio updates correctly
- ✅ No crashes
- ✅ Logs readable

## Definition of Step 2 Complete

You have:
- ✅ Automated trading reacting to price
- ✅ Simulated financial state
- ✅ Visible consequences

Now manipulation will cause incorrect trades.
Perfect setup for Step 3.
