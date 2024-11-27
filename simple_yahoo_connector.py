import yfinance as yf
import pandas as pd
from datetime import datetime
import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleYahooConnector:
    def __init__(self):
        pass
    
    def get_stock_price(self, ticker):
        """Get current stock price for a ticker"""
        try:
            logger.info(f"Fetching stock price for {ticker}")
            stock = yf.Ticker(ticker)
            info = stock.info
            price = info.get('regularMarketPrice')
            if not price:
                price = info.get('currentPrice')
            logger.info(f"Retrieved price for {ticker}: {price}")
            return price
        except Exception as e:
            logger.error(f"Error fetching stock price for {ticker}: {str(e)}")
            raise Exception(f"Error fetching stock price: {str(e)}")

    def get_options_chain(self, ticker, max_expiry_count: int = 3) -> Dict[str, List[dict]]:
        """
        Get options chain for a ticker, organized by expiration date
        
        Args:
            ticker: Stock ticker symbol
            max_expiry_count: Maximum number of expiration dates to fetch
            
        Returns:
            Dictionary with expiration dates as keys and lists of option data as values
        """
        try:
            logger.info(f"Fetching options chain for {ticker}")
            stock = yf.Ticker(ticker)
            
            # Get all expiration dates
            expirations = stock.options
            logger.info(f"Available expiration dates: {expirations}")
            
            if not expirations:
                raise Exception("No options available for this ticker")
            
            # Limit to max_expiry_count dates
            expirations = expirations[:max_expiry_count]
            
            options_by_date = {}
            today = datetime.now()
            
            for expiry in expirations:
                exp_date = datetime.strptime(expiry, '%Y-%m-%d')
                years_to_exp = (exp_date - today).days / 365.0
                
                # Get options chain for this expiration
                opt = stock.option_chain(expiry)
                
                # Process calls and puts with volume > 0
                calls = opt.calls[opt.calls['volume'] > 0]
                puts = opt.puts[opt.puts['volume'] > 0]
                
                # Convert to list of dictionaries
                options_list = []
                
                # Process calls
                for _, row in calls.iterrows():
                    option_data = {
                        'expiration_date': expiry,
                        'days_to_expiry': (exp_date - today).days,
                        'strike': float(row['strike']),
                        'expiration': float(years_to_exp),
                        'implied_volatility': float(row['impliedVolatility']),
                        'option_type': 'call',
                        'current_option_price': float(row['lastPrice']),
                        'volume': int(row['volume']),
                        'open_interest': int(row['openInterest']),
                        'bid': float(row.get('bid', 0) or 0),
                        'ask': float(row.get('ask', 0) or 0),
                        'delta': float(row.get('delta', 0) or 0),
                        'gamma': float(row.get('gamma', 0) or 0),
                        'theta': float(row.get('theta', 0) or 0),
                        'vega': float(row.get('vega', 0) or 0)
                    }
                    options_list.append(option_data)
                
                # Process puts
                for _, row in puts.iterrows():
                    option_data = {
                        'expiration_date': expiry,
                        'days_to_expiry': (exp_date - today).days,
                        'strike': float(row['strike']),
                        'expiration': float(years_to_exp),
                        'implied_volatility': float(row['impliedVolatility']),
                        'option_type': 'put',
                        'current_option_price': float(row['lastPrice']),
                        'volume': int(row['volume']),
                        'open_interest': int(row['openInterest']),
                        'bid': float(row.get('bid', 0) or 0),
                        'ask': float(row.get('ask', 0) or 0),
                        'delta': float(row.get('delta', 0) or 0),
                        'gamma': float(row.get('gamma', 0) or 0),
                        'theta': float(row.get('theta', 0) or 0),
                        'vega': float(row.get('vega', 0) or 0)
                    }
                    options_list.append(option_data)
                
                # Sort options by strike price and option type
                options_list.sort(key=lambda x: (x['strike'], x['option_type']))
                
                # Store in dictionary
                options_by_date[expiry] = options_list
                logger.info(f"Retrieved {len(options_list)} options for {ticker} expiring on {expiry}")
            
            return options_by_date
            
        except Exception as e:
            logger.error(f"Error fetching options chain for {ticker}: {str(e)}")
            raise Exception(f"Error fetching options chain: {str(e)}")
