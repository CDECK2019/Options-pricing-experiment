from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime, timedelta

@dataclass
class StrategyTemplate:
    name: str
    description: str
    filters: Dict
    risk_metrics: List[str]
    required_data: List[str]

class OptionsStrategyScreener:
    def __init__(self):
        self.templates = {
            "covered_call": StrategyTemplate(
                name="Covered Call Scanner",
                description="Find covered call opportunities with balanced premium and assignment risk",
                filters={
                    "option_type": "call",
                    "delta_range": (0.25, 0.35),  # Conservative delta range
                    "min_dte": 30,
                    "max_dte": 45,
                    "min_iv_percentile": 40,  # Look for elevated IV
                    "min_volume": 100,
                    "min_open_interest": 500,
                    "max_bid_ask_spread": 0.05,  # 5% max spread
                    "itm_otm": "OTM"  # Out of the money calls
                },
                risk_metrics=[
                    "static_return",
                    "assigned_return",
                    "annualized_return",
                    "break_even_price"
                ],
                required_data=["underlying_price", "dividend_dates"]
            ),
            
            "cash_secured_put": StrategyTemplate(
                name="Cash Secured Put Scanner",
                description="Find put-selling opportunities with good premium/risk ratio",
                filters={
                    "option_type": "put",
                    "delta_range": (0.2, 0.3),
                    "min_dte": 25,
                    "max_dte": 45,
                    "min_iv_rank": 50,  # Higher IV rank for better premiums
                    "min_volume": 100,
                    "support_distance": 0.05,  # 5% above technical support
                    "max_bid_ask_spread": 0.05
                },
                risk_metrics=[
                    "premium_to_cash_required",
                    "annualized_return",
                    "break_even_distance"
                ],
                required_data=["technical_levels", "earnings_dates"]
            ),
            
            "iron_condor": StrategyTemplate(
                name="Iron Condor Scanner",
                description="Find range-bound opportunities with high probability of profit",
                filters={
                    "min_iv_rank": 60,  # Higher IV for better premium
                    "call_wing_delta": (0.15, 0.20),
                    "put_wing_delta": (0.15, 0.20),
                    "min_dte": 25,
                    "max_dte": 45,
                    "min_wing_width": 0.02,  # Minimum spread between strikes
                    "max_bid_ask_spread": 0.05,
                    "min_credit": 0.20  # Minimum credit received
                },
                risk_metrics=[
                    "probability_of_profit",
                    "max_loss",
                    "risk_reward_ratio",
                    "potential_early_assignment"
                ],
                required_data=["historical_volatility", "earnings_dates"]
            ),
            
            "calendar_spread": StrategyTemplate(
                name="Calendar Spread Scanner",
                description="Find opportunities for time decay exploitation with minimal directional risk",
                filters={
                    "front_month_dte": (20, 30),
                    "back_month_dte": (45, 60),
                    "delta_range": (-0.05, 0.05),  # Near ATM
                    "min_iv_skew": 0.02,  # Minimum IV difference between months
                    "min_volume": 50,
                    "max_bid_ask_spread": 0.07,
                    "earnings_between": False  # No earnings between expiration dates
                },
                risk_metrics=[
                    "vega_risk",
                    "theta_decay_ratio",
                    "max_loss_estimate",
                    "optimal_exit_dte"
                ],
                required_data=["term_structure", "historical_vol_by_expiration"]
            ),
            
            "volatility_skew": StrategyTemplate(
                name="Volatility Skew Scanner",
                description="Find opportunities to exploit rich/cheap implied volatility",
                filters={
                    "min_dte": 30,
                    "max_dte": 60,
                    "min_volume": 100,
                    "min_iv_skew_percentile": 80,  # Looking for extreme skew
                    "min_put_call_ratio": 1.5,
                    "max_bid_ask_spread": 0.05
                },
                risk_metrics=[
                    "skew_zscore",
                    "historical_skew_comparison",
                    "put_call_ratio_percentile"
                ],
                required_data=["historical_skew", "put_call_ratios"]
            ),
            
            "earnings_volatility": StrategyTemplate(
                name="Earnings Volatility Scanner",
                description="Find opportunities around earnings announcements",
                filters={
                    "days_to_earnings": (1, 5),
                    "min_iv_rank": 70,
                    "min_historical_move": 0.05,  # 5% minimum historical earnings move
                    "min_volume": 200,
                    "max_bid_ask_spread": 0.05,
                    "market_cap_min": 1e9  # $1B minimum market cap
                },
                risk_metrics=[
                    "implied_move",
                    "historical_vs_implied_move",
                    "options_volume_surge",
                    "iv_crush_estimate"
                ],
                required_data=["earnings_history", "historical_iv_crush"]
            )
        }

    def get_template(self, strategy_name: str) -> Optional[StrategyTemplate]:
        """Retrieve a specific strategy template"""
        return self.templates.get(strategy_name)

    def apply_template(self, strategy_name: str, options_chain: pd.DataFrame) -> pd.DataFrame:
        """Apply a strategy template's filters to an options chain"""
        template = self.get_template(strategy_name)
        if not template:
            raise ValueError(f"Strategy template {strategy_name} not found")
            
        filtered_chain = options_chain.copy()
        
        # Apply basic filters
        for filter_name, filter_value in template.filters.items():
            if isinstance(filter_value, tuple):
                filtered_chain = filtered_chain[
                    (filtered_chain[filter_name] >= filter_value[0]) & 
                    (filtered_chain[filter_name] <= filter_value[1])
                ]
            else:
                filtered_chain = filtered_chain[filtered_chain[filter_name] == filter_value]
                
        # Calculate strategy-specific risk metrics
        for metric in template.risk_metrics:
            filtered_chain[metric] = self._calculate_risk_metric(metric, filtered_chain)
            
        return filtered_chain

    def _calculate_risk_metric(self, metric_name: str, data: pd.DataFrame) -> pd.Series:
        """Calculate specific risk metrics for a strategy"""
        # Implementation of various risk metric calculations
        pass
