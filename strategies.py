from abc import ABC, abstractmethod
from typing import List, Dict
from datetime import datetime
from models import Strategy, StrategyType, Allocation, MarketData
from metrics import calculate_returns, calculate_sharpe_ratio, calculate_sortino_ratio, calculate_max_drawdown
import numpy as np

class BaseStrategy(ABC):
    def __init__(self, strategy_id: str, name: str, strategy_type: StrategyType):
        self.strategy_id = strategy_id
        self.name = name
        self.strategy_type = strategy_type
        self.price_history: Dict[str, List[float]] = {}
        self.returns_history: List[float] = []
        self.prev_prices: List[float] = []

    @abstractmethod
    def generate_allocation(self, market_data: List[MarketData]) -> List[Allocation]:
        pass

    def update_history(self, market_data: List[MarketData]):
        for md in market_data:
            if md.symbol not in self.price_history:
                self.price_history[md.symbol] = []
            self.price_history[md.symbol].append(md.price)
        
        # Simple aggregate return for the strategy performance tracking
        # For simplicity, we assume an equal-weighted return of all assets tracked
        current_prices = [md.price for md in market_data]
        if self.prev_prices:
            ret = (np.mean(current_prices) - np.mean(self.prev_prices)) / np.mean(self.prev_prices)
            self.returns_history.append(float(ret))
        self.prev_prices = current_prices

    def get_metrics(self) -> Dict[str, float]:
        if not self.returns_history:
            return {"sharpe": 0.0, "sortino": 0.0, "max_drawdown": 0.0}
        
        # Flatten price history for drawdown calculation
        all_prices = []
        for symbol in self.price_history:
            all_prices.extend(self.price_history[symbol])
            
        return {
            "sharpe": calculate_sharpe_ratio(np.array(self.returns_history)),
            "sortino": calculate_sortino_ratio(np.array(self.returns_history)),
            "max_drawdown": calculate_max_drawdown(all_prices) if all_prices else 0.0
        }

class BetaStrategy(BaseStrategy):
    """Passive Buy and Hold strategy for a specific benchmark (e.g., ^NSEI)."""
    def __init__(self, strategy_id: str, name: str, benchmark_symbol: str = "^NSEI"):
        super().__init__(strategy_id, name, StrategyType.BETA)
        self.benchmark_symbol = benchmark_symbol

    def generate_allocation(self, market_data: List[MarketData]) -> List[Allocation]:
        self.update_history(market_data)
        
        # Always 100% in the benchmark
        return [
            Allocation(
                strategy_id=self.strategy_id,
                asset_symbol=self.benchmark_symbol,
                weight=1.0,
                timestamp=datetime.now()
            )
        ]

class AlphaStrategy(BaseStrategy):
    """Mean Reversion Alpha strategy."""
    def __init__(self, strategy_id: str, name: str, symbols: List[str]):
        super().__init__(strategy_id, name, StrategyType.ALPHA)
        self.symbols = symbols
        self.lookback = 5

    def generate_allocation(self, market_data: List[MarketData]) -> List[Allocation]:
        self.update_history(market_data)
        
        allocations = []
        # Mean Reversion Logic: Buy assets that are below their mean
        eligible_assets = []
        for md in market_data:
            if md.symbol in self.symbols and md.symbol in self.price_history and len(self.price_history[md.symbol]) >= self.lookback:
                mean_price = np.mean(self.price_history[md.symbol][-self.lookback:])
                if md.price < mean_price:
                    eligible_assets.append(md.symbol)
        
        if not eligible_assets:
            # Fallback to cash or equal weight if no signals
            weight = 1.0 / len(self.symbols)
            for symbol in self.symbols:
                allocations.append(Allocation(self.strategy_id, symbol, weight, datetime.now()))
        else:
            weight = 1.0 / len(eligible_assets)
            for symbol in eligible_assets:
                allocations.append(Allocation(self.strategy_id, symbol, weight, datetime.now()))
                
        return allocations
