import numpy as np
from ml_optimizer import MLOptimizer
from models import MarketData, MarketRegime, Allocation
from datetime import datetime

def test_ml_optimizer_regime_detection():
    optimizer = MLOptimizer()
    
    # Simulate a bull market (prices going up)
    prices = [100.0, 101.0, 102.0, 103.0, 105.0]
    for p in prices:
        regime = optimizer.detect_regime([MarketData("SPY", datetime.now(), p)])
        
    assert regime == MarketRegime.BULL

def test_ml_optimizer_allocation_scaling():
    optimizer = MLOptimizer()
    alpha_alloc = [Allocation("alpha", "BTC", 1.0, datetime.now())]
    beta_alloc = [Allocation("beta", "SPY", 1.0, datetime.now())]
    
    # In BEAR regime, beta should be 0.8, alpha 0.2
    final = optimizer.optimize_allocation(MarketRegime.BEAR, alpha_alloc, beta_alloc)
    
    btc_weight = next(a.weight for a in final if a.asset_symbol == "BTC")
    spy_weight = next(a.weight for a in final if a.asset_symbol == "SPY")
    
    assert abs(btc_weight - 0.2) < 1e-6
    assert abs(spy_weight - 0.8) < 1e-6
    print("test_ml_optimizer_allocation_scaling passed")

if __name__ == "__main__":
    test_ml_optimizer_regime_detection()
    test_ml_optimizer_allocation_scaling()
    print("All MLOptimizer tests passed!")
