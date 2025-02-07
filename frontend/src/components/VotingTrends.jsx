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

const VotingTrends = ({ messages = [], debateSides = [{ id: '1', name: 'Side 1' }, { id: '2', name: 'Side 2' }] }) => {
  // 计算每个时间点每个立场的消息数量
  const calculateTrends = () => {
    const trends = {};
    // 为每个立场初始化计数器
    debateSides.forEach(side => {
      trends[side.id] = new Map();
    });

    // 按时间排序消息
    const sortedMessages = [...messages].sort((a, b) => 
      new Date(a.timestamp) - new Date(b.timestamp)
    );

    // 为每个立场计算累计值
    sortedMessages.forEach(message => {
      if (message.stance) {
        const time = message.timestamp;
        const currentCount = trends[message.stance]?.get(time) || 0;
        if (trends[message.stance]) {
          trends[message.stance].set(time, currentCount + 1);
        }
      }
    });

    return trends;
  };

  // 如果没有消息，显示空状态
  if (!messages || messages.length === 0) {
    return (
      <div className="bg-gradient-to-br from-[#fdf6e3] to-[#f5e6d3] rounded-lg shadow-sm p-4 h-[300px] flex items-center justify-center">
        <p className="text-gray-400">No messages yet</p>
      </div>
    );
  }

  const trends = calculateTrends();

  // 准备图表数据
  const timePoints = Array.from(
    new Set(messages.map(m => m.timestamp))
  ).sort((a, b) => new Date(a) - new Date(b));

  const data = {
    labels: timePoints,
    datasets: debateSides.map((side, index) => {
      // 计算累计值
      const cumulativeData = timePoints.map(time => {
        const prevIndex = timePoints.indexOf(time);
        const prevTotal = prevIndex > 0 ? 
          [...(trends[side.id]?.entries() || [])]
            .filter((_, i) => i < prevIndex)
            .reduce((sum, [_, count]) => sum + count, 0) : 0;
        return prevTotal + (trends[side.id]?.get(time) || 0);
      });

      // 为每个立场生成不同的颜色
      const hue = (index * 137) % 360; // 使用黄金角度来生成分散的颜色
      const borderColor = `hsl(${hue}, 70%, 50%)`;
      const backgroundColor = `hsla(${hue}, 70%, 50%, 0.1)`;

      return {
        label: side.name,
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
        text: 'Debate Engagement Trends',
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
        },
        callbacks: {
          label: function(context) {
            return `${context.dataset.label}: ${context.parsed.y} messages`;
          }
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

export default VotingTrends;
