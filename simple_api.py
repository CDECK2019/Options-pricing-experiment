from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Union
import logging
from simple_yahoo_connector import SimpleYahooConnector
from simple_scenario_analyzer import SimpleScenarioAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScenarioRequest(BaseModel):
    ticker: str
    min_change: float
    max_change: float
    step_size: float
    max_expiry_count: Optional[int] = 3

yahoo = SimpleYahooConnector()
analyzer = SimpleScenarioAnalyzer()

@app.post("/api/analyze")
async def analyze_scenarios(request: ScenarioRequest):
    try:
        logger.info(f"Received request for ticker: {request.ticker}")
        
        # Get current stock price and options
        stock_price = yahoo.get_stock_price(request.ticker)
        logger.info(f"Current stock price: {stock_price}")
        
        options_by_date = yahoo.get_options_chain(request.ticker, request.max_expiry_count)
        logger.info(f"Retrieved options for {len(options_by_date)} expiration dates")
        
        if not stock_price or not options_by_date:
            raise HTTPException(status_code=404, detail="Data not found")
        
        results = {}
        current_change = request.min_change
        
        while current_change <= request.max_change:
            # Calculate new stock price for this scenario
            new_stock_price = stock_price * (1 + current_change / 100)
            logger.info(f"Analyzing scenario: {current_change}% change, new price: {new_stock_price}")
            
            # Analyze options for each expiration date
            analyzed_by_date = {}
            
            for expiry_date, options_list in options_by_date.items():
                # Analyze all options for this price point and expiration
                analyzed_options = []
                for option in options_list:
                    analysis = analyzer.calculate_profit_potential(
                        current_price=stock_price,
                        new_stock_price=new_stock_price,
                        option_data=option
                    )
                    if analysis:
                        analyzed_option = {
                            **option,
                            "theoretical_value": analysis["new_option_price"],
                            "profit_potential": analysis["percent_change"]
                        }
                        analyzed_options.append(analyzed_option)
                
                # Sort by profit potential and get best performers
                analyzed_options.sort(key=lambda x: x.get("profit_potential", 0), reverse=True)
                analyzed_by_date[expiry_date] = analyzed_options
            
            results[str(current_change)] = {
                "new_stock_price": new_stock_price,
                "options_by_date": analyzed_by_date
            }
            
            current_change += request.step_size
        
        response_data = {
            "ticker": request.ticker,
            "current_price": stock_price,
            "results": results
        }
        logger.info(f"Analysis complete for {request.ticker}")
        return JSONResponse(content=response_data)
        
    except Exception as e:
        logger.error(f"Error in analyze_scenarios: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/options/{ticker}")
async def get_options(ticker: str):
    try:
        stock_price = yahoo.get_stock_price(ticker)
        options_chain = yahoo.get_options_chain(ticker)
        
        if not options_chain:
            raise HTTPException(status_code=404, detail="No options data found")
            
        return {
            "stock_price": stock_price,
            "options_chain": options_chain
        }
        
    except Exception as e:
        logger.error(f"Error in get_options: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Mount the static files directory AFTER the API routes
app.mount("/", StaticFiles(directory=".", html=True), name="static")
