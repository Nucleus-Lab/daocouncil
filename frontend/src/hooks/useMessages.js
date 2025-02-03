import { useState } from 'react';

export const useMessages = () => {
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [participantCounter, setParticipantCounter] = useState(1);

  const addMessage = (text, stance, round) => {
    const newParticipantNumber = participantCounter;
    setParticipantCounter(prev => prev + 1);

    setMessages([...messages, {
      id: Date.now(),
      text,
      sender: `Participant ${newParticipantNumber}`,
      timestamp: new Date().toLocaleTimeString(),
      stance,
      round
    }]);
    
    setCurrentMessage('');
  };

  return {
    messages,
    setMessages,
    currentMessage,
    setCurrentMessage,
    addMessage
  };
};
