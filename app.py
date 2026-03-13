from fastapi import FastAPI, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from ingestion import IngestionService
from strategies import AlphaStrategy, BetaStrategy
from risk_manager import RiskManager
from ml_optimizer import MLOptimizer
from models import StrategyType
from metrics import calculate_correlation_matrix, calculate_performance_by_category
import pandas as pd
from datetime import datetime
import os
import uvicorn

app = FastAPI(title="Alpha-Beta System API")
ingestion = IngestionService()

# Global strategy instances for demo
alpha_strat = AlphaStrategy("strat_alpha_001", "Mean Reversion Alpha", ["RELIANCE.NS", "TCS.NS"])
beta_strat = BetaStrategy("strat_beta_001", "Passive Beta (^NSEI)", "^NSEI")
risk_manager = RiskManager()
ml_optimizer = MLOptimizer()

@app.get("/api/market-data")
async def get_market_data():
    symbols = ["^NSEI", "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "GOLDBEES.NS"]
    data = ingestion.fetch_market_data(symbols)
    
    # 1. Detect Regime
    regime = ml_optimizer.detect_regime(data)
    
    # 2. Update strategies with new data
    alpha_alloc = alpha_strat.generate_allocation(data)
    beta_alloc = beta_strat.generate_allocation(data)
    
    # 3. Dynamic Reallocation
    final_alloc = ml_optimizer.optimize_allocation(regime, alpha_alloc, beta_alloc)
    
    # 4. Apply Risk Controls
    final_alloc = risk_manager.apply_guardrails(final_alloc)
    final_alloc = risk_manager.apply_stop_loss_take_profit(final_alloc, data)
    
    return {
        "market_data": data,
        "regime": regime.value,
        "final_allocation": [
            {"symbol": a.asset_symbol, "weight": a.weight} 
            for a in final_alloc if a.weight > 0
        ]
    }

@app.get("/api/economic-indicators")
async def get_economic_indicators():
    return ingestion.get_economic_indicators()

@app.get("/api/strategies")
async def get_strategies():
    return [
        {
            "id": alpha_strat.strategy_id,
            "name": alpha_strat.name,
            "type": alpha_strat.strategy_type.value,
            "metrics": alpha_strat.get_metrics(),
            "allocation": [
                {"symbol": a.asset_symbol, "weight": a.weight} 
                for a in alpha_strat.generate_allocation(ingestion.fetch_market_data(["RELIANCE.NS", "TCS.NS"]))
            ]
        },
        {
            "id": beta_strat.strategy_id,
            "name": beta_strat.name,
            "type": beta_strat.strategy_type.value,
            "metrics": beta_strat.get_metrics(),
            "allocation": [
                {"symbol": a.asset_symbol, "weight": a.weight}
                for a in beta_strat.generate_allocation(ingestion.fetch_market_data(["^NSEI"]))
            ]
        }
    ]

@app.get("/api/news")
async def get_news():
    return ingestion.get_geopolitical_news()

@app.get("/api/analytics/correlation")
async def get_correlation():
    symbols = ["^NSEI", "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "GOLDBEES.NS"]
    hist_data = ingestion.fetch_historical_data(symbols)
    df = pd.DataFrame(hist_data)
    corr_matrix = calculate_correlation_matrix(df)
    return corr_matrix.to_dict()

@app.get("/api/analytics/performance")
async def get_performance_report():
    # Mock data for demonstration of multi-dimensional reporting
    strat_data = [
        {"type": "alpha", "name": alpha_strat.name, "return": 0.05, "sharpe": 1.5},
        {"type": "beta", "name": beta_strat.name, "return": 0.03, "sharpe": 1.1}
    ]
    report = calculate_performance_by_category(strat_data)
    return report

# Mount static files
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {"message": "Static index.html not found"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
