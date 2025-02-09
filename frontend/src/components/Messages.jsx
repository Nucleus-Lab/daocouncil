import React, { useState, useRef, useEffect } from 'react';
import UserAvatar from './UserAvatar';

const Messages = ({
  messages = [],  // 添加默认值
  currentMessage,
  setCurrentMessage,
  onSubmit,
  userStance,
  setUserStance,
  debateSides = [{ id: '1', name: 'Side 1' }, { id: '2', name: 'Side 2' }, { id: '3', name: 'Side 3' }]  // Default values
}) => {
  const messageInputRef = useRef(null);
  const messagesEndRef = useRef(null);
  const [isPinnedMessageExpanded, setIsPinnedMessageExpanded] = useState(true);

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submitMessage();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submitMessage();
    }
  };

  const submitMessage = () => {
    if (currentMessage.trim()) {
      const messageData = {
        text: currentMessage,
        stance: userStance
      };
      onSubmit(messageData);
      setCurrentMessage('');
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // 在消息列表更新时滚动到底部
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 在当前消息更新时滚动到底部
  useEffect(() => {
    if (currentMessage) {
      scrollToBottom();
    }
  }, [currentMessage]);

  return (
    <div className="h-full flex flex-col p-2 bg-gradient-to-br from-[#fdf6e3] to-[#f5e6d3]">
      <h2 className="flex-none text-lg font-bold mb-2 text-[#2c1810] flex items-center gap-2">
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
        Debate Chat
      </h2>
      
      {/* Pinned Message */}
      {messages[0] && (
        <div className="flex-none mb-3 bg-gradient-to-br from-[#fdf6e3] to-[#f5e6d3] rounded-lg shadow-sm p-3">
        <div className="flex gap-3">
          <UserAvatar name="Moderator" size="small" />
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <svg className="w-4 h-4 text-[#d4a762]" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M5 4a2 2 0 012-2h6a2 2 0 012 2v14l-5-2.5L5 18V4z" />
                </svg>
                <span className="text-xs font-medium text-[#d4a762]">PINNED</span>
                <span className="font-semibold text-[#2c1810]">Judge Agent</span>
                <span className="text-xs text-[#6b4423]">{messages[0]?.timestamp}</span>
              </div>
              <button 
                onClick={() => setIsPinnedMessageExpanded(!isPinnedMessageExpanded)}
                className="text-[#6b4423] hover:text-[#2c1810] transition-colors"
              >
                <svg className={`w-5 h-5 transform transition-transform ${isPinnedMessageExpanded ? '' : 'rotate-180'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            </div>
            {isPinnedMessageExpanded && messages[0] && (
              <div className="text-sm text-[#4a3223] mt-1.5 space-y-2 flex-1">
                {messages[0].text && (
                  <div className="space-y-1">
                    <div className="flex items-start gap-2">
                      <span className="font-medium">Debate Topic:</span>
                      <span className="text-[#2c1810]">{messages[0].text.split('\nAction:')[0]?.replace(/^(Topic:|Debate Topic:)/i, '').trim()}</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="font-medium">Action:</span>
                      <span className="text-[#2c1810]">{messages[0].text.split('\nAction:')[1]?.trim()}</span>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
      )}

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto min-h-0 space-y-2 mb-3 pr-2">
        {messages?.slice(1)?.map((message) => message && debateSides && (
          <div
            key={message.id}
            className={`group p-3 bg-gradient-to-br from-[#fdf6e3] to-[#f5e6d3] rounded-lg shadow-sm hover:shadow-md transition-shadow ${message.stance && debateSides[0] ? 'border-l-4 ' + (
              message.stance === (debateSides[0]?.id || '1')
                ? 'border-[#78a055]' // 农场绿
                : message.stance === (debateSides[1]?.id || '2')
                ? 'border-[#c15b3f]' // 红土色
                : message.stance === (debateSides[2]?.id || '3')
                ? 'border-[#4f95a3]' // 湖水蓝
                : 'border-[#8b6943]' // 土色
            ) : ''}`}
          >
            <div className="flex gap-3">
              <UserAvatar name={message.sender} />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-[#2c1810]">
                    {message.username || 'Anonymous'} 
                    {message.sender !== 'Moderator' && (
                      <span className="text-sm font-normal text-[#6b4423] ml-1">
                        ({message.sender})
                      </span>
                    )}
                  </span>
                  {message.stance && (
                    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                      message.stance === (debateSides[0]?.id || '1')
                        ? 'bg-[#78a055]/10 text-[#78a055]'
                        : message.stance === (debateSides[1]?.id || '2')
                        ? 'bg-[#c15b3f]/10 text-[#c15b3f]'
                        : message.stance === (debateSides[2]?.id || '3')
                        ? 'bg-[#4f95a3]/10 text-[#4f95a3]'
                        : 'bg-[#8b6943]/10 text-[#8b6943]'
                    }`}>
                      {debateSides.find(side => side.id === message.stance)?.name}
                    </span>
                  )}
                  <span className="text-xs text-[#6b4423]">{message.timestamp}</span>
                </div>
                <p className="text-sm text-[#4a3223] mt-1.5 leading-relaxed whitespace-pre-wrap break-words">
                  {message.text}
                </p>
              </div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} /> {/* 添加一个空的div作为滚动目标 */}
      </div>

      {/* Message Input */}
      <div className="flex-none bg-gradient-to-r from-[#fdf6e3] to-[#f5e6d3] p-4 rounded-lg shadow-sm">
        {/* Stance Selection */}
        <div className="mb-4 flex items-center gap-3">
          <span className="text-sm font-medium text-[#6b4423]">Your Stance:</span>
          <div className="flex gap-2">
            {debateSides.map((side) => (
              <button
                key={side.id}
                onClick={() => setUserStance(side.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  userStance === side.id
                    ? side.id === debateSides[0].id
                      ? 'bg-[#78a055] text-white'
                      : side.id === debateSides[1].id
                      ? 'bg-[#c15b3f] text-white'
                      : side.id === debateSides[2].id
                      ? 'bg-[#4f95a3] text-white'
                      : 'bg-[#8b6943] text-white'
                    : 'bg-[#fdf6e3] text-[#6b4423] border border-[#d4a762] hover:bg-[#f5e6d3]'
                }`}
              >
                {side.name}
              </button>
            ))}
          </div>
        </div>

        <div className="flex gap-3">
          <div className="flex-1 relative">
            <textarea
              ref={messageInputRef}
              value={currentMessage}
              onChange={(e) => setCurrentMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your message..."
              className="w-full px-4 py-3 bg-[#fdf6e3] rounded-lg border border-[#d4a762] text-[#2c1810] placeholder-[#8b6943] focus:outline-none focus:ring-2 focus:ring-[#78a055] focus:border-transparent resize-none"
              rows={1}
            />
          </div>
          <button
            onClick={submitMessage}
            disabled={!currentMessage.trim()}
            className="flex-none flex items-center justify-center w-14 h-[42px] rounded-lg bg-[#78a055] hover:bg-[#6b8c47] text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <svg className="w-7 h-7 transform rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Messages;
