import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, AreaChart, Area } from 'recharts';

const calculateProfit = (price, metrics) => {
  const positions = metrics.positions || [];
  let totalProfit = 0;

  positions.forEach(position => {
    if (position.type === 'call') {
      totalProfit += Math.max(0, price - position.strike) - position.premium;
    } else if (position.type === 'put') {
      totalProfit += Math.max(0, position.strike - price) - position.premium;
    } else if (position.type === 'stock') {
      totalProfit += price - position.entryPrice;
    }
  });

  return totalProfit;
};

const RiskVisualization = ({ strategyMetrics, underlyingPrice }) => {
  const [selectedView, setSelectedView] = useState('pnl');

  // Generate P/L curve data points
  const generatePnLCurve = () => {
    if (!underlyingPrice || !strategyMetrics) {
      return [];
    }

    const priceRange = Array.from({ length: 50 }, (_, i) => 
      underlyingPrice * (0.7 + i * 0.02));
    
    return priceRange.map(price => ({
      price: parseFloat(price.toFixed(2)),
      profit: parseFloat(calculateProfit(price, strategyMetrics).toFixed(2)),
      var: parseFloat((strategyMetrics.valueAtRisk || 0).toFixed(2)),
      expectedShortfall: parseFloat((strategyMetrics.expectedShortfall || 0).toFixed(2))
    }));
  };

  const renderPnLChart = () => (
    <Card>
      <CardHeader>
        <CardTitle>Position P/L Profile</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-64">
          <AreaChart width={600} height={240} data={generatePnLCurve()}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="price" />
            <YAxis />
            <Tooltip 
              formatter={(value) => `$${value}`}
              labelFormatter={(value) => `Price: $${value}`}
            />
            <Legend />
            <Area 
              type="monotone" 
              dataKey="profit" 
              name="P/L"
              stroke="#8884d8" 
              fill="#8884d8" 
              fillOpacity={0.3} 
            />
            <Line 
              type="monotone" 
              dataKey="var" 
              name="VaR"
              stroke="#ff0000" 
              strokeDasharray="5 5" 
            />
            <Line 
              type="monotone" 
              dataKey="expectedShortfall" 
              name="Expected Shortfall"
              stroke="#ff7300" 
              strokeDasharray="5 5" 
            />
          </AreaChart>
        </div>
      </CardContent>
    </Card>
  );

  const renderGreeksChart = () => (
    <Card>
      <CardHeader>
        <CardTitle>Greeks Exposure</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-64">
          <LineChart 
            width={600} 
            height={240} 
            data={strategyMetrics?.greeksExposure || []}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="price" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" name="Delta" dataKey="delta" stroke="#8884d8" />
            <Line type="monotone" name="Gamma" dataKey="gamma" stroke="#82ca9d" />
            <Line type="monotone" name="Theta" dataKey="theta" stroke="#ffc658" />
          </LineChart>
        </div>
      </CardContent>
    </Card>
  );

  const renderRiskMetrics = () => (
    <Card>
      <CardHeader>
        <CardTitle>Risk Metrics</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="font-medium">Value at Risk (95%):</span>
              <span>${(strategyMetrics?.valueAtRisk || 0).toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium">Expected Shortfall:</span>
              <span>${(strategyMetrics?.expectedShortfall || 0).toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium">Kelly Position Size:</span>
              <span>{(strategyMetrics?.kellyCriterion || 0).toFixed(2)} contracts</span>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="font-medium">Optimal Profit Target:</span>
              <span>${(strategyMetrics?.optimalExits?.profit_target || 0).toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium">Recommended Stop Loss:</span>
              <span>${(strategyMetrics?.optimalExits?.stop_loss || 0).toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium">Time-Based Exit:</span>
              <span>{strategyMetrics?.optimalExits?.time_exit_days || 0} days</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-6">
      {renderPnLChart()}
      {renderGreeksChart()}
      {renderRiskMetrics()}
    </div>
  );
};

export default RiskVisualization;
