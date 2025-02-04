import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const VotingTrends = ({ votingData }) => {
  return (
    <div className="h-full flex flex-col">
      <h2 className="text-sm text-amber-200 flex items-center gap-1 tracking-wide mb-2">
        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        {'>>'} Voting Trends
      </h2>
      
      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={votingData}
            margin={{
              top: 5,
              right: 5,
              left: -20,
              bottom: 5,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#2c1810" opacity={0.1} />
            <XAxis 
              dataKey="time" 
              stroke="#2c1810" 
              opacity={0.5}
              tick={{ fontSize: 10 }}
            />
            <YAxis 
              stroke="#2c1810" 
              opacity={0.5}
              tick={{ fontSize: 10 }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1a1a1a', 
                border: 'none',
                borderRadius: '4px',
                color: '#fff'
              }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="yes"
              stroke="#22c55e"
              strokeWidth={2}
              dot={false}
              name="Yes Votes"
            />
            <Line
              type="monotone"
              dataKey="no"
              stroke="#ef4444"
              strokeWidth={2}
              dot={false}
              name="No Votes"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default VotingTrends;
