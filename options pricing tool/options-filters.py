from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np

@dataclass
class FilterParameters:
    min_volume: int = 0
    min_open_interest: int = 0
    min_iv: float = 0
    max_iv: float = float('inf')
    min_delta: float = float('-inf')
    max_delta: float = float('inf')
    min_strike_ratio: float = 0
    max_strike_ratio: float = float('inf')
    min_dte: int = 0
    max_dte: int = float('inf')
    max_spread_percent: float = float('inf')

class OptionsFilters:
    @staticmethod
    def filter_by_liquidity(options_df, min_volume=100, min_open_interest=500):
        """Filter options based on volume and open interest thresholds"""
        mask = (options_df['volume'] >= min_volume) & \
               (options_df['open_interest'] >= min_open_interest)
        return options_df[mask]

    @staticmethod
    def filter_by_moneyness(options_df, min_strike_ratio=0.8, max_strike_ratio=1.2):
        """Filter options based on strike price relative to underlying price"""
        strike_ratio = options_df['strike_price'] / options_df['underlying_price']
        mask = (strike_ratio >= min_strike_ratio) & (strike_ratio <= max_strike_ratio)
        return options_df[mask]

    @staticmethod
    def filter_by_greeks(options_df, min_delta=-1, max_delta=1, 
                        min_gamma=0, max_gamma=float('inf'),
                        min_theta=float('-inf'), max_theta=0):
        """Filter options based on Greeks thresholds"""
        mask = (options_df['delta'] >= min_delta) & (options_df['delta'] <= max_delta) & \
               (options_df['gamma'] >= min_gamma) & (options_df['gamma'] <= max_gamma) & \
               (options_df['theta'] >= min_theta) & (options_df['theta'] <= max_theta)
        return options_df[mask]

    @staticmethod
    def filter_by_volatility(options_df, min_iv=0.1, max_iv=2.0, 
                           min_hv_ratio=0.8, max_hv_ratio=1.2):
        """Filter options based on implied volatility and historical volatility ratio"""
        iv_mask = (options_df['implied_volatility'] >= min_iv) & \
                 (options_df['implied_volatility'] <= max_iv)
        
        # Calculate IV/HV ratio
        iv_hv_ratio = options_df['implied_volatility'] / options_df['historical_volatility_30d']
        hv_mask = (iv_hv_ratio >= min_hv_ratio) & (iv_hv_ratio <= max_hv_ratio)
        
        return options_df[iv_mask & hv_mask]

    @staticmethod
    def filter_by_spread(options_df, max_spread_percent=0.05):
        """Filter options based on bid-ask spread percentage"""
        spread_pct = (options_df['ask'] - options_df['bid']) / options_df['underlying_price']
        return options_df[spread_pct <= max_spread_percent]

    @staticmethod
    def filter_by_expiration(options_df, min_dte=7, max_dte=45):
        """Filter options based on days till expiration"""
        now = datetime.now()
        dte = (options_df['expiration_date'] - now).dt.days
        mask = (dte >= min_dte) & (dte <= max_dte)
        return options_df[mask]

    @staticmethod
    def apply_all_filters(options_df, params: FilterParameters):
        """Apply all filters with given parameters"""
        filtered_df = options_df.copy()
        
        filtered_df = OptionsFilters.filter_by_liquidity(
            filtered_df, params.min_volume, params.min_open_interest)
        
        filtered_df = OptionsFilters.filter_by_moneyness(
            filtered_df, params.min_strike_ratio, params.max_strike_ratio)
        
        filtered_df = OptionsFilters.filter_by_greeks(
            filtered_df, params.min_delta, params.max_delta)
        
        filtered_df = OptionsFilters.filter_by_volatility(
            filtered_df, params.min_iv, params.max_iv)
        
        filtered_df = OptionsFilters.filter_by_spread(
            filtered_df, params.max_spread_percent)
        
        filtered_df = OptionsFilters.filter_by_expiration(
            filtered_df, params.min_dte, params.max_dte)
        
        return filtered_df
