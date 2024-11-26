import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ScreenerResults:
    symbol: str
    strategy_matches: List[Dict]
    risk_metrics: Dict
    underlying_data: Dict

class IntegratedOptionsScreener:
    def __init__(self):
        self.data_manager = YahooOptionsAPI()
        
    def screen_for_strategies(self, symbol: str) -> ScreenerResults:
        """
        Screen options chain for potential strategies
        """
        # Fetch all necessary data
        try:
            # Get current data
            ticker = yf.Ticker(symbol)
            current_price = ticker.info['regularMarketPrice']
            options_chain = self.data_manager.get_options_chain(symbol)
            
            if options_chain.empty:
                raise ValueError(f"No options data available for {symbol}")

            # Screen for different strategies
            strategies = []
            
            # Screen for covered calls
            covered_calls = self._screen_covered_calls(
                options_chain, current_price)
            if covered_calls:
                strategies.extend(covered_calls)
            
            # Screen for cash-secured puts
            csps = self._screen_cash_secured_puts(
                options_chain, current_price)
            if csps:
                strategies.extend(csps)
                
            # Calculate risk metrics
            risk_metrics = self._calculate_risk_metrics(
                options_chain, current_price)
            
            # Get underlying data
            underlying_data = {
                'price': current_price,
                'volume': ticker.info.get('volume'),
                'market_cap': ticker.info.get('marketCap'),
                'beta': ticker.info.get('beta')
            }
            
            return ScreenerResults(
                symbol=symbol,
                strategy_matches=strategies,
                risk_metrics=risk_metrics,
                underlying_data=underlying_data
            )
            
        except Exception as e:
            print(f"Error screening {symbol}: {str(e)}")
            return None

    def _screen_covered_calls(self, 
                            chain: pd.DataFrame, 
                            current_price: float) -> List[Dict]:
        """Screen for covered call opportunities"""
        covered_calls = []
        
        # Filter for calls only
        calls = chain[
            (chain['option_type'] == 'CALL') & 
            (chain['strike_price'] >= current_price) &  # OTM calls
            (chain['volume'] > 100) &  # Minimum volume
            (chain['open_interest'] > 500)  # Minimum open interest
        ]
        
        for _, option in calls.iterrows():
            # Calculate metrics
            premium = (option['bid'] + option['ask']) / 2
            static_return = (premium / current_price) * 100
            max_return = ((option['strike_price'] - current_price + premium) / 
                         current_price) * 100
            
            if static_return >= 0.5:  # Minimum 0.5% premium
                covered_calls.append({
                    'strategy': 'Covered Call',
                    'strike': option['strike_price'],
                    'expiration': option['expiration_date'],
                    'premium': premium,
                    'static_return': static_return,
                    'max_return': max_return,
                    'implied_volatility': option['implied_volatility'],
                    'volume': option['volume'],
                    'open_interest': option['open_interest']
                })
        
        return covered_calls

    def _screen_cash_secured_puts(self, 
                                chain: pd.DataFrame, 
                                current_price: float) -> List[Dict]:
        """Screen for cash-secured put opportunities"""
        csps = []
        
        # Filter for puts only
        puts = chain[
            (chain['option_type'] == 'PUT') & 
            (chain['strike_price'] <= current_price) &  # OTM puts
            (chain['volume'] > 100) & 
            (chain['open_interest'] > 500)
        ]
        
        for _, option in puts.iterrows():
            premium = (option['bid'] + option['ask']) / 2
            static_return = (premium / option['strike_price']) * 100
            
            if static_return >= 0.3:  # Minimum 0.3% premium
                csps.append({
                    'strategy': 'Cash-Secured Put',
                    'strike': option['strike_price'],
                    'expiration': option['expiration_date'],
                    'premium': premium,
                    'static_return': static_return,
                    'break_even': option['strike_price'] - premium,
                    'implied_volatility': option['implied_volatility'],
                    'volume': option['volume'],
                    'open_interest': option['open_interest']
                })
        
        return csps

    def _calculate_risk_metrics(self, 
                              chain: pd.DataFrame, 
                              current_price: float) -> Dict:
        """Calculate overall risk metrics"""
        return {
            'avg_iv': chain['implied_volatility'].mean(),
            'iv_skew': self._calculate_iv_skew(chain),
            'put_call_ratio': self._calculate_put_call_ratio(chain),
            'atm_options': self._find_atm_options(chain, current_price)
        }

    def _calculate_iv_skew(self, chain: pd.DataFrame) -> float:
        """Calculate IV skew (difference between put and call IV)"""
        atm_calls = chain[
            (chain['option_type'] == 'CALL') & 
            (chain['implied_volatility'] > 0)
        ]['implied_volatility'].mean()
        
        atm_puts = chain[
            (chain['option_type'] == 'PUT') & 
            (chain['implied_volatility'] > 0)
        ]['implied_volatility'].mean()
        
        return atm_puts - atm_calls

    def _calculate_put_call_ratio(self, chain: pd.DataFrame) -> float:
        """Calculate put/call ratio based on volume"""
        put_volume = chain[chain['option_type'] == 'PUT']['volume'].sum()
        call_volume = chain[chain['option_type'] == 'CALL']['volume'].sum()
        
        if call_volume == 0:
            return 0
        return put_volume / call_volume

    def _find_atm_options(self, 
                         chain: pd.DataFrame, 
                         current_price: float) -> Dict:
        """Find at-the-money options"""
        atm_threshold = current_price * 0.02  # 2% range
        
        atm_options = chain[
            (abs(chain['strike_price'] - current_price) <= atm_threshold)
        ]
        
        if atm_options.empty:
            return {}
            
        return {
            'call': atm_options[atm_options['option_type'] == 'CALL'].iloc[0].to_dict(),
            'put': atm_options[atm_options['option_type'] == 'PUT'].iloc[0].to_dict()
        }

# Example usage
screener = IntegratedOptionsScreener()
results = screener.screen_for_strategies('AAPL')
