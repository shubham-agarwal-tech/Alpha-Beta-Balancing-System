from typing import List, Dict, Tuple
import numpy as np
from datetime import datetime
from models import MarketData, MarketRegime, StrategyType, Allocation

class MLOptimizer:
    def __init__(self):
        self.market_history: List[float] = []
        self.regime_map = {
            MarketRegime.BULL: {"alpha_weight": 0.7, "beta_weight": 0.3},
            MarketRegime.BEAR: {"alpha_weight": 0.2, "beta_weight": 0.8},
            MarketRegime.SIDEWAYS: {"alpha_weight": 0.5, "beta_weight": 0.5},
            MarketRegime.HIGH_VOLATILITY: {"alpha_weight": 0.1, "beta_weight": 0.9}
        }

    def detect_regime(self, market_data: List[MarketData]) -> MarketRegime:
        """
        Heuristic-based ML classifier to identify market regime.
        In a real scenario, this would be an LSTM or Random Forest model.
        """
        # Using ^NSEI (Nifty 50) as a proxy for market sentiment
        nsei_prices = [md.price for md in market_data if md.symbol == "^NSEI"]
        if not nsei_prices:
            return MarketRegime.SIDEWAYS
        
        self.market_history.append(nsei_prices[0])
        if len(self.market_history) < 5:
            return MarketRegime.SIDEWAYS
        
        recent_prices = self.market_history[-5:]
        returns = np.diff(recent_prices) / recent_prices[:-1]
        mean_ret = np.mean(returns)
        volatility = np.std(returns)
        
        if volatility > 0.02: # Threshold for high volatility
            return MarketRegime.HIGH_VOLATILITY
        elif mean_ret > 0.005:
            return MarketRegime.BULL
        elif mean_ret < -0.005:
            return MarketRegime.BEAR
        else:
            return MarketRegime.SIDEWAYS

    def optimize_allocation(self, market_regime: MarketRegime, 
                           alpha_allocations: List[Allocation], 
                           beta_allocations: List[Allocation]) -> List[Allocation]:
        """
        Dynamically adjusts capital weights between Alpha and Beta strategies 
        based on the detected market regime.
        """
        weights = self.regime_map.get(market_regime, self.regime_map[MarketRegime.SIDEWAYS])
        alpha_w = weights["alpha_weight"]
        beta_w = weights["beta_weight"]
        
        print(f"DEBUG: Market Regime Detected: {market_regime.value}. Reallocating: Alpha {alpha_w*100}%, Beta {beta_w*100}%")
        
        final_allocations = []
        
        # Scale alpha allocations
        for alloc in alpha_allocations:
            alloc.weight *= alpha_w
            final_allocations.append(alloc)
            
        # Scale beta allocations
        for alloc in beta_allocations:
            alloc.weight *= beta_w
            final_allocations.append(alloc)
            
        # Final normalization to ensure total weight <= 1.0
        total_weight = sum(a.weight for a in final_allocations)
        if total_weight > 1.0:
            for alloc in final_allocations:
                alloc.weight /= total_weight
                
        return final_allocations
