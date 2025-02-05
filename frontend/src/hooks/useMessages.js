import { useState } from 'react';

export const useMessages = (walletAddress, username) => {
  const [messages, setMessages] = useState([]);

  const addMessage = async (text, stance, round, replyTo = null, debateInfo = null) => {
    // 检查用户是否是创建者
    let displayUsername = username;
    if (debateInfo && debateInfo.creator_address === walletAddress) {
      displayUsername = 'Moderator';
    }

    const newMessage = {
      id: Date.now(),
      text,
      sender: walletAddress,
      username: displayUsername || 'Anonymous',
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

    try {
      if (!debateInfo) {
        throw new Error('Debate information is missing');
      }

      // 确保 discussion_id 是整数
      const discussionId = parseInt(debateInfo.discussion_id);
      if (!discussionId) {
        throw new Error('Invalid discussion ID');
      }

      console.log('Sending message with discussion_id:', discussionId); // 调试日志

      const response = await fetch('http://localhost:8000/msg', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          discussion_id: discussionId,
          user_address: walletAddress,
          message: text
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to send message');
      }

      setMessages(prevMessages => [...prevMessages, newMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  };

  const loadMessages = async (discussion_id) => {
    try {
      const response = await fetch(`http://localhost:8000/msg/${discussion_id}`);
      if (!response.ok) {
        throw new Error('Failed to load messages');
      }

      const data = await response.json();
      
      // 获取辩论信息以检查创建者
      const debateResponse = await fetch(`http://localhost:8000/debate/${discussion_id}`);
      const debateInfo = await debateResponse.json();

      // 转换消息格式
      const formattedMessages = data.map(msg => ({
        id: msg.id,
        text: msg.message,
        sender: msg.user_address,
        username: debateInfo.creator_address === msg.user_address ? 'Moderator' : (msg.username || 'Anonymous'),
        timestamp: new Date(msg.timestamp).toLocaleTimeString(),
        stance: msg.stance,
        round: msg.round
      }));

      setMessages(formattedMessages);
    } catch (error) {
      console.error('Error loading messages:', error);
      throw error;
    }
  };

  return {
    messages,
    addMessage,
    loadMessages,
    setMessages
  };
};
