import { useState } from 'react';

const formatWalletAddress = (address) => {
  if (!address || address === 'Moderator') return '';
  return address.length > 10 ? `${address.slice(0, 4)}...${address.slice(-4)}` : address;
};

export const useMessages = (walletAddress, username) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Welcome to the debate! Please be respectful and constructive in your discussion.",
      sender: "Moderator",
      username: "Moderator",
      timestamp: new Date().toLocaleTimeString(),
    }
  ]);

  const addMessage = (text, stance, round, replyTo = null) => {
    const newMessage = {
      id: Date.now(),
      text,
      sender: formatWalletAddress(walletAddress),
      username: username || 'Anonymous',
      timestamp: new Date().toLocaleTimeString(),
      stance,
      round,
      replyTo: replyTo ? {
        id: replyTo.id,
        text: replyTo.text,
        sender: replyTo.sender,
        username: replyTo.username
      } : null
    };
    setMessages(prevMessages => [...prevMessages, newMessage]);
  };

  return {
    messages,
    setMessages,
    addMessage,
  };
};
