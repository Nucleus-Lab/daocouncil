import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const AIVotingTrends = ({ aiVotingTrends = [] }) => {
  if (aiVotingTrends.length === 0) {
    return (
      <div className="bg-gradient-to-br from-[#fdf6e3] to-[#f5e6d3] rounded-lg shadow-sm p-4 h-[300px] flex items-center justify-center">
        <p className="text-gray-400">No AI votes yet</p>
      </div>
    );
  }

  // Prepare data for the chart
  const timePoints = aiVotingTrends.map(trend => trend.time);
  const voteOptions = [...new Set(aiVotingTrends.flatMap(trend => Object.keys(trend.votes)))];

  const data = {
    labels: timePoints,
    datasets: voteOptions.map((option, index) => {
      // Calculate cumulative votes for each option
      const cumulativeData = aiVotingTrends.map((trend, i) => {
        const prevTotal = i > 0 ? 
          aiVotingTrends
            .slice(0, i)
            .reduce((sum, t) => sum + (t.votes[option] || 0), 0) : 0;
        return prevTotal + (trend.votes[option] || 0);
      });

      // Generate color for each option
      const hue = (index * 137) % 360;
      const borderColor = `hsl(${hue}, 70%, 50%)`;
      const backgroundColor = `hsla(${hue}, 70%, 50%, 0.1)`;

      return {
        label: `Option ${option}`,
        data: cumulativeData,
        borderColor,
        backgroundColor,
        tension: 0.4,
        fill: true
      };
    })
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          usePointStyle: true,
          padding: 15,
          color: '#4a3223',
          font: {
            family: "'Inter', sans-serif",
            size: 12
          }
        }
      },
      title: {
        display: true,
        text: 'AI Jurors Voting Trends',
        color: '#2c1810',
        font: {
          family: "'Inter', sans-serif",
          size: 14,
          weight: 'medium'
        },
        padding: {
          top: 10,
          bottom: 20
        }
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(44, 24, 16, 0.95)',
        titleColor: '#ffd294',
        bodyColor: '#f0c987',
        borderColor: '#6b4423',
        borderWidth: 1,
        padding: 10,
        bodyFont: {
          family: "'Inter', sans-serif"
        },
        titleFont: {
          family: "'Inter', sans-serif",
          weight: 'medium'
        }
      }
    },
    scales: {
      x: {
        grid: {
          display: false
        },
        ticks: {
          color: '#4a3223',
          font: {
            family: "'Inter', sans-serif",
            size: 12
          }
        }
      },
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(107, 68, 35, 0.1)'
        },
        ticks: {
          color: '#4a3223',
          font: {
            family: "'Inter', sans-serif",
            size: 12
          },
          stepSize: 1
        }
      }
    }
  };

  return (
    <div className="bg-gradient-to-br from-[#fdf6e3] to-[#f5e6d3] rounded-lg shadow-sm p-4 h-[300px]">
      <Line data={data} options={options} />
    </div>
  );
};

export default AIVotingTrends; 