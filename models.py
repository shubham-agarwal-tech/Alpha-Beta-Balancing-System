from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum

class AssetType(Enum):
    EQUITY = "equity"
    BOND = "bond"
    COMMODITY = "commodity"
    CRYPTO = "crypto"

class StrategyType(Enum):
    ALPHA = "alpha"
    BETA = "beta"

class MarketRegime(Enum):
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    HIGH_VOLATILITY = "high_volatility"

@dataclass
class RiskLimits:
    max_position_size: float = 0.2  # Max 20% per asset
    max_drawdown_limit: float = -0.15 # Max 15% drawdown before exit
    stop_loss_pct: float = -0.05    # 5% stop loss
    take_profit_pct: float = 0.15   # 15% take profit

@dataclass
class Asset:
    symbol: str
    asset_type: AssetType
    description: str

@dataclass
class MarketData:
    symbol: str
    timestamp: datetime
    price: float
    volume: Optional[float] = None

@dataclass
class RiskProfile:
    volatility: float
    max_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float

@dataclass
class Allocation:
    strategy_id: str
    asset_symbol: str
    weight: float  # Percentage of capital
    timestamp: datetime

@dataclass
class Strategy:
    id: str
    name: str
    strategy_type: StrategyType
    assets: List[str]
    current_allocation: List[Allocation] = field(default_factory=list)
    risk_profile: Optional[RiskProfile] = None

@dataclass
class PerformanceMetric:
    strategy_id: str
    timestamp: datetime
    return_pct: float
    cumulative_return: float
