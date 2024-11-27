import numpy as np
from scipy.stats import norm
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleScenarioAnalyzer:
    def __init__(self, risk_free_rate=0.05):
        self.risk_free_rate = risk_free_rate
    
    def black_scholes(self, S, K, T, r, sigma, option_type='call'):
        """
        Calculate option price using Black-Scholes formula
        
        Args:
            S: Current stock price
            K: Strike price
            T: Time to expiration in years
            r: Risk-free rate
            sigma: Implied volatility
            option_type: 'call' or 'put'
        """
        try:
            if T <= 0:
                # For expired options, calculate intrinsic value
                if option_type == 'call':
                    return max(S - K, 0)
                else:
                    return max(K - S, 0)
            
            d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
            d2 = d1 - sigma*np.sqrt(T)
            
            if option_type == 'call':
                price = S*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)
            else:  # put
                price = K*np.exp(-r*T)*norm.cdf(-d2) - S*norm.cdf(-d1)
            
            return max(price, 0)  # Option price cannot be negative
            
        except Exception as e:
            logger.error(f"Error in Black-Scholes calculation: {str(e)}")
            return 0

    def calculate_profit_potential(self, current_price, new_stock_price, option_data):
        """Calculate the profit potential for an option given a new stock price"""
        try:
            # Extract option data
            strike = option_data['strike']
            expiration = option_data['expiration']
            implied_vol = option_data['implied_volatility']
            current_option_price = option_data['current_option_price']
            option_type = option_data['option_type']
            
            # Calculate new theoretical option price
            new_option_price = self.black_scholes(
                S=new_stock_price,
                K=strike,
                T=expiration,
                r=self.risk_free_rate,
                sigma=implied_vol,
                option_type=option_type
            )
            
            # Calculate percent change in option value
            if current_option_price > 0:
                percent_change = ((new_option_price - current_option_price) / current_option_price) * 100
            else:
                percent_change = 0
            
            return {
                "new_option_price": new_option_price,
                "percent_change": percent_change
            }
            
        except Exception as e:
            logger.error(f"Error calculating profit potential: {str(e)}")
            return None
