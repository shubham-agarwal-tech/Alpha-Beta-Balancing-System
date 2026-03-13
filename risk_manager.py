from typing import List, Dict, Optional
import numpy as np
from models import Allocation, MarketData, RiskLimits, Strategy
from datetime import datetime

class RiskManager:
    def __init__(self, limits: RiskLimits = RiskLimits()):
        self.limits = limits
        self.entry_prices: Dict[str, float] = {}

    def apply_stop_loss_take_profit(self, current_allocations: List[Allocation], market_data: List[MarketData]) -> List[Allocation]:
        """Monitors positions and triggers exit if thresholds are breached."""
        prices = {md.symbol: md.price for md in market_data}
        adjusted_allocations = []
        
        for alloc in current_allocations:
            symbol = alloc.asset_symbol
            if symbol not in prices:
                adjusted_allocations.append(alloc)
                continue
                
            current_price = prices[symbol]
            
            # Record entry price if not tracked
            if symbol not in self.entry_prices:
                self.entry_prices[symbol] = current_price
            
            entry_price = self.entry_prices[symbol]
            pct_change = (current_price - entry_price) / entry_price
            
            if pct_change <= self.limits.stop_loss_pct:
                print(f"DEBUG: Stop-loss triggered for {symbol} at {current_price} (Price Change: {pct_change*100:.2f}%)")
                # Close position (set weight to 0)
                alloc.weight = 0.0
                del self.entry_prices[symbol]
            elif pct_change >= self.limits.take_profit_pct:
                print(f"DEBUG: Take-profit triggered for {symbol} at {current_price} (Price Change: {pct_change*100:.2f}%)")
                alloc.weight = 0.0
                del self.entry_prices[symbol]
            
            adjusted_allocations.append(alloc)
            
        return adjusted_allocations

    def calculate_kelly_fraction(self, win_prob: float, win_loss_ratio: float) -> float:
        """Calculates the Kelly Criterion fraction: f* = p - (1-p)/b """
        if win_loss_ratio <= 0:
            return 0.0
        fraction = win_prob - (1 - win_prob) / win_loss_ratio
        return max(0.0, min(fraction, self.limits.max_position_size))

    def apply_guardrails(self, allocations: List[Allocation]) -> List[Allocation]:
        """Ensures allocations do not exceed hard risk limits."""
        total_weight = sum(a.weight for a in allocations)
        
        for alloc in allocations:
            # Enforce max position size per asset
            if alloc.weight > self.limits.max_position_size:
                print(f"DEBUG: Guardrail triggered: Capping {alloc.asset_symbol} weight from {alloc.weight} to {self.limits.max_position_size}")
                alloc.weight = self.limits.max_position_size
        
        # Re-normalize if total exceeds 1.0
        new_total = sum(a.weight for a in allocations)
        if new_total > 1.0:
            for alloc in allocations:
                alloc.weight = alloc.weight / new_total
                
        return allocations

    def validate_strategy_risk(self, strategy: Strategy) -> bool:
        """Validates if a strategy's historical metrics are within acceptable bounds."""
        if strategy.risk_profile:
            if strategy.risk_profile.max_drawdown < self.limits.max_drawdown_limit:
                print(f"WARNING: Strategy {strategy.name} exceeds max drawdown limit ({strategy.risk_profile.max_drawdown:.2f})")
                return False
        return True
