import React, { useState } from 'react';

const JoinDebateForm = ({ onSubmit, onCancel, walletAddress }) => {
  const [debateId, setDebateId] = useState('');
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');
  const validDebateId = '12345'; // 示例会议号，改为数字格式

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // 检查用户名是否为空
    if (!username.trim()) {
      setError('Please enter a username');
      return;
    }

    // 检查 debate ID 是否为空
    if (!debateId.trim()) {
      setError('Please enter a debate ID');
      return;
    }

    // 检查 debate ID 是否为数字
    const debateIdNum = parseInt(debateId);
    if (isNaN(debateIdNum)) {
      setError('Invalid debate ID. Please enter a valid number.');
      return;
    }

    try {
      // 先获取辩论信息，确认辩论存在
      const debateResponse = await fetch(`http://localhost:8000/debate/${debateIdNum}`);
      if (!debateResponse.ok) {
        if (debateResponse.status === 404) {
          throw new Error('Debate not found. Please check if the debate ID is correct.');
        }
        throw new Error('Failed to get debate information. Please try again.');
      }

      const debateData = await debateResponse.json();
      if (!debateData.debate) {
        throw new Error('Invalid debate ID. Please check if the debate ID is correct.');
      }

      // 注册用户并加入辩论
      const userResponse = await fetch('http://localhost:8000/user', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username.trim(),
          user_address: walletAddress,
          debate_id: debateIdNum
        }),
      });

      if (!userResponse.ok) {
        const errorData = await userResponse.json();
        throw new Error(errorData.detail || 'Failed to join debate');
      }

      // 调用 onSubmit，传递完整的辩论信息
      onSubmit({
        debateId: debateIdNum,
        username: username.trim(),
        debateInfo: {
          sides: debateData.debate.sides,
          topic: debateData.debate.topic,
          action: debateData.debate.action,
          discussion_id: debateData.debate.discussion_id,
          funding: debateData.debate.funding,
          creator_address: debateData.debate.creator_address,
          created_at: debateData.debate.created_at,
          jurors: debateData.jurors
        }
      });
    } catch (error) {
      console.error('Error joining debate:', error);
      setError(error.message);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
        <h2 className="text-2xl font-bold text-court-brown mb-6">Join Existing Debate</h2>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Username Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Your Username
            </label>
            <input
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-1 focus:ring-court-brown focus:border-court-brown"
              placeholder="Enter your username"
            />
          </div>

          {/* Debate ID Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Debate ID
            </label>
            <input
              type="text"
              required
              value={debateId}
              onChange={(e) => setDebateId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-1 focus:ring-court-brown focus:border-court-brown"
              placeholder={`Enter debate ID (e.g., ${validDebateId})`}
            />
            <p className="mt-1 text-sm text-gray-500">
              Please enter a numeric debate ID
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="text-red-500 text-sm">
              {error}
            </div>
          )}

          {/* Buttons */}
          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 text-sm font-medium text-white bg-court-brown rounded-md hover:bg-court-brown-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-court-brown"
            >
              Join Debate
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default JoinDebateForm;
