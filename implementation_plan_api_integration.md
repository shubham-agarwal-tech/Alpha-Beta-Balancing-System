# API Integration Implementation Plan

Integrate real-world financial and geopolitical data sources to replace mock data in the [ingestion.py](file:///c:/Users/Pc/Desktop/Shubham/13.03.2026/alpha_beta_system%20-phase-4/ingestion.py) module.

## User Review Required

> [!IMPORTANT]
> This change requires an API key for **NewsAPI**. I will provide a [.env.example](file:///c:/Users/Pc/Desktop/Shubham/13.03.2026/alpha_beta_system%20-phase-4/.env.example) file. You will need to obtain this key and add it to a `.env` file in the project root.
> - NewsAPI: [https://newsapi.org/](https://newsapi.org/)
> 
> **Macroeconomic data** now uses the **World Bank API** (no key required) and **Yahoo Finance** treasury yield proxies, removing the need for a FRED API key.

## Proposed Changes

### Core System

#### [MODIFY] [requirements.txt](file:///c:/Users/Pc/Desktop/Shubham/13.03.2026/alpha_beta_system%20-phase-4/requirements.txt)
- Add `yfinance`, `newsapi-python`, `python-dotenv`, `requests`. (Remove `fredapi`).

#### [MODIFY] [.env.example](file:///c:/Users/Pc/Desktop/Shubham/13.03.2026/alpha_beta_system%20-phase-4/.env.example)
- Remove `FRED_API_KEY`.

#### [MODIFY] [ingestion.py](file:///c:/Users/Pc/Desktop/Shubham/13.03.2026/alpha_beta_system%20-phase-4/ingestion.py)
- Replace `fredapi` usage with `requests` calls to World Bank API.
- Use `yfinance` to fetch `^IRX` (13-week T-Bill) for Interest Rates.
- Implement robust error handling for API failures.

#### [MODIFY] [main.py](file:///c:/Users/Pc/Desktop/Shubham/13.03.2026/alpha_beta_system%20-phase-4/main.py)
- Update import and instantiation from `MockIngestionService` to [IngestionService](file:///c:/Users/Pc/Desktop/Shubham/13.03.2026/alpha_beta_system%20-phase-4/ingestion.py#15-161).

#### [MODIFY] [app.py](file:///c:/Users/Pc/Desktop/Shubham/13.03.2026/alpha_beta_system%20-phase-4/app.py)
- Update import and instantiation from `MockIngestionService` to [IngestionService](file:///c:/Users/Pc/Desktop/Shubham/13.03.2026/alpha_beta_system%20-phase-4/ingestion.py#15-161).

## Verification Plan

### Automated Tests
1. **Unit Tests for Ingestion**:
   - Create a temporary test script `test_api_connection.py` to verify that each API (yfinance, NewsAPI, FRED) can fetch data given the keys.
   - Run: `python test_api_connection.py`
2. **Existing Infrastructure**:
   - Run `python main.py` to ensure the system still runs end-to-end with real data.

### Manual Verification
1. **API Key Setup**:
   - User needs to fill in `.env` with valid keys.
2. **Data Consistency**:
   - Verify that the prices returned by [get_market_data](file:///c:/Users/Pc/Desktop/Shubham/13.03.2026/alpha_beta_system%20-phase-4/app.py#24-51) match expected tickers (SPY, BTC, etc.).
   - Verify that news headlines are current and relevant to geopolitical terms.
