import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { AlertCircle, TrendingUp, TrendingDown, Clock } from 'lucide-react';

const PositionMonitor = ({ 
  positions = [], 
  alerts = [] 
}) => {
  if (!positions.length) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Active Positions Monitor</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-gray-500 py-8">
            No active positions to display
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Active Positions Monitor</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {positions.map((position, index) => (
              <Card key={index} className="bg-white">
                <CardContent className="p-4">
                  <div className="flex justify-between items-center mb-4">
                    <div className="font-bold">{position.symbol || 'Unknown'}</div>
                    <div className={`px-2 py-1 rounded ${
                      (position.pnl || 0) >= 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {(position.pnl || 0) >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                      ${Math.abs(position.pnl || 0).toFixed(2)}
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Strategy:</span>
                      <span className="font-medium">{position.strategy || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Days to Expiry:</span>
                      <span className="font-medium">{position.dte || 0}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Current IV:</span>
                      <span className="font-medium">{((position.currentIv || 0) * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Theta:</span>
                      <span className="font-medium">${(position.theta || 0).toFixed(2)}/day</span>
                    </div>
                  </div>

                  {position.alerts?.length > 0 && (
                    <div className="mt-4 p-2 bg-yellow-50 rounded">
                      <div className="flex items-center text-yellow-800">
                        <AlertCircle className="w-4 h-4 mr-2" />
                        <span className="text-sm">{position.alerts[0]}</span>
                      </div>
                    </div>
                  )}

                  <div className="mt-4 h-1 bg-gray-200 rounded">
                    <div 
                      className="h-1 bg-blue-500 rounded"
                      style={{ 
                        width: `${((position.daysHeld || 0) / (position.totalDays || 1)) * 100}%` 
                      }}
                    />
                  </div>
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Entry</span>
                    <span>Target Exit</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {alerts.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Position Alerts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {alerts.map((alert, index) => (
                <div 
                  key={index}
                  className={`p-3 rounded flex items-center ${
                    alert.severity === 'high' ? 'bg-red-100 text-red-800' :
                    alert.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-blue-100 text-blue-800'
                  }`}
                >
                  <Clock className="w-4 h-4 mr-2" />
                  <div>
                    <div className="font-medium">{alert.title || 'Alert'}</div>
                    <div className="text-sm">{alert.message || ''}</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

// Example usage with mock data
const ExamplePositionMonitor = () => {
  const mockPositions = [
    {
      symbol: 'AAPL',
      pnl: 250.50,
      strategy: 'Iron Condor',
      dte: 15,
      currentIv: 0.25,
      theta: -0.50,
      daysHeld: 10,
      totalDays: 30,
      alerts: ['Approaching profit target']
    },
    {
      symbol: 'SPY',
      pnl: -120.75,
      strategy: 'Covered Call',
      dte: 25,
      currentIv: 0.18,
      theta: -0.35,
      daysHeld: 5,
      totalDays: 45,
      alerts: ['High IV percentile']
    }
  ];

  const mockAlerts = [
    {
      severity: 'high',
      title: 'Profit Target Reached',
      message: 'AAPL Iron Condor at 75% max profit'
    },
    {
      severity: 'medium',
      title: 'Implied Volatility Alert',
      message: 'SPY IV rank above 80%'
    }
  ];

  return <PositionMonitor positions={mockPositions} alerts={mockAlerts} />;
};

export default ExamplePositionMonitor;
