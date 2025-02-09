import { useState } from 'react';
import { API_CONFIG } from '../config/api';

export const useMessages = (walletAddress, username) => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const addMessage = async (text, stance, round, replyTo = null, debateInfo = null) => {
    try {
      setIsLoading(true);
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
        username: username,  // 添加 username
        message: text,
        stance: stance === '' ? null : stance  // 明确处理空字符串的情况
      };

      // 调试日志
      console.log('Sending message data:', messageData);

      const response = await fetch(`${API_CONFIG.BACKEND_URL}/msg`, {
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
      console.log('Message sent successfully. Waiting for potential juror response...');  // 添加日志

      // Add the message to local state immediately
      const newMessage = {
        id: responseData.message_id,
        text: text,  // 改用 text 而不是 message
        sender: walletAddress,  // 改用 sender 而不是 user_address
        username: username,
        timestamp: new Date().toLocaleTimeString(),  // 使用本地时间格式
        stance: stance,
        round: round
      };

      setMessages(prevMessages => [...prevMessages, newMessage]);
      
      return responseData;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const loadMessages = async (discussion_id) => {
    try {
      setIsLoading(true);
      const response = await fetch(`${API_CONFIG.BACKEND_URL}/msg/${discussion_id}`);
      if (!response.ok) {
        throw new Error('Failed to load messages');
      }
      const data = await response.json();
      // 转换消息格式
      const formattedMessages = data.map(msg => ({
        id: msg.id,
        text: msg.message,
        sender: msg.user_address,
        username: msg.username || 'Anonymous',
        timestamp: new Date(msg.timestamp).toLocaleTimeString(),
        stance: msg.stance,
        round: msg.round || 1
      }));
      setMessages(formattedMessages);
      return formattedMessages;
    } catch (error) {
      console.error('Error loading messages:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    messages,
    setMessages,
    addMessage,
    loadMessages,
    isLoading
  };
};
