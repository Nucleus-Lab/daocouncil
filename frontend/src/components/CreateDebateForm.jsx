import React, { useState, useEffect } from 'react';
import DatePicker from 'react-datepicker';
import "react-datepicker/dist/react-datepicker.css";
import { API_CONFIG } from '../config/api';

const CreateDebateForm = ({ onSubmit, onCancel, walletAddress, username }) => {
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
  const [isGenerating, setIsGenerating] = useState(false);

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
          username: username,
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
        body: JSON.stringify({
          topic: formData.topic,
          action: formData.actionPrompt,
          creator_address: walletAddress,
          creator_username: username,
          funding: formData.funding,
          jurors: formData.jurors.map(juror => juror.persona),
          sides: formData.sides.map(side => side.name)
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create debate');
      }

      const result = await response.json();
      console.log('Debate created successfully:', result);
      console.log('Debate details:');
      console.log('- Discussion ID:', result.discussion_id);
      console.log('- Topic:', result.topic);
      console.log('- Funding:', result.funding);
      console.log('- Action:', result.action);
      console.log('Wallet Information:');
      console.log('- CDP Wallet Address:', result.cdp_wallet_address);
      console.log('- Privy Wallet Address:', result.privy_wallet_address);
      console.log('- Privy Wallet ID:', result.privy_wallet_id);
      console.log('Participants:');
      console.log('- Creator:', result.creator_username, '(', result.creator_address, ')');
      console.log('- Jurors:', result.jurors);
      console.log('- Sides:', result.sides);
      console.log('Timestamps:');
      console.log('- Created at:', result.created_at);
      
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
    if (!formData.topic || isGenerating) return;
    
    setIsGenerating(true);
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
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '1rem'
    }}>
      <div style={{
        backgroundColor: '#ffffff',
        borderRadius: '0.5rem',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        width: '100%',
        maxWidth: '42rem',
        display: 'flex',
        flexDirection: 'column',
        maxHeight: '90vh'
      }}>
        <div style={{
          padding: '1.5rem',
          borderBottom: '1px solid #e5e7eb'
        }}>
          <h2 style={{
            fontSize: '1.5rem',
            fontWeight: 'bold',
            color: '#1a202c'
          }}>Create New Debate</h2>
        </div>
        
        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: '1.5rem',
          backgroundColor: '#ffffff'
        }}>
          <form onSubmit={handleSubmit} id="create-debate-form" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* Debate ID */}
            <div style={{
              backgroundColor: '#fff8e1',
              padding: '1rem',
              borderRadius: '0.375rem'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <label style={{
                    display: 'block',
                    fontSize: '0.875rem',
                    fontWeight: 500,
                    color: '#92400e',
                    marginBottom: '0.25rem'
                  }}>
                    Debate ID
                  </label>
                  <div style={{
                    fontSize: '1.125rem',
                    fontFamily: 'monospace',
                    fontWeight: 'bold',
                    color: '#92400e'
                  }}>
                    {formData.debateId}
                  </div>
                </div>
                <button
                  type="button"
                  onClick={copyDebateId}
                  style={{
                    padding: '0.375rem 0.75rem',
                    fontSize: '0.875rem',
                    backgroundColor: '#fef3c7',
                    color: '#92400e',
                    borderRadius: '0.375rem',
                    border: 'none',
                    cursor: 'pointer',
                    transition: 'background-color 0.2s'
                  }}
                  onMouseOver={e => e.target.style.backgroundColor = '#fde68a'}
                  onMouseOut={e => e.target.style.backgroundColor = '#fef3c7'}
                >
                  {copied ? 'Copied!' : 'Copy ID'}
                </button>
              </div>
              <p style={{
                marginTop: '0.5rem',
                fontSize: '0.875rem',
                color: '#92400e'
              }}>
                Save this ID to share with others who want to join the debate.
              </p>
            </div>

            {/* Topic */}
            <div>
              <label style={{
                display: 'block',
                fontSize: '0.875rem',
                fontWeight: 500,
                color: '#1a202c',
                marginBottom: '0.25rem'
              }}>
                Debate Topic
              </label>
              <input
                type="text"
                required
                value={formData.topic}
                onChange={(e) => setFormData(prev => ({ ...prev, topic: e.target.value }))}
                style={{
                  width: '100%',
                  padding: '0.5rem 0.75rem',
                  border: '1px solid #e5e7eb',
                  borderRadius: '0.375rem',
                  backgroundColor: '#ffffff',
                  color: '#1a202c',
                  outline: 'none'
                }}
                placeholder="Enter the topic for debate"
              />
            </div>

            {/* Jurors */}
            <div>
              <label style={{
                display: 'block',
                fontSize: '0.875rem',
                fontWeight: 500,
                color: '#1a202c',
                marginBottom: '0.5rem'
              }}>
                Juror Personas
              </label>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <button
                    type="button"
                    onClick={generatePersonas}
                    disabled={!formData.topic || isGenerating}
                    style={{
                      padding: '0.375rem 0.75rem',
                      fontSize: '0.875rem',
                      backgroundColor: !formData.topic || isGenerating ? '#e5e7eb' : '#92400e',
                      color: !formData.topic || isGenerating ? '#9ca3af' : '#ffffff',
                      borderRadius: '0.375rem',
                      border: 'none',
                      cursor: !formData.topic || isGenerating ? 'not-allowed' : 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      transition: 'background-color 0.2s'
                    }}
                    onMouseOver={e => {
                      if (formData.topic && !isGenerating) {
                        e.target.style.backgroundColor = '#78350f';
                      }
                    }}
                    onMouseOut={e => {
                      if (formData.topic && !isGenerating) {
                        e.target.style.backgroundColor = '#92400e';
                      }
                    }}
                  >
                    {isGenerating && (
                      <svg style={{ animation: 'spin 1s linear infinite', height: '1rem', width: '1rem' }} viewBox="0 0 24 24">
                        <circle style={{ opacity: 0.25 }} cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path style={{ opacity: 0.75 }} fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                    )}
                    {isGenerating ? 'Generating...' : 'Auto Generate'}
                  </button>
                </div>
                {formData.jurors.map((juror, index) => (
                  <div key={juror.id} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <textarea
                      value={juror.persona}
                      onChange={(e) => handleJurorPersonaChange(juror.id, e.target.value)}
                      onFocus={() => handleJurorFocus(juror.id)}
                      placeholder={`Juror ${index + 1} Persona Description`}
                      style={{
                        flex: 1,
                        padding: '0.5rem',
                        border: '1px solid #e5e7eb',
                        borderRadius: '0.375rem',
                        backgroundColor: '#ffffff',
                        color: '#1a202c',
                        height: juror.expanded ? '8rem' : '2.5rem',
                        resize: 'none',
                        overflow: juror.expanded ? 'auto' : 'hidden',
                        transition: 'height 0.3s ease-in-out'
                      }}
                    />
                  </div>
                ))}
              </div>
            </div>

            {/* Funding */}
            <div>
              <label style={{
                display: 'block',
                fontSize: '0.875rem',
                fontWeight: 500,
                color: '#1a202c',
                marginBottom: '0.5rem'
              }}>
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
                style={{
                  width: '100%',
                  padding: '0.5rem 0.75rem',
                  border: '1px solid #e5e7eb',
                  borderRadius: '0.375rem',
                  backgroundColor: '#ffffff',
                  color: '#1a202c',
                  outline: 'none'
                }}
                placeholder="Enter funding amount"
              />
            </div>

            {/* Action Prompt */}
            <div>
              <label style={{
                display: 'block',
                fontSize: '0.875rem',
                fontWeight: 500,
                color: '#1a202c',
                marginBottom: '0.25rem'
              }}>
                Action Prompt
              </label>
              <textarea
                required
                value={formData.actionPrompt}
                onChange={(e) => setFormData(prev => ({ ...prev, actionPrompt: e.target.value }))}
                style={{
                  width: '100%',
                  padding: '0.5rem 0.75rem',
                  border: '1px solid #e5e7eb',
                  borderRadius: '0.375rem',
                  backgroundColor: '#ffffff',
                  color: '#1a202c',
                  outline: 'none',
                  height: '6rem',
                  resize: 'none'
                }}
                placeholder="What action should be taken based on the debate outcome?"
              />
            </div>

            {/* Debate Sides */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <label style={{
                  display: 'block',
                  fontSize: '0.875rem',
                  fontWeight: 500,
                  color: '#1a202c'
                }}>
                  Debate Sides
                </label>
                <button
                  type="button"
                  onClick={addSide}
                  style={{
                    fontSize: '0.875rem',
                    color: '#92400e',
                    border: 'none',
                    backgroundColor: 'transparent',
                    cursor: 'pointer'
                  }}
                  onMouseOver={e => e.target.style.color = '#78350f'}
                  onMouseOut={e => e.target.style.color = '#92400e'}
                >
                  + Add Side
                </button>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {formData.sides.map((side) => (
                  <div key={side.id} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <input
                      type="text"
                      value={side.name}
                      onChange={(e) => updateSideName(side.id, e.target.value)}
                      style={{
                        flex: 1,
                        padding: '0.5rem 0.75rem',
                        border: '1px solid #e5e7eb',
                        borderRadius: '0.375rem',
                        backgroundColor: '#ffffff',
                        color: '#1a202c',
                        outline: 'none'
                      }}
                      placeholder="Enter side name"
                      required
                    />
                    {formData.sides.length > 2 && (
                      <button
                        type="button"
                        onClick={() => removeSide(side.id)}
                        style={{
                          color: '#ef4444',
                          border: 'none',
                          backgroundColor: 'transparent',
                          cursor: 'pointer'
                        }}
                        onMouseOver={e => e.target.style.color = '#dc2626'}
                        onMouseOut={e => e.target.style.color = '#ef4444'}
                      >
                        Remove
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Date Range */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <label style={{
                  display: 'block',
                  fontSize: '0.875rem',
                  fontWeight: 500,
                  color: '#1a202c',
                  marginBottom: '0.25rem'
                }}>
                  Start Date
                </label>
                <DatePicker
                  selected={formData.startDate}
                  onChange={(date) => setFormData(prev => ({ ...prev, startDate: date }))}
                  customInput={
                    <input
                      style={{
                        width: '100%',
                        padding: '0.5rem 0.75rem',
                        border: '1px solid #e5e7eb',
                        borderRadius: '0.375rem',
                        backgroundColor: '#ffffff',
                        color: '#1a202c',
                        outline: 'none'
                      }}
                    />
                  }
                  dateFormat="yyyy-MM-dd HH:mm"
                  showTimeSelect
                  timeFormat="HH:mm"
                  timeIntervals={60}
                  timeCaption="Time"
                  minDate={new Date()}
                />
              </div>
              <div>
                <label style={{
                  display: 'block',
                  fontSize: '0.875rem',
                  fontWeight: 500,
                  color: '#1a202c',
                  marginBottom: '0.25rem'
                }}>
                  End Date
                </label>
                <DatePicker
                  selected={formData.endDate}
                  onChange={(date) => setFormData(prev => ({ ...prev, endDate: date }))}
                  customInput={
                    <input
                      style={{
                        width: '100%',
                        padding: '0.5rem 0.75rem',
                        border: '1px solid #e5e7eb',
                        borderRadius: '0.375rem',
                        backgroundColor: '#ffffff',
                        color: '#1a202c',
                        outline: 'none'
                      }}
                    />
                  }
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

        <div style={{
          padding: '1.5rem',
          borderTop: '1px solid #e5e7eb',
          backgroundColor: '#f9fafb',
          display: 'flex',
          justifyContent: 'flex-end',
          gap: '1rem'
        }}>
          <button
            type="button"
            onClick={onCancel}
            style={{
              padding: '0.5rem 1rem',
              color: '#4a5568',
              border: 'none',
              backgroundColor: 'transparent',
              cursor: 'pointer'
            }}
            onMouseOver={e => e.target.style.color = '#1a202c'}
            onMouseOut={e => e.target.style.color = '#4a5568'}
          >
            Cancel
          </button>
          <button
            form="create-debate-form"
            type="submit"
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#92400e',
              color: '#ffffff',
              border: 'none',
              borderRadius: '0.375rem',
              cursor: 'pointer',
              transition: 'background-color 0.2s'
            }}
            onMouseOver={e => e.target.style.backgroundColor = '#78350f'}
            onMouseOut={e => e.target.style.backgroundColor = '#92400e'}
          >
            Create Debate
          </button>
        </div>
      </div>
    </div>
  );
};

export default CreateDebateForm;
