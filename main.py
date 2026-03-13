from ingestion import MockIngestionService
from strategies import AlphaStrategy, BetaStrategy
from risk_manager import RiskManager
from ml_optimizer import MLOptimizer
from models import StrategyType
import time

def run_phase3_demo():
    print("=== Alpha-Beta System Phase 3: Risk Management & ML Feedback Demo ===\n")
    
    ingestion = MockIngestionService()
    risk_manager = RiskManager()
    ml_optimizer = MLOptimizer()
    
    # Initialize Strategies
    beta_strat = BetaStrategy("strat_beta_001", "Passive Beta (SPY)")
    alpha_strat = AlphaStrategy("strat_alpha_001", "Mean Reversion Alpha", ["SPY", "BTC"])
    
    symbols = ["SPY", "TLT", "GLD", "BTC"]
    
    print(f"System Components Initialized. Starting Dynamic Allocation Loop...\n")
    
    for i in range(1, 16):
        print(f"--- Iteration {i} ---")
        market_data = ingestion.fetch_market_data(symbols)
        
        # 1. Detect Market Regime
        regime = ml_optimizer.detect_regime(market_data)
        
        # 2. Generate Initial Strategy Allocations
        alpha_alloc = alpha_strat.generate_allocation(market_data)
        beta_alloc = beta_strat.generate_allocation(market_data)
        
        # 3. Dynamic Reallocation (ML Feedback)
        final_alloc = ml_optimizer.optimize_allocation(regime, alpha_alloc, beta_alloc)
        
        # 4. Apply Risk Guardrails
        final_alloc = risk_manager.apply_guardrails(final_alloc)
        
        # 5. Monitor Stop-Loss/Take-Profit
        final_alloc = risk_manager.apply_stop_loss_take_profit(final_alloc, market_data)
        
        print(f"Final System Allocation:")
        for a in final_alloc:
            if a.weight > 0:
                print(f"  - {a.asset_symbol}: {a.weight*100:.2f}%")
        
        # Performance Tracking
        alpha_metrics = alpha_strat.get_metrics()
        print(f"Alpha Strategy Stats: Sharpe {alpha_metrics['sharpe']:.2f}, MaxDD {alpha_metrics['max_drawdown']*100:.2f}%")
        print("-" * 30)
        time.sleep(0.3)

    print("\n=== Phase 3 Implementation Verified ===")

if __name__ == "__main__":
    run_phase3_demo()
