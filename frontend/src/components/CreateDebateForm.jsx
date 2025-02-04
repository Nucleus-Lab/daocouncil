import React, { useState } from 'react';
import DatePicker from 'react-datepicker';
import "react-datepicker/dist/react-datepicker.css";

const CreateDebateForm = ({ onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    topic: '',
    numJurors: 3,
    funding: 0,
    actionPrompt: '',
    startDate: new Date(),
    endDate: new Date(Date.now() + 24 * 60 * 60 * 1000) // Default to 24 hours from now
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      ...formData,
      debateId: Math.random().toString(36).substring(2, 10).toUpperCase()
    });
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl p-6">
        <h2 className="text-2xl font-bold text-court-brown mb-6">Create New Debate</h2>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Topic */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Topic
            </label>
            <input
              type="text"
              required
              value={formData.topic}
              onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-court-brown"
              placeholder="Enter debate topic"
            />
          </div>

          {/* Time Selection */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Start Date & Time
              </label>
              <DatePicker
                selected={formData.startDate}
                onChange={(date) => setFormData({ ...formData, startDate: date })}
                showTimeSelect
                timeFormat="HH:mm"
                timeIntervals={15}
                dateFormat="MMMM d, yyyy h:mm aa"
                minDate={new Date()}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-court-brown"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                End Date & Time
              </label>
              <DatePicker
                selected={formData.endDate}
                onChange={(date) => setFormData({ ...formData, endDate: date })}
                showTimeSelect
                timeFormat="HH:mm"
                timeIntervals={15}
                dateFormat="MMMM d, yyyy h:mm aa"
                minDate={formData.startDate}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-court-brown"
              />
            </div>
          </div>

          {/* Number of Jurors */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Number of Jurors
            </label>
            <input
              type="number"
              required
              min="1"
              max="10"
              value={formData.numJurors}
              onChange={(e) => setFormData({ ...formData, numJurors: parseInt(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-court-brown"
            />
          </div>

          {/* Funding */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Funding (ETH)
            </label>
            <input
              type="number"
              required
              min="0"
              step="0.01"
              value={formData.funding}
              onChange={(e) => setFormData({ ...formData, funding: parseFloat(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-court-brown"
            />
          </div>

          {/* Action Prompt */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Action Prompt
            </label>
            <textarea
              required
              value={formData.actionPrompt}
              onChange={(e) => setFormData({ ...formData, actionPrompt: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-court-brown h-32"
              placeholder="Describe the action or proposal to be debated..."
            />
          </div>

          {/* Buttons */}
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
              Create Debate
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateDebateForm;
