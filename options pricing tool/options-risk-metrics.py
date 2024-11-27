import numpy as np
from scipy.stats import norm
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class RiskMetrics:
    probability_of_profit: float
    max_profit: float
    max_loss: float
    break_even_points: list
    risk_reward_ratio: float
    expected_value: float
    theta_per_day: float
    vega_exposure: float

class OptionsRiskCalculator:
    def __init__(self, risk_free_rate=0.05):
        self.risk_free_rate = risk_free_rate

    def calculate_all_metrics(self, strategy: str, positions: list, underlying_price: float,
                            days_to_expiration: int, volatility: float) -> RiskMetrics:
        """Calculate all risk metrics for a given strategy"""
        if strategy == "covered_call":
            return self._covered_call_metrics(positions[0], underlying_price, 
                                           days_to_expiration, volatility)
        elif strategy == "iron_condor":
            return self._iron_condor_metrics(positions, underlying_price, 
                                          days_to_expiration, volatility)
        # Add other strategies...

    def _covered_call_metrics(self, option, underlying_price: float, 
                            days_to_expiration: int, volatility: float) -> RiskMetrics:
        """Calculate risk metrics for covered call strategy"""
        strike = option['strike']
        premium = option['premium']
        
        # Calculate max profit/loss
        max_profit = (strike - underlying_price) + premium
        max_loss = underlying_price - premium
        
        # Calculate break-even point
        break_even = underlying_price - premium
        
        # Calculate probability of profit using Black-Scholes
        d1 = (np.log(underlying_price/strike) + 
              (self.risk_free_rate + 0.5 * volatility**2) * days_to_expiration/365) / \
             (volatility * np.sqrt(days_to_expiration/365))
        prob_profit = 1 - norm.cdf(d1)
        
        # Calculate theta decay
        theta = self._calculate_theta(underlying_price, strike, days_to_expiration, 
                                    volatility, option['type'])
        
        # Calculate vega exposure
        vega = self._calculate_vega(underlying_price, strike, days_to_expiration, 
                                  volatility)
        
        return RiskMetrics(
            probability_of_profit=prob_profit,
            max_profit=max_profit,
            max_loss=max_loss,
            break_even_points=[break_even],
            risk_reward_ratio=abs(max_profit/max_loss),
            expected_value=max_profit * prob_profit - max_loss * (1-prob_profit),
            theta_per_day=theta,
            vega_exposure=vega
        )

    def _iron_condor_metrics(self, positions: list, underlying_price: float,
                           days_to_expiration: int, volatility: float) -> RiskMetrics:
        """Calculate risk metrics for iron condor strategy"""
        # Extract strikes and premiums
        long_put = positions[0]
        short_put = positions[1]
        short_call = positions[2]
        long_call = positions[3]
        
        # Calculate max profit (net credit received)
        net_credit = (short_put['premium'] + short_call['premium'] - 
                     long_put['premium'] - long_call['premium'])
        max_profit = net_credit
        
        # Calculate max loss
        put_spread = short_put['strike'] - long_put['strike']
        call_spread = long_call['strike'] - short_call['strike']
        max_loss = max(put_spread, call_spread) - net_credit
        
        # Calculate break-even points
        be_lower = short_put['strike'] - net_credit
        be_upper = short_call['strike'] + net_credit
        
        # Calculate probability of profit
        prob_below_upper = norm.cdf(
            (np.log(be_upper/underlying_price) - 
             (self.risk_free_rate - 0.5 * volatility**2) * days_to_expiration/365) / \
            (volatility * np.sqrt(days_to_expiration/365))
        )
        prob_above_lower = 1 - norm.cdf(
            (np.log(be_lower/underlying_price) - 
             (self.risk_free_rate - 0.5 * volatility**2) * days_to_expiration/365) / \
            (volatility * np.sqrt(days_to_expiration/365))
        )
        prob_profit = prob_below_upper - (1 - prob_above_lower)
        
        # Calculate total theta
        total_theta = sum(self._calculate_theta(underlying_price, pos['strike'], 
                                              days_to_expiration, volatility, pos['type']) 
                         for pos in positions)
        
        # Calculate total vega
        total_vega = sum(self._calculate_vega(underlying_price, pos['strike'], 
                                            days_to_expiration, volatility) 
                        for pos in positions)
        
        return RiskMetrics(
            probability_of_profit=prob_profit,
            max_profit=max_profit,
            max_loss=max_loss,
            break_even_points=[be_lower, be_upper],
            risk_reward_ratio=abs(max_profit/max_loss),
            expected_value=max_profit * prob_profit - max_loss * (1-prob_profit),
            theta_per_day=total_theta,
            vega_exposure=total_vega
        )

    def _calculate_theta(self, S: float, K: float, T: int, sigma: float, 
                        option_type: str) -> float:
        """Calculate theta for an option position"""
        T = T / 365.0  # Convert days to years
        d1 = (np.log(S/K) + (self.risk_free_rate + 0.5 * sigma**2) * T) / \
             (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        theta = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) - \
                self.risk_free_rate * K * np.exp(-self.risk_free_rate * T) * norm.cdf(d2)
                
        if option_type.lower() == 'put':
            theta = theta + self.risk_free_rate * K * np.exp(-self.risk_free_rate * T)
            
        return theta

    def _calculate_vega(self, S: float, K: float, T: int, sigma: float) -> float:
        """Calculate vega for an option position"""
        T = T / 365.0  # Convert days to years
        d1 = (np.log(S/K) + (self.risk_free_rate + 0.5 * sigma**2) * T) / \
             (sigma * np.sqrt(T))
        
        vega = S * np.sqrt(T) * norm.pdf(d1)
        return vega / 100  # Convert to 1% move in volatility
