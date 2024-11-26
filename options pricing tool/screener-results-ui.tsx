import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

const ScreenerResults = ({ symbol }) => {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Example data structure matching our Python screener output
  const mockResults = {
    symbol: symbol,
    strategy_matches: [
      {
        strategy: 'Covered Call',
        strike: 175.0,
        expiration: '2024-02-16',
        premium: 3.45,
        static_return: 2.1,
        implied_volatility: 0.25,
        volume: 1500,
        open_interest: 2500
      },
      {
        strategy: 'Cash-Secured Put',
        strike: 165.0,
        expiration: '2024-02-16',
        premium: 2.80,
        static_return: 1.8,
        implied_volatility: 0.28,
        volume: 1200,
        open_interest: 2200
      }
    ],
    risk_metrics: {
      avg_iv: 0.27,
      iv_skew: 0.03,
      put_call_ratio: 0.85
    },
    underlying_data: {
      price: 170.50,
      volume: 45000000,
      market_cap: 2800000000000,
      beta: 1.2
    }
  };

  const fetchResults = async (symbol) => {
    setLoading(true);
    setError(null);
    try {
      // In a real implementation, this would be an API call
      // await fetch(`/api/screen/${symbol}`)
      
      // Using mock data for demonstration
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API delay
      setResults(mockResults);
    } catch (err) {
      setError('Failed to fetch screening results');
      console.error('Error fetching results:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (symbol) {
      fetchResults(symbol);
    }
  }, [symbol]);

  const renderStrategyResults = (strategies) => (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {strategies.map((strategy, index) => (
        <Card key={index}>
          <CardContent className="p-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-bold">{strategy.strategy}</h3>
              <span className={`font-medium ${
                strategy.static_return >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {strategy.static_return.toFixed(2)}% Return
              </span>
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Strike:</span>
                <span className="font-medium">${strategy.strike.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Premium:</span>
                <span className="font-medium">${strategy.premium.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Expiration:</span>
                <span className="font-medium">{strategy.expiration}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">IV:</span>
                <span className="font-medium">
                  {(strategy.implied_volatility * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Volume:</span>
                <span className="font-medium">
                  {strategy.volume.toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Open Interest:</span>
                <span className="font-medium">
                  {strategy.open_interest.toLocaleString()}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );

  const renderRiskMetrics = (metrics) => (
    <Card>
      <CardHeader>
        <CardTitle>Risk Metrics</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Average IV:</span>
              <span className="font-medium">
                {(metrics.avg_iv * 100).toFixed(1)}%
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">IV Skew:</span>
              <span className="font-medium">
                {(metrics.iv_skew * 100).toFixed(1)}%
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Put/Call Ratio:</span>
              <span className="font-medium">
                {metrics.put_call_ratio.toFixed(2)}
              </span>
            </div>
          </div>
          
          <Card className="bg-gray-50">
            <CardContent className="p-4">
              <h4 className="font-medium mb-2">Market Overview</h4>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span>Price:</span>
                  <span>${results.underlying_data.price.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Volume:</span>
                  <span>{results.underlying_data.volume.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span>Beta:</span>
                  <span>{results.underlying_data.beta.toFixed(2)}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <span className="text-lg">Loading results for {symbol}...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-64">
        <span className="text-lg text-red-600">{error}</span>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="flex justify-center items-center h-64">
        <span className="text-lg">No results found for {symbol}</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>{symbol} Analysis Results</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <div className="flex items-center space-x-4">
              <span className="text-xl font-medium">
                ${results.underlying_data.price.toFixed(2)}
              </span>
              <span className="text-sm text-gray-500">
                Market Cap: ${(results.underlying_data.market_cap / 1e9).toFixed(1)}B
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="strategies">
        <TabsList className="w-full">
          <TabsTrigger value="strategies" className="flex-1">Strategy Matches</TabsTrigger>
          <TabsTrigger value="risk" className="flex-1">Risk Analysis</TabsTrigger>
        </TabsList>
        
        <TabsContent value="strategies">
          {renderStrategyResults(results.strategy_matches)}
        </TabsContent>
        
        <TabsContent value="risk">
          {renderRiskMetrics(results.risk_metrics)}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ScreenerResults;
