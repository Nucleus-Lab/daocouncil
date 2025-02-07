import React, { useState, useEffect } from 'react';
import DatePicker from 'react-datepicker';
import "react-datepicker/dist/react-datepicker.css";
import { API_CONFIG } from '../config/api';

const CreateDebateForm = ({ onSubmit, onCancel, walletAddress }) => {
  const [formData, setFormData] = useState({
    topic: '',
    numJurors: 5,
    jurors: [
      { id: '1', persona: '', expanded: false },
      { id: '2', persona: '', expanded: false },
      { id: '3', persona: '', expanded: false },
      { id: '4', persona: '', expanded: false },
      { id: '5', persona: '', expanded: false }
    ],
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
    const generateDebateId = () => {
      // 生成一个较小的数字ID
      const timestamp = Math.floor(Date.now() / 1000) % 1000000;  // 使用时间戳的后6位
      const random = Math.floor(Math.random() * 1000);  // 0-999的随机数
      return `${timestamp}${random}`.padStart(6, '0');  // 确保至少6位数
    };

    setFormData(prev => ({ ...prev, debateId: generateDebateId() }));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!walletAddress) {
      alert('Please connect your wallet first');
      return;
    }
    
    // 准备发送给后端的数据
    const debateData = {
      discussion_id: parseInt(formData.debateId),
      topic: formData.topic,
      sides: formData.sides.map(side => side.name),
      jurors: formData.jurors.map(juror => juror.persona),
      funding: parseFloat(formData.funding) || 0,
      action: formData.actionPrompt,
      creator_address: walletAddress
    };

    // 验证数据
    if (!debateData.topic?.trim()) {
      alert('Please enter a topic');
      return;
    }

    if (debateData.jurors.length === 0) {
      alert('Please add at least one juror persona');
      return;
    }

    if (debateData.jurors.some(persona => !persona.trim())) {
      alert('All jurors must have a persona description');
      return;
    }

    if (debateData.sides.some(side => !side.trim())) {
      alert('All sides must have a name');
      return;
    }

    console.log('Sending debate data:', debateData);

    try {
      // 首先创建或更新用户
      const userResponse = await fetch(`${API_CONFIG.BACKEND_URL}/user`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: 'Moderator',
          user_address: walletAddress
        }),
      });

      if (!userResponse.ok) {
        const errorData = await userResponse.json();
        throw new Error(errorData.detail || 'Failed to update user');
      }

      // 然后创建辩论
      const response = await fetch(`${API_CONFIG.BACKEND_URL}/debate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(debateData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create debate');
      }

      const result = await response.json();
      console.log('Debate created successfully:', result);
      
      // 确保结果包含所需的字段
      if (!result || !result.discussion_id) {
        throw new Error('Invalid response from server');
      }
      
      onSubmit(result);
    } catch (error) {
      console.error('Error creating debate:', error);
      alert(error.message || 'Failed to create debate. Please try again.');
    }
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

  const handleJurorPersonaChange = (id, newPersona) => {
    setFormData(prev => ({
      ...prev,
      jurors: prev.jurors.map(juror =>
        juror.id === id ? { ...juror, persona: newPersona } : juror
      )
    }));
  };

  const handleJurorFocus = (focusedId) => {
    setFormData(prev => ({
      ...prev,
      jurors: prev.jurors.map(juror => ({
        ...juror,
        expanded: juror.id === focusedId
      }))
    }));
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

  const generatePersonas = async () => {
    if (!formData.topic) {
      alert('Please enter a topic first');
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/generate_personas`, {
        method: 'POST',
        headers: {
          'accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          topic: formData.topic
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('Server error:', errorData);
        throw new Error(errorData.detail || 'Failed to generate personas');
      }

      const data = await response.json();
      console.log('Generated personas:', data); // 添加日志以查看返回数据
      
      // 直接使用返回的personas数组
      if (data.personas && data.personas.length >= 5) {
        const newJurors = formData.jurors.map((juror, index) => ({
          ...juror,
          persona: data.personas[index]
        }));
        setFormData(prev => ({ ...prev, jurors: newJurors }));
      } else {
        throw new Error('Not enough personas generated');
      }
    } catch (error) {
      console.error('Error generating personas:', error);
      alert(error.message || 'Failed to generate personas. Please try again.');
    }
  };

  return (
    <div className="fixed inset-0 bg-[#00000080] flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl flex flex-col max-h-[90vh]">
        <div className="flex-none p-6 border-b border-[#e5e7eb]">
          <h2 className="text-2xl font-bold text-[#4a5568]">Create New Debate</h2>
        </div>
        
        <div className="flex-1 overflow-y-auto p-6 bg-white">
          <form onSubmit={handleSubmit} id="create-debate-form" className="space-y-6">
            {/* Debate ID */}
            <div className="bg-[#fff8e1] p-4 rounded-md">
              <div className="flex items-center justify-between">
                <div>
                  <label className="block text-sm font-medium text-[#92400e] mb-1">
                    Debate ID
                  </label>
                  <div className="text-lg font-mono font-bold text-[#92400e]">
                    {formData.debateId}
                  </div>
                </div>
                <button
                  type="button"
                  onClick={copyDebateId}
                  className="px-3 py-1.5 text-sm bg-[#fef3c7] hover:bg-[#fde68a] text-[#92400e] rounded-md transition-colors"
                >
                  {copied ? 'Copied!' : 'Copy ID'}
                </button>
              </div>
              <p className="mt-2 text-sm text-[#92400e]">
                Save this ID to share with others who want to join the debate.
              </p>
            </div>

            {/* Topic */}
            <div>
              <label className="block text-sm font-medium text-[#4a5568] mb-1">
                Debate Topic
              </label>
              <input
                type="text"
                required
                value={formData.topic}
                onChange={(e) => setFormData(prev => ({ ...prev, topic: e.target.value }))}
                className="w-full px-3 py-2 border border-[#e5e7eb] rounded-md focus:outline-none focus:ring-2 focus:ring-[#92400e] bg-white text-[#1a202c]"
                placeholder="Enter the topic for debate"
              />
            </div>

            {/* Jurors */}
            <div>
              <label className="block text-sm font-medium text-[#4a5568] mb-2">
                Juror Personas
              </label>
              <div className="space-y-3">
                <div className="flex justify-between items-center mb-2">
                  <button
                    type="button"
                    onClick={generatePersonas}
                    disabled={!formData.topic}
                    className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                      formData.topic 
                        ? 'bg-[#92400e] text-white hover:bg-[#78350f]'
                        : 'bg-[#e5e7eb] text-[#9ca3af] cursor-not-allowed'
                    }`}
                  >
                    Generate Personas
                  </button>
                </div>
                {formData.jurors.map((juror, index) => (
                  <div key={juror.id} className="flex items-center gap-2 mb-2">
                    <textarea
                      value={juror.persona}
                      onChange={(e) => handleJurorPersonaChange(juror.id, e.target.value)}
                      onFocus={() => handleJurorFocus(juror.id)}
                      placeholder={`Juror ${index + 1} Persona Description`}
                      className={`flex-1 p-2 border border-[#e5e7eb] rounded focus:outline-none focus:ring-2 focus:ring-[#92400e] bg-white text-[#1a202c] transition-all duration-300 ease-in-out ${
                        juror.expanded ? 'h-32' : 'h-10'
                      }`}
                      style={{
                        resize: 'none',
                        overflow: juror.expanded ? 'auto' : 'hidden'
                      }}
                    />
                  </div>
                ))}
              </div>
            </div>

            {/* Funding */}
            <div>
              <label className="block text-sm font-medium text-[#4a5568] mb-2">
                Funding
              </label>
              <input
                type="number"
                step="any"
                min="0"
                value={formData.funding === 0 && formData.funding === '' ? '' : formData.funding}
                onChange={(e) => {
                  const value = e.target.value;
                  const funding = value === '' ? '' : Number(parseFloat(value).toFixed(18));
                  setFormData(prev => ({ ...prev, funding }));
                }}
                className="w-full px-3 py-2 border border-[#e5e7eb] rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-[#92400e] bg-white text-[#1a202c]"
                placeholder="Enter funding amount"
              />
            </div>

            {/* Action Prompt */}
            <div>
              <label className="block text-sm font-medium text-[#4a5568] mb-1">
                Action Prompt
              </label>
              <textarea
                required
                value={formData.actionPrompt}
                onChange={(e) => setFormData(prev => ({ ...prev, actionPrompt: e.target.value }))}
                className="w-full px-3 py-2 border border-[#e5e7eb] rounded-md focus:outline-none focus:ring-2 focus:ring-[#92400e] bg-white text-[#1a202c]"
                rows="3"
                placeholder="What action should be taken based on the debate outcome?"
              />
            </div>

            {/* Debate Sides */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <label className="block text-sm font-medium text-[#4a5568]">
                  Debate Sides
                </label>
                <button
                  type="button"
                  onClick={addSide}
                  className="text-sm text-[#92400e] hover:text-[#78350f]"
                >
                  + Add Side
                </button>
              </div>
              <div className="space-y-3">
                {formData.sides.map((side) => (
                  <div key={side.id} className="flex items-center gap-2">
                    <input
                      type="text"
                      value={side.name}
                      onChange={(e) => updateSideName(side.id, e.target.value)}
                      className="flex-1 px-3 py-2 border border-[#e5e7eb] rounded-md focus:outline-none focus:ring-2 focus:ring-[#92400e] bg-white text-[#1a202c]"
                      placeholder="Enter side name"
                      required
                    />
                    {formData.sides.length > 2 && (
                      <button
                        type="button"
                        onClick={() => removeSide(side.id)}
                        className="text-[#ef4444] hover:text-[#dc2626]"
                      >
                        Remove
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Date Range */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-[#4a5568] mb-1">
                  Start Date
                </label>
                <DatePicker
                  selected={formData.startDate}
                  onChange={(date) => setFormData(prev => ({ ...prev, startDate: date }))}
                  className="w-full px-3 py-2 border border-[#e5e7eb] rounded-md focus:outline-none focus:ring-2 focus:ring-[#92400e] bg-white text-[#1a202c]"
                  dateFormat="yyyy-MM-dd HH:mm"
                  showTimeSelect
                  timeFormat="HH:mm"
                  timeIntervals={60}
                  timeCaption="Time"
                  minDate={new Date()}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-[#4a5568] mb-1">
                  End Date
                </label>
                <DatePicker
                  selected={formData.endDate}
                  onChange={(date) => setFormData(prev => ({ ...prev, endDate: date }))}
                  className="w-full px-3 py-2 border border-[#e5e7eb] rounded-md focus:outline-none focus:ring-2 focus:ring-[#92400e] bg-white text-[#1a202c]"
                  dateFormat="yyyy-MM-dd HH:mm"
                  showTimeSelect
                  timeFormat="HH:mm"
                  timeIntervals={60}
                  timeCaption="Time"
                  minDate={formData.startDate}
                />
              </div>
            </div>
          </form>
        </div>

        <div className="flex-none p-6 border-t border-[#e5e7eb] bg-[#f9fafb]">
          <div className="flex justify-end gap-4">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 text-[#4a5568] hover:text-[#1a202c] transition-colors"
            >
              Cancel
            </button>
            <button
              form="create-debate-form"
              type="submit"
              className="px-4 py-2 bg-[#92400e] text-white rounded-md hover:bg-[#78350f] transition-colors"
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
