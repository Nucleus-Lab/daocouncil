import React from 'react';
import UserAvatar from './UserAvatar';

const Messages = ({ 
  messages, 
  currentMessage, 
  setCurrentMessage, 
  handleSubmit, 
  userStance, 
  setUserStance 
}) => {
  return (
    <div className="w-[50%] bg-white shadow-lg p-1.5 flex flex-col min-h-0">
      <h2 className="text-lg font-bold mb-1.5 text-court-brown">Debate Chat</h2>
      
      {/* Pinned Message */}
      <div className="flex-none mb-1.5 bg-amber-50 border border-amber-200 p-1.5">
        <div className="flex gap-2">
          <UserAvatar name="Moderator" size="small" />
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-1.5">
              <div className="flex items-center gap-1.5">
                <svg className="w-3 h-3 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                </svg>
                <span className="text-xs font-medium text-amber-800">PINNED</span>
                <span className="font-semibold text-gray-900">Moderator</span>
              </div>
              <span className="text-xs text-gray-500">{messages[0]?.timestamp}</span>
            </div>
            <p className="text-sm text-gray-800 mt-1 leading-relaxed">{messages[0]?.text}</p>
          </div>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto space-y-1.5 mb-2 min-h-0 pr-1.5">
        {messages.slice(1).map((message) => (
          <div
            key={message.id}
            className="p-1.5 hover:bg-gray-50 flex gap-2"
          >
            <UserAvatar name={message.sender} />
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-1.5">
                <span className="font-semibold text-sm text-gray-900">
                  {message.sender}
                </span>
                {message.stance && (
                  <span className={`text-xs font-medium px-1.5 py-0.5 ${
                    message.stance === 'yes' 
                      ? 'bg-green-100 text-green-800'
                      : message.stance === 'no'
                      ? 'bg-red-100 text-red-800'
                      : ''
                  }`}>
                    {message.stance.toUpperCase()}
                  </span>
                )}
                <span className="text-xs text-gray-400">{message.timestamp}</span>
              </div>
              <p className="text-sm text-gray-800 mt-1 leading-relaxed">{message.text}</p>
            </div>
          </div>
        ))}
      </div>
      
      {/* Message Input with Stance */}
      <div className="flex-none">
        <div className="flex gap-1.5">
          <select
            value={userStance}
            onChange={(e) => setUserStance(e.target.value)}
            className="flex-none w-20 p-1.5 border focus:outline-none focus:ring-1 focus:ring-court-brown text-xs bg-white"
          >
            <option value="">No Stance</option>
            <option value="yes">Yes</option>
            <option value="no">No</option>
          </select>
          <input
            type="text"
            value={currentMessage}
            onChange={(e) => setCurrentMessage(e.target.value)}
            className="flex-1 p-1.5 border focus:outline-none focus:ring-1 focus:ring-court-brown text-xs"
            placeholder="Type your message..."
          />
          <button
            type="submit"
            onClick={handleSubmit}
            className="text-xs font-medium bg-court-brown text-white px-3 py-1.5 hover:bg-opacity-90 transition-colors"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default Messages;
