import React, { useState } from 'react';
import { API_CONFIG } from '../config/api';

const JoinDebateForm = ({ onSubmit, onCancel, walletAddress, username }) => {
  const [debateId, setDebateId] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

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
      const debateResponse = await fetch(`${API_CONFIG.BACKEND_URL}/debate/${debateIdNum}`);
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

      // 调用 onSubmit，传递完整的辩论信息
      onSubmit({
        debateId: debateIdNum,
        username: username,
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
          {/* Username Display */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Your Username
            </label>
            <div className="px-3 py-2 border border-gray-300 rounded-md bg-gray-50">
              {username}
            </div>
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
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-court-brown focus:border-court-brown"
              placeholder="Enter debate ID"
            />
          </div>

          {error && (
            <div className="text-red-500 text-sm">{error}</div>
          )}

          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-court-brown text-white rounded-md hover:bg-court-brown-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-court-brown"
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
