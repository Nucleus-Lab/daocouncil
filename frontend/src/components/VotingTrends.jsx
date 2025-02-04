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
  // 如果没有消息，显示空状态
  if (!messages || messages.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-4 h-[300px] flex items-center justify-center">
        <p className="text-gray-400">No messages yet</p>
      </div>
    );
  }

  // 计算每个时间点每个立场的消息数量
  const calculateTrends = () => {
    const trends = {};
    debateSides.forEach(side => {
      trends[side.id] = new Map();
    });

    // 按时间排序消息
    const sortedMessages = [...messages].sort((a, b) => 
      new Date(a.timestamp) - new Date(b.timestamp)
    );

    sortedMessages.forEach(message => {
      if (message.stance) {
        const time = message.timestamp;
        const currentCount = trends[message.stance].get(time) || 0;
        trends[message.stance].set(time, currentCount + 1);
      }
    });

    return trends;
  };

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
          [...trends[side.id].entries()]
            .filter((_, i) => i < prevIndex)
            .reduce((sum, [_, count]) => sum + count, 0) : 0;
        return prevTotal + (trends[side.id].get(time) || 0);
      });

      return {
        label: side.name,
        data: cumulativeData,
        borderColor: index === 0 ? 'rgb(52, 211, 153)' : 
                    index === 1 ? 'rgb(251, 113, 133)' : 
                    `hsl(${(index * 137) % 360}, 70%, 50%)`,
        backgroundColor: index === 0 ? 'rgba(52, 211, 153, 0.5)' : 
                        index === 1 ? 'rgba(251, 113, 133, 0.5)' : 
                        `hsla(${(index * 137) % 360}, 70%, 50%, 0.5)`,
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
          color: '#4a3223', // 温暖的棕色
          font: {
            family: "'Inter', sans-serif",
            size: 12
          }
        }
      },
      title: {
        display: true,
        text: 'Debate Engagement Trends',
        color: '#2c1810', // 深棕色
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
        backgroundColor: 'rgba(44, 24, 16, 0.95)', // 深棕色背景
        titleColor: '#ffd294', // 温暖的橙色
        bodyColor: '#f0c987', // 浅橙色
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
    interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false
    },
    scales: {
      x: {
        grid: {
          display: false
        },
        ticks: {
          color: '#4a3223', // 温暖的棕色
          font: {
            family: "'Inter', sans-serif",
            size: 12
          },
          callback: function(value, index) {
            // 格式化时间显示
            const time = this.getLabelForValue(value);
            return time.split(' ')[0]; // 只显示时间部分
          },
          maxRotation: 45,
          minRotation: 45
        }
      },
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(107, 68, 35, 0.1)' // 淡棕色网格
        },
        ticks: {
          color: '#4a3223', // 温暖的棕色
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
