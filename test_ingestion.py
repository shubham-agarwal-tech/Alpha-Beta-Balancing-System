import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
from datetime import datetime
from ingestion import IngestionService
from models import Asset, AssetType, MarketData

@pytest.fixture
def ingestion_service():
    with patch('ingestion.load_dotenv'):
        service = IngestionService()
        return service

def test_get_assets(ingestion_service):
    assets = ingestion_service.get_assets()
    assert len(assets) > 0
    assert any(asset.symbol == "^NSEI" for asset in assets)
    assert isinstance(assets[0], Asset)

def test_get_asset_classes(ingestion_service):
    classes = ingestion_service.get_asset_classes()
    assert "^NSEI" in classes
    assert classes["^NSEI"] == AssetType.EQUITY.value
    assert classes["RELIANCE.NS"] == AssetType.EQUITY.value

@patch('ingestion.yf.Tickers')
def test_fetch_market_data(mock_tickers, ingestion_service):
    # Mock fast_info behavior
    mock_ticker = MagicMock()
    mock_ticker.fast_info = {'last_price': 100.0, 'last_volume': 1000}
    mock_tickers.return_value.tickers = {'^NSEI': mock_ticker}
    
    data = ingestion_service.fetch_market_data(['^NSEI'])
    
    assert len(data) == 1
    assert data[0].symbol == '^NSEI'
    assert data[0].price == 100.0
    assert data[0].volume == 1000.0

@patch('ingestion.yf.Tickers')
def test_fetch_market_data_fallback(mock_tickers, ingestion_service):
    # Mock fallback to history
    mock_ticker = MagicMock()
    mock_ticker.fast_info = {'last_price': None}
    mock_ticker.history.return_value = pd.DataFrame({'Close': [105.0]}, index=[datetime.now()])
    mock_tickers.return_value.tickers = {'^NSEI': mock_ticker}
    
    data = ingestion_service.fetch_market_data(['^NSEI'])
    
    assert len(data) == 1
    assert data[0].price == 105.0

@patch('ingestion.Fred')
def test_get_economic_indicators(mock_fred_class, ingestion_service):
    mock_fred = MagicMock()
    mock_fred_class.return_value = mock_fred
    ingestion_service.fred = mock_fred
    
    # Mock FRED series data
    mock_fred.get_series.side_effect = [
        pd.Series([2.5]), # GDP
        pd.Series([250.0, 260.0, 270.0]), # CPI (last 13 elements needed for calculation, but we can mock as needed)
        pd.Series([5.25]), # Interest Rate
        pd.Series([3.8])   # Unemployment
    ]
    
    # CPI mock specifically for the 12-month calculation
    cpi_data = [100.0] * 13
    cpi_data[-1] = 105.0 # 5% increase
    mock_fred.get_series.side_effect = [
        pd.Series([2.5]), 
        pd.Series([2.5]), # First CPI call (FPCPITOTLZGUSA fallback)
        pd.Series(cpi_data), # Second CPI call (CPIAUCSL)
        pd.Series([5.25]), 
        pd.Series([3.8])
    ]
    
    indicators = ingestion_service.get_economic_indicators()
    
    assert indicators["GDP_Growth"] == 2.5
    assert indicators["Interest_Rate"] == 5.25
    assert indicators["Unemployment_Rate"] == 3.8
    assert indicators["CPI_Inflation"] == pytest.approx(5.0)

@patch('ingestion.NewsApiClient')
def test_get_geopolitical_news(mock_news_class, ingestion_service):
    mock_news = MagicMock()
    mock_news_class.return_value = mock_news
    ingestion_service.newsapi = mock_news
    
    mock_news.get_everything.return_value = {
        'articles': [
            {'title': 'War escalates in region', 'url': 'http://test.com/1'},
            {'title': 'Peace summit a success', 'url': 'http://test.com/2'},
            {'title': 'Market remains stable', 'url': 'http://test.com/3'}
        ]
    }
    
    news = ingestion_service.get_geopolitical_news()
    
    assert len(news) == 3
    assert news[0]['sentiment'] == 'negative'
    assert news[0]['impact_score'] == 0.8
    assert news[1]['sentiment'] == 'positive'
    assert news[1]['impact_score'] == 0.6
    assert news[2]['sentiment'] == 'neutral'
    assert news[2]['impact_score'] == 0.5

@patch('ingestion.yf.download')
def test_fetch_historical_data(mock_download, ingestion_service):
    # Mock single symbol response
    mock_df = pd.DataFrame({'Close': [100.0, 101.0, 102.0]})
    mock_download.return_value = mock_df
    
    data = ingestion_service.fetch_historical_data(['^NSEI'], days=3)
    
    assert '^NSEI' in data
    assert data['^NSEI'] == [100.0, 101.0, 102.0]
    
    # Mock multiple symbols (returned as MultiIndex columns)
    mock_df_multi = pd.DataFrame({
        ('^NSEI', 'Close'): [100.0, 101.0],
        ('RELIANCE.NS', 'Close'): [90.0, 91.0]
    })
    # yfinance returns a MultiIndex if multiple tickers are requested
    # But mock the structure that ingestion.py expects
    # In ingestion.py: if len(yf_symbols) > 1: df = data[yf_sym]
    
    mock_download.return_value = {
        '^NSEI': pd.DataFrame({'Close': [100.0, 101.0]}),
        'RELIANCE.NS': pd.DataFrame({'Close': [90.0, 91.0]})
    }
    
    # Wait, ingestion.py line 147: df = data[yf_sym]
    # If data is a dict-like or DataFrame with MultiIndex columns
    
    data = ingestion_service.fetch_historical_data(['^NSEI', 'RELIANCE.NS'], days=2)
    assert '^NSEI' in data
    assert 'RELIANCE.NS' in data
    assert data['^NSEI'] == [100.0, 101.0]
