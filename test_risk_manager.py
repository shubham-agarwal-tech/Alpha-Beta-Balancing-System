from risk_manager import RiskManager
from models import Allocation, MarketData, RiskLimits
from datetime import datetime

def test_risk_manager_guardrails():
    rm = RiskManager(RiskLimits(max_position_size=0.2))
    allocs = [
        Allocation("strat1", "AAPL", 0.5, datetime.now()),
        Allocation("strat1", "MSFT", 0.1, datetime.now())
    ]
    
    adjusted = rm.apply_guardrails(allocs)
    
    # AAPL should be capped at 0.2
    aapl_alloc = next(a for a in adjusted if a.asset_symbol == "AAPL")
    assert aapl_alloc.weight == 0.2
    
    # Total should be normalized or at least not exceed 1.0
    assert sum(a.weight for a in adjusted) <= 1.0

def test_risk_manager_stop_loss():
    rm = RiskManager(RiskLimits(stop_loss_pct=-0.05))
    allocs = [Allocation("strat1", "BTC", 0.5, datetime.now())]
    
    # Initial price
    market_data_1 = [MarketData("BTC", datetime.now(), 100.0)]
    rm.apply_stop_loss_take_profit(allocs, market_data_1)
    
    # Price drop 10%
    market_data_2 = [MarketData("BTC", datetime.now(), 90.0)]
    adjusted = rm.apply_stop_loss_take_profit(allocs, market_data_2)
    
    btc_alloc = next(a for a in adjusted if a.asset_symbol == "BTC")
    assert btc_alloc.weight == 0.0

def test_kelly_fraction():
    rm = RiskManager(RiskLimits(max_position_size=0.5))
    # Win prob 60%, win/loss 2:1 -> Kelly = 0.6 - (0.4/2) = 0.4
    fraction = rm.calculate_kelly_fraction(0.6, 2.0)
    assert abs(fraction - 0.4) < 1e-6
    print("test_kelly_fraction passed")

if __name__ == "__main__":
    test_risk_manager_guardrails()
    test_risk_manager_stop_loss()
    test_kelly_fraction()
    print("All RiskManager tests passed!")
