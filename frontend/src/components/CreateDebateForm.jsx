import React, { useState, useEffect } from 'react';
import DatePicker from 'react-datepicker';
import "react-datepicker/dist/react-datepicker.css";

const CreateDebateForm = ({ onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    topic: '',
    numJurors: 3,
    funding: 0,
    actionPrompt: '',
    startDate: new Date(),
    endDate: new Date(Date.now() + 24 * 60 * 60 * 1000),
    debateId: '',
    sides: [
      { id: '1', name: 'Side 1' },
      { id: '2', name: 'Side 2' }
    ]
  });

  const [copied, setCopied] = useState(false);

  useEffect(() => {
    // Generate debate ID on component mount
    const generateDebateId = () => {
      const timestamp = Date.now().toString(36);
      const random = Math.random().toString(36).substring(2, 6);
      return `${timestamp.slice(-4)}${random}`.toUpperCase();
    };

    setFormData(prev => ({ ...prev, debateId: generateDebateId() }));
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const copyDebateId = async () => {
    try {
      await navigator.clipboard.writeText(formData.debateId);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const addSide = () => {
    setFormData(prev => ({
      ...prev,
      sides: [
        ...prev.sides,
        { id: Date.now().toString(), name: `Side ${prev.sides.length + 1}` }
      ]
    }));
  };

  const removeSide = (idToRemove) => {
    if (formData.sides.length <= 2) {
      alert('A debate must have at least 2 sides');
      return;
    }
    setFormData(prev => ({
      ...prev,
      sides: prev.sides.filter(side => side.id !== idToRemove)
    }));
  };

  const updateSideName = (id, newName) => {
    setFormData(prev => ({
      ...prev,
      sides: prev.sides.map(side =>
        side.id === id ? { ...side, name: newName } : side
      )
    }));
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl flex flex-col max-h-[90vh]">
        <div className="flex-none p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-court-brown">Create New Debate</h2>
        </div>
        
        <div className="flex-1 overflow-y-auto p-6">
          <form onSubmit={handleSubmit} id="create-debate-form" className="space-y-6">
            {/* Debate ID */}
            <div className="bg-amber-50 p-4 rounded-md">
              <div className="flex items-center justify-between">
                <div>
                  <label className="block text-sm font-medium text-amber-800 mb-1">
                    Debate ID
                  </label>
                  <div className="text-lg font-mono font-bold text-amber-900">
                    {formData.debateId}
                  </div>
                </div>
                <button
                  type="button"
                  onClick={copyDebateId}
                  className="px-3 py-1.5 text-sm bg-amber-100 hover:bg-amber-200 text-amber-900 rounded-md transition-colors"
                >
                  {copied ? 'Copied!' : 'Copy ID'}
                </button>
              </div>
              <p className="mt-2 text-sm text-amber-700">
                Save this ID to share with others who want to join the debate.
              </p>
            </div>

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

            {/* Debate Sides */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium text-gray-700">
                  Debate Sides
                </label>
                <button
                  type="button"
                  onClick={addSide}
                  className="text-sm text-amber-600 hover:text-amber-700 flex items-center gap-1"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  Add Side
                </button>
              </div>
              <div className="space-y-2">
                {formData.sides.map((side) => (
                  <div key={side.id} className="flex gap-2">
                    <input
                      type="text"
                      required
                      value={side.name}
                      onChange={(e) => updateSideName(side.id, e.target.value)}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-court-brown text-sm"
                      placeholder="Enter side name"
                    />
                    {formData.sides.length > 2 && (
                      <button
                        type="button"
                        onClick={() => removeSide(side.id)}
                        className="px-2 text-gray-400 hover:text-red-500"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    )}
                  </div>
                ))}
              </div>
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
                  dateFormat="MMMM d, yyyy h:mm aa"
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
                  dateFormat="MMMM d, yyyy h:mm aa"
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
                min="3"
                max="12"
                required
                value={formData.numJurors}
                onChange={(e) => setFormData({ ...formData, numJurors: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-court-brown"
              />
            </div>

            {/* Funding Amount */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Funding Amount (ETH)
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                required
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
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-court-brown h-24"
                placeholder="Enter the action prompt for jurors..."
              />
            </div>
          </form>
        </div>

        <div className="flex-none p-6 border-t border-gray-200 bg-gray-50">
          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              form="create-debate-form"
              className="px-4 py-2 bg-court-brown text-white rounded-md hover:bg-opacity-90 transition-colors"
            >
              Create Debate
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateDebateForm;
