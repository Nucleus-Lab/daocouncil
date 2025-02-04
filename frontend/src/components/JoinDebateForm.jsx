import React, { useState } from 'react';

const JoinDebateForm = ({ onSubmit, onCancel }) => {
  const [debateId, setDebateId] = useState('');
  const validDebateId = 'ABC12345'; // 示例会议号

  const handleSubmit = (e) => {
    e.preventDefault();
    if (debateId.toUpperCase() === validDebateId) {
      onSubmit(debateId);
    } else {
      alert('Invalid debate ID. Try ABC12345');
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
        <h2 className="text-2xl font-bold text-court-brown mb-6">Join Existing Debate</h2>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Debate ID
            </label>
            <input
              type="text"
              required
              value={debateId}
              onChange={(e) => setDebateId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-court-brown"
              placeholder="Enter debate ID (e.g., ABC12345)"
            />
          </div>

          <div className="flex justify-end gap-4">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-court-brown text-white rounded-md hover:bg-opacity-90 transition-colors"
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
