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

      // 准备消息数据
      const messageData = {
        discussion_id: discussionId,
        user_address: walletAddress,
        message: text,
        stance: stance === '' ? null : stance  // 明确处理空字符串的情况
      };

      // 调试日志
      console.log('Sending message data:', messageData);

      const response = await fetch('http://localhost:8000/msg', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(messageData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to send message');
      }

      const responseData = await response.json();
      console.log('Server response:', responseData);  // 添加服务器响应日志
      return responseData;
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
