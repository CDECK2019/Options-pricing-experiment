from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="Options Screener API")

class ScreenerFilter(BaseModel):
    min_volume: Optional[int] = 0
    min_open_interest: Optional[int] = 0
    min_iv: Optional[float] = None
    max_iv: Optional[float] = None
    min_delta: Optional[float] = None
    max_delta: Optional[float] = None
    min_strike_ratio: Optional[float] = None
    max_strike_ratio: Optional[float] = None
    min_dte: Optional[int] = None
    max_dte: Optional[int] = None
    max_spread_percent: Optional[float] = None

class OptionContract(BaseModel):
    symbol: str
    strike: float
    expiration: datetime
    option_type: str
    bid: float
    ask: float
    volume: int
    open_interest: int
    implied_vol: float
    delta: float
    gamma: float
    theta: float
    vega: float

@app.post("/api/v1/screen")
async def screen_options(filters: ScreenerFilter) -> List[OptionContract]:
    """
    Screen options based on provided filters
    """
    try:
        # Convert filters to FilterParameters and apply
        filter_params = FilterParameters(**filters.dict())
        filtered_options = OptionsFilters.apply_all_filters(
            get_options_data(), filter_params)
        return [OptionContract(**opt) for opt in filtered_options.to_dict('records')]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/templates")
async def get_screen_templates():
    """
    Get predefined screening templates
    """
    return {
        "covered_call": ScreenerFilter(
            min_delta=0.3,
            max_delta=0.5,
            min_dte=30,
            max_dte=45,
            min_volume=100
        ),
        "iron_condor": ScreenerFilter(
            min_iv=0.2,
            max_delta=0.3,
            min_dte=25,
            max_dte=45
        )
        # Add more templates as needed
    }

@app.post("/api/v1/save_template")
async def save_template(name: str, filters: ScreenerFilter):
    """
    Save a custom screening template
    """
    # Save to database
    pass

@app.get("/api/v1/market_data/{symbol}")
async def get_market_data(symbol: str):
    """
    Get current market data for a symbol
    """
    pass
