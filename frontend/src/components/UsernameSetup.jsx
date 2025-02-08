import React, { useState } from 'react';
import { API_CONFIG } from '../config/api';

const UsernameSetup = ({ onSubmit, walletAddress }) => {
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!username.trim()) {
      setError('Please enter a username');
      return;
    }

    try {
      // 创建新用户
      const response = await fetch(`${API_CONFIG.BACKEND_URL}/user`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username.trim(),
          user_address: walletAddress
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to set username');
      }

      onSubmit(username.trim());
    } catch (error) {
      console.error('Error setting username:', error);
      setError(error.message);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
        <h2 className="text-2xl font-bold text-court-brown mb-6">Set Your Username</h2>
        <p className="text-gray-600 mb-4">
          Please choose a username. This will be your permanent name for all debates.
        </p>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Username
            </label>
            <input
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-court-brown focus:border-court-brown"
              placeholder="Enter your username"
            />
          </div>

          {error && (
            <div className="text-red-500 text-sm">{error}</div>
          )}

          <div className="flex justify-end space-x-4">
            <button
              type="submit"
              className="px-4 py-2 bg-court-brown text-white rounded-md hover:bg-court-brown-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-court-brown"
            >
              Set Username
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UsernameSetup;
