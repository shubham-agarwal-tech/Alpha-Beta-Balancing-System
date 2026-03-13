import numpy as np
import pandas as pd
from typing import List, Union

def calculate_returns(prices: Union[List[float], np.ndarray]) -> np.ndarray:
    """Calculates percentage returns from a price series."""
    prices = np.array(prices)
    if len(prices) < 2:
        return np.array([])
    returns = (prices[1:] - prices[:-1]) / prices[:-1]
    return returns

def calculate_sharpe_ratio(returns: np.ndarray, risk_free_rate: float = 0.02, periods_per_year: int = 252) -> float:
    """
    Calculates the annualized Sharpe Ratio.
    risk_free_rate is assumed to be annual.
    """
    if len(returns) == 0:
        return 0.0
    
    mean_return = np.mean(returns)
    std_return = np.std(returns)
    
    if std_return == 0:
        return 0.0
    
    # Adjust risk-free rate to the period
    rf_period = (1 + risk_free_rate) ** (1 / periods_per_year) - 1
    
    sharpe = (mean_return - rf_period) / std_return
    return sharpe * np.sqrt(periods_per_year)

def calculate_sortino_ratio(returns: np.ndarray, risk_free_rate: float = 0.02, periods_per_year: int = 252) -> float:
    """
    Calculates the annualized Sortino Ratio (only considers downside volatility).
    """
    if len(returns) == 0:
        return 0.0
    
    mean_return = np.mean(returns)
    rf_period = (1 + risk_free_rate) ** (1 / periods_per_year) - 1
    
    # Calculate downside deviation
    downside_returns = returns[returns < rf_period]
    if len(downside_returns) == 0:
        return 0.0
    
    downside_std = np.std(returns[returns < 0]) # Standard approach is often just negative returns
    if downside_std == 0:
        return 0.0
        
    sortino = (mean_return - rf_period) / downside_std
    return sortino * np.sqrt(periods_per_year)

def calculate_max_drawdown(prices: Union[List[float], np.ndarray]) -> float:
    """Calculates the maximum drawdown from a price series."""
    prices = np.array(prices)
    if len(prices) == 0:
        return 0.0
    
    peak = np.maximum.accumulate(prices)
    drawdown = (prices - peak) / peak
    return float(np.min(drawdown))

def calculate_correlation_matrix(returns_df: pd.DataFrame) -> pd.DataFrame:
    """Calculates the correlation matrix for a DataFrame of asset returns."""
    if returns_df.empty:
        return pd.DataFrame()
    return returns_df.corr()

def calculate_performance_by_category(strategy_data: List[dict]) -> List[dict]:
    """
    Aggregates performance metrics by strategy type or asset class.
    Expected input: list of dicts with 'type', 'name', 'return', 'sharpe'
    """
    if not strategy_data:
        return []
    
    df = pd.DataFrame(strategy_data)
    summary = df.groupby('type').agg({
        'return': 'mean',
        'sharpe': 'mean'
    }).reset_index()
    
    return summary.to_dict('records')
