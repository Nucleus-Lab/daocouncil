import { useState } from 'react';

export const useMessages = (walletAddress, username) => {
  const addMessage = async (text, stance, round, replyTo = null, debateInfo = null) => {
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
          message: text,
          stance: stance || null  // 添加 stance，如果没有则为 null
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to send message');
      }

      return await response.json();
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
      return await response.json();
    } catch (error) {
      console.error('Error loading messages:', error);
      throw error;
    }
  };

  return {
    addMessage,
    loadMessages
  };
};
