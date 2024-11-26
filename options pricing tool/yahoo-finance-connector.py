import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

class YahooOptionsAPI:
    def __init__(self):
        """Initialize Yahoo Finance options data connector"""
        self.rate_limit_delay = 1.0  # Delay between requests to avoid rate limiting
        
    def get_options_chain(self, symbol: str, expiration_date: Optional[str] = None) -> pd.DataFrame:
        """
        Get options chain for a symbol
        
        Parameters:
        - symbol: Stock symbol
        - expiration_date: Optional specific expiration date (YYYY-MM-DD)
        """
        try:
            # Get ticker object
            ticker = yf.Ticker(symbol)
            time.sleep(self.rate_limit_delay)
            
            # Get all expiration dates if none specified
            if not expiration_date:
                exp_dates = ticker.options
                if not exp_dates:
                    return pd.DataFrame()
                expiration_date = exp_dates[0]  # Use nearest expiration
            
            # Get calls and puts
            options = ticker.option_chain(expiration_date)
            
            # Combine calls and puts
            calls = options.calls.copy()
            calls['option_type'] = 'CALL'
            puts = options.puts.copy()
            puts['option_type'] = 'PUT'
            
            # Combine and clean data
            df = pd.concat([calls, puts])
            
            # Rename columns to match our schema
            column_mapping = {
                'strike': 'strike_price',
                'bid': 'bid',
                'ask': 'ask',
                'volume': 'volume',
                'openInterest': 'open_interest',
                'impliedVolatility': 'implied_volatility'
            }
            
            df = df.rename(columns=column_mapping)
            
            # Calculate Greeks (Yahoo doesn't provide them directly)
            df = self._calculate_basic_greeks(df, ticker.info['regularMarketPrice'])
            
            # Add expiration date
            df['expiration_date'] = expiration_date
            
            return df
            
        except Exception as e:
            print(f"Error fetching options chain: {str(e)}")
            return pd.DataFrame()

    def _calculate_basic_greeks(self, df: pd.DataFrame, current_price: float) -> pd.DataFrame:
        """
        Calculate basic Greeks approximations
        Note: These are rough approximations. For accurate Greeks, 
        a proper options pricing model should be used.
        """
        risk_free_rate = 0.05  # Approximate risk-free rate
        
        df['delta'] = df.apply(
            lambda row: self._calculate_delta(
                current_price,
                row['strike_price'],
                row['implied_volatility'],
                row['option_type']
            ),
            axis=1
        )
        
        # Approximate other Greeks
        df['gamma'] = df.apply(
            lambda row: self._calculate_gamma(
                current_price,
                row['strike_price'],
                row['implied_volatility']
            ),
            axis=1
        )
        
        df['theta'] = df.apply(
            lambda row: self._calculate_theta(
                current_price,
                row['strike_price'],
                row['implied_volatility'],
                row['option_type']
            ),
            axis=1
        )
        
        df['vega'] = df.apply(
            lambda row: self._calculate_vega(
                current_price,
                row['strike_price'],
                row['implied_volatility']
            ),
            axis=1
        )
        
        return df

    def _calculate_delta(self, S: float, K: float, sigma: float, option_type: str) -> float:
        """Approximate delta using simple model"""
        if option_type == 'CALL':
            if S > K:
                return 0.7 + (S - K) / (S * sigma) * 0.3
            else:
                return 0.3 - (K - S) / (S * sigma) * 0.3
        else:
            if S > K:
                return -0.3 + (S - K) / (S * sigma) * 0.3
            else:
                return -0.7 - (K - S) / (S * sigma) * 0.3

    def _calculate_gamma(self, S: float, K: float, sigma: float) -> float:
        """Approximate gamma"""
        return 0.1 * np.exp(-(S - K)**2 / (2 * (S * sigma)**2))

    def _calculate_theta(self, S: float, K: float, sigma: float, option_type: str) -> float:
        """Approximate theta"""
        atm_factor = -S * sigma / np.sqrt(365)
        return atm_factor * np.exp(-(S - K)**2 / (2 * (S * sigma)**2))

    def _calculate_vega(self, S: float, K: float, sigma: float) -> float:
        """Approximate vega"""
        return S * np.exp(-(S - K)**2 / (2 * (S * sigma)**2)) / 100

    def get_historical_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """
        Get historical price data
        
        Parameters:
        - symbol: Stock symbol
        - period: Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        - interval: Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        """
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            time.sleep(self.rate_limit_delay)
            return df
        except Exception as e:
            print(f"Error fetching historical data: {str(e)}")
            return pd.DataFrame()

    def get_quote(self, symbol: str) -> Dict:
        """Get current quote and info for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            time.sleep(self.rate_limit_delay)
            return ticker.info
        except Exception as e:
            print(f"Error fetching quote: {str(e)}")
            return {}

class OptionsDataManager:
    def __init__(self):
        self.api = YahooOptionsAPI()
        
    def fetch_complete_data(self, symbol: str) -> Dict:
        """Fetch all relevant data for a symbol"""
        try:
            # Get current quote and info
            quote = self.api.get_quote(symbol)
            
            # Get options data for nearest expiration
            options_data = self.api.get_options_chain(symbol)
            
            # Get historical data
            historical_data = self.api.get_historical_data(symbol)
            
            # Calculate historical volatility
            if not historical_data.empty:
                returns = np.log(historical_data['Close'] / historical_data['Close'].shift(1))
                historical_volatility = returns.std() * np.sqrt(252)  # Annualized
            else:
                historical_volatility = None
            
            return {
                'quote': quote,
                'options_chain': options_data,
                'historical_data': historical_data,
                'historical_volatility': historical_volatility
            }
            
        except Exception as e:
            print(f"Error fetching complete data for {symbol}: {str(e)}")
            return None

    def get_iv_percentile(self, symbol: str, lookback_days: int = 252) -> float:
        """Calculate IV percentile using historical data"""
        try:
            # Get historical data
            historical = self.api.get_historical_data(symbol, period=f"{lookback_days}d")
            
            if historical.empty:
                return None
                
            # Calculate historical volatility for each window
            returns = np.log(historical['Close'] / historical['Close'].shift(1))
            rolling_vol = returns.rolling(window=30).std() * np.sqrt(252)
            
            # Calculate percentile of current volatility
            current_vol = rolling_vol.iloc[-1]
            percentile = (rolling_vol < current_vol).mean() * 100
            
            return percentile
            
        except Exception as e:
            print(f"Error calculating IV percentile: {str(e)}")
            return None
