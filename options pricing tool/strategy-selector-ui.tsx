import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

const StrategySelector = () => {
  const [selectedStrategy, setSelectedStrategy] = useState('covered_call');
  const [customFilters, setCustomFilters] = useState({});
  const [riskMetrics, setRiskMetrics] = useState(null);
  
  const strategyConfigs = {
    covered_call: {
      name: 'Covered Call',
      description: 'Conservative income strategy',
      defaultFilters: {
        delta: 0.30,
        daysToExpiration: 45,
        ivPercentile: 50
      }
    },
    iron_condor: {
      name: 'Iron Condor',
      description: 'Neutral range-bound strategy',
      defaultFilters: {
        wingDelta: 0.16,
        daysToExpiration: 45,
        ivRank: 50
      }
    }
  };

  return (
    <div className="p-4 max-w-7xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Strategy Selection</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            {Object.entries(strategyConfigs).map(([key, config]) => (
              <div 
                key={key}
                className={`p-4 border rounded-lg cursor-pointer ${
                  selectedStrategy === key ? 'border-blue-500 bg-blue-50' : ''
                }`}
                onClick={() => setSelectedStrategy(key)}
              >
                <h3 className="font-bold">{config.name}</h3>
                <p className="text-sm text-gray-600">{config.description}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Strategy Parameters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {selectedStrategy === 'covered_call' && (
              <>
                <div>
                  <label className="block text-sm font-medium mb-2">Target Delta</label>
                  <Slider 
                    defaultValue={[30]}
                    min={10}
                    max={50}
                    step={1}
                    onValueChange={(value) => 
                      setCustomFilters(prev => ({...prev, delta: value[0] / 100}))
                    }
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Days to Expiration</label>
                  <Slider 
                    defaultValue={[45]}
                    min={7}
                    max={120}
                    step={1}
                    onValueChange={(value) => 
                      setCustomFilters(prev => ({...prev, dte: value[0]}))
                    }
                  />
                </div>
              </>
            )}
            
            {selectedStrategy === 'iron_condor' && (
              <>
                <div>
                  <label className="block text-sm font-medium mb-2">Wing Delta</label>
                  <Slider 
                    defaultValue={[16]}
                    min={10}
                    max={30}
                    step={1}
                    onValueChange={(value) => 
                      setCustomFilters(prev => ({...prev, wingDelta: value[0] / 100}))
                    }
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Width (Points)</label>
                  <Slider 
                    defaultValue={[5]}
                    min={1}
                    max={20}
                    step={1}
                    onValueChange={(value) => 
                      setCustomFilters(prev => ({...prev, width: value[0]}))
                    }
                  />
                </div>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {riskMetrics && (
        <Card>
          <CardHeader>
            <CardTitle>Risk Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <div>
                  <span className="font-medium">Probability of Profit:</span>
                  <span className="ml-2">{(riskMetrics.pop * 100).toFixed(1)}%</span>
                </div>
                <div>
                  <span className="font-medium">Max Profit:</span>
                  <span className="ml-2">${riskMetrics.maxProfit.toFixed(2)}</span>
                </div>
                <div>
                  <span className="font-medium">Max Loss:</span>
                  <span className="ml-2">${riskMetrics.maxLoss.toFixed(2)}</span>
                </div>
              </div>
              <div className="h-40">
                <LineChart width={300} height={160} data={riskMetrics.profitCurve}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="price" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="profit" stroke="#8884d8" />
                </LineChart>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default StrategySelector;
