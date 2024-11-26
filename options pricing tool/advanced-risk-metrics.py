import numpy as np
from scipy.stats import norm
from dataclasses import dataclass
from typing import Dict, List, Tuple
import pandas as pd

@dataclass
class AdvancedRiskMetrics:
    value_at_risk: float
    expected_shortfall: float
    optimal_exit_points: Dict[str, float]
    position_size: Dict[str, float]
    kelly_criterion: float
    risk_adjusted_return: float
    gamma_exposure: float
    vanna_exposure: float
    charm_exposure: float

class AdvancedRiskCalculator:
    def __init__(self, account_size: float, risk_free_rate: float = 0.05):
        self.account_size = account_size
        self.risk_free_rate = risk_free_rate
        
    def calculate_advanced_metrics(
        self,
        strategy: str,
        positions: list,
        underlying_price: float,
        volatility: float,
        historical_prices: pd.DataFrame
    ) -> AdvancedRiskMetrics:
        """Calculate comprehensive risk metrics for position sizing and management"""
        
        # Calculate Value at Risk (VaR) using historical simulation
        var_95 = self._calculate_var(positions, historical_prices, confidence_level=0.95)
        
        # Calculate Expected Shortfall (Conditional VaR)
        expected_shortfall = self._calculate_expected_shortfall(positions, historical_prices)
        
        # Calculate optimal position size using Kelly Criterion
        kelly_size = self._calculate_kelly_criterion(positions, historical_prices)
        
        # Calculate optimal exit points based on Greeks and time decay
        exit_points = self._calculate_optimal_exits(positions, underlying_price, volatility)
        
        # Calculate position size recommendations
        position_size = self._calculate_position_size(
            var_95, kelly_size, strategy, underlying_price
        )
        
        # Calculate higher-order Greeks
        greeks = self._calculate_higher_order_greeks(
            positions, underlying_price, volatility
        )
        
        return AdvancedRiskMetrics(
            value_at_risk=var_95,
            expected_shortfall=expected_shortfall,
            optimal_exit_points=exit_points,
            position_size=position_size,
            kelly_criterion=kelly_size,
            risk_adjusted_return=self._calculate_risk_adjusted_return(positions),
            gamma_exposure=greeks['gamma'],
            vanna_exposure=greeks['vanna'],
            charm_exposure=greeks['charm']
        )

    def _calculate_var(
        self,
        positions: list,
        historical_prices: pd.DataFrame,
        confidence_level: float
    ) -> float:
        """Calculate Value at Risk using historical simulation"""
        position_values = []
        for price in historical_prices['close']:
            total_value = sum(self._calculate_position_value(pos, price) 
                            for pos in positions)
            position_values.append(total_value)
            
        return np.percentile(position_values, (1 - confidence_level) * 100)

    def _calculate_expected_shortfall(
        self,
        positions: list,
        historical_prices: pd.DataFrame
    ) -> float:
        """Calculate Expected Shortfall (Conditional VaR)"""
        var_95 = self._calculate_var(positions, historical_prices, 0.95)
        position_values = []
        for price in historical_prices['close']:
            total_value = sum(self._calculate_position_value(pos, price) 
                            for pos in positions)
            if total_value < var_95:
                position_values.append(total_value)
                
        return np.mean(position_values) if position_values else var_95

    def _calculate_kelly_criterion(
        self,
        positions: list,
        historical_prices: pd.DataFrame
    ) -> float:
        """Calculate Kelly Criterion for optimal position sizing"""
        returns = []
        for i in range(1, len(historical_prices)):
            prev_value = sum(self._calculate_position_value(pos, historical_prices['close'][i-1]) 
                           for pos in positions)
            curr_value = sum(self._calculate_position_value(pos, historical_prices['close'][i]) 
                           for pos in positions)
            returns.append((curr_value - prev_value) / prev_value)
            
        win_prob = len([r for r in returns if r > 0]) / len(returns)
        avg_win = np.mean([r for r in returns if r > 0]) if any(r > 0 for r in returns) else 0
        avg_loss = abs(np.mean([r for r in returns if r < 0])) if any(r < 0 for r in returns) else 0
        
        if avg_loss == 0:
            return 0
            
        return (win_prob / avg_loss) - ((1 - win_prob) / avg_win)

    def _calculate_optimal_exits(
        self,
        positions: list,
        underlying_price: float,
        volatility: float
    ) -> Dict[str, float]:
        """Calculate optimal exit points based on Greeks and time decay"""
        exits = {}
        
        # Profit target based on probability analysis
        total_premium = sum(pos['premium'] for pos in positions)
        exits['profit_target'] = total_premium * 0.75  # Take profit at 75% of max profit
        
        # Stop loss based on VaR
        exits['stop_loss'] = self._calculate_var(positions, pd.DataFrame(), 0.99)
        
        # Time-based exit using theta decay
        total_theta = sum(self._calculate_theta(pos, underlying_price, volatility) 
                         for pos in positions)
        exits['time_exit_days'] = int(-total_premium / (2 * total_theta))  # Exit when theta decay accelerates
        
        # Volatility-based exit
        vega_exposure = sum(self._calculate_vega(pos, underlying_price, volatility) 
                           for pos in positions)
        exits['vol_exit_up'] = volatility * 1.2 if vega_exposure > 0 else volatility * 0.8
        exits['vol_exit_down'] = volatility * 0.8 if vega_exposure > 0 else volatility * 1.2
        
        return exits

    def _calculate_higher_order_greeks(
        self,
        positions: list,
        underlying_price: float,
        volatility: float
    ) -> Dict[str, float]:
        """Calculate higher-order Greeks for advanced risk management"""
        greeks = {'gamma': 0.0, 'vanna': 0.0, 'charm': 0.0}
        
        for pos in positions:
            # Gamma calculation (rate of change of delta)
            d1 = self._calculate_d1(pos, underlying_price, volatility)
            gamma = self._calculate_gamma(pos, underlying_price, volatility, d1)
            greeks['gamma'] += gamma
            
            # Vanna calculation (delta sensitivity to volatility)
            vanna = self._calculate_vanna(pos, underlying_price, volatility, d1)
            greeks['vanna'] += vanna
            
            # Charm calculation (delta sensitivity to time)
            charm = self._calculate_charm(pos, underlying_price, volatility, d1)
            greeks['charm'] += charm
            
        return greeks

    def _calculate_position_size(
        self,
        var_95: float,
        kelly_size: float,
        strategy: str,
        underlying_price: float
    ) -> Dict[str, float]:
        """Calculate recommended position size based on multiple factors"""
        # Base position size on account risk tolerance (1% risk per trade)
        risk_based_size = self.account_size * 0.01 / abs(var_95)
        
        # Adjust Kelly criterion to be more conservative
        conservative_kelly = kelly_size * 0.5
        
        # Consider strategy-specific factors
        strategy_multiplier = {
            'covered_call': 1.0,
            'iron_condor': 0.8,  # More conservative due to undefined risk
            'calendar_spread': 0.7,  # More complex, require smaller size
            'naked_puts': 0.5,  # Undefined risk requires smaller size
        }.get(strategy, 0.5)
        
        # Calculate final position size recommendations
        return {
            'risk_based_contracts': int(risk_based_size),
            'kelly_based_contracts': int(conservative_kelly * risk_based_size),
            'final_recommendation': int(min(risk_based_size, 
                                         conservative_kelly * risk_based_size) * strategy_multiplier),
            'max_capital_usage': underlying_price * int(risk_based_size) * strategy_multiplier,
            'risk_per_contract': var_95
        }

    def _calculate_risk_adjusted_return(self, positions: list) -> float:
        """Calculate risk-adjusted return metrics (Sharpe-like ratio for options)"""
        # Implementation specific to options positions
        pass
