import random
from datetime import datetime, timedelta
from typing import List, Dict
from models import MarketData, Asset, AssetType

class MockIngestionService:
    def __init__(self):
        self.assets = {
            "SPY": Asset("SPY", AssetType.EQUITY, "S&P 500 ETF Trust"),
            "TLT": Asset("TLT", AssetType.BOND, "iShares 20+ Year Treasury Bond ETF"),
            "GLD": Asset("GLD", AssetType.COMMODITY, "SPDR Gold Shares"),
            "BTC": Asset("BTC", AssetType.CRYPTO, "Bitcoin"),
        }
        self.current_prices = {
            "SPY": 450.0,
            "TLT": 100.0,
            "GLD": 180.0,
            "BTC": 40000.0,
        }

    def get_assets(self) -> List[Asset]:
        return list(self.assets.values())

    def fetch_market_data(self, symbols: List[str]) -> List[MarketData]:
        """Simulates fetching real-time market data with slight price fluctuations."""
        data = []
        for symbol in symbols:
            if symbol in self.current_prices:
                # Add some random walk
                change = random.uniform(-0.01, 0.01)
                self.current_prices[symbol] *= (1 + change)
                
                md = MarketData(
                    symbol=symbol,
                    timestamp=datetime.now(),
                    price=self.current_prices[symbol],
                    volume=random.uniform(10000, 1000000)
                )
                data.append(md)
        return data

    def get_economic_indicators(self) -> Dict[str, float]:
        """Simulates fetching key macroeconomic indicators."""
        return {
            "GDP_Growth": 2.5,
            "CPI_Inflation": 3.2,
            "Interest_Rate": 5.25,
            "Unemployment_Rate": 3.8
        }

    def get_geopolitical_news(self) -> List[Dict[str, str]]:
        """Simulates fetching simplified geopolitical sentiment."""
        return [
            {"headline": "Trade talks show progress", "sentiment": "positive", "impact_score": 0.7},
            {"headline": "Regional conflict escalates", "sentiment": "negative", "impact_score": 0.9},
            {"headline": "Central bank signals rate pause", "sentiment": "neutral", "impact_score": 0.5}
        ]

    def fetch_historical_data(self, symbols: List[str], days: int = 30) -> Dict[str, List[float]]:
        """Simulates historical price data for a set of symbols."""
        historical_data = {}
        for symbol in symbols:
            if symbol in self.current_prices:
                base_price = self.current_prices[symbol]
                prices = []
                for _ in range(days):
                    # Random walk for history
                    change = random.uniform(-0.02, 0.02)
                    base_price *= (1 + change)
                    prices.append(base_price)
                historical_data[symbol] = prices
        return historical_data

    def get_asset_classes(self) -> Dict[str, str]:
        """Returns mapping of symbols to asset types."""
        return {symbol: asset.asset_type.value for symbol, asset in self.assets.items()}
