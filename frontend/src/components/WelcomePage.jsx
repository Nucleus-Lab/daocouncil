import React from 'react';

const WelcomePage = ({ onCreateDebate, onJoinDebate, isWalletConnected, onConnectWallet }) => {
  const handleAction = (action) => {
    if (!isWalletConnected) {
      onConnectWallet();
      return;
    }
    action();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-court-brown flex flex-col items-center justify-center p-4">
      {/* Connect Wallet Button */}
      <div className="absolute top-4 right-4">
        <button
          onClick={onConnectWallet}
          className="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors"
        >
          {isWalletConnected ? "0x1234...5678" : "Connect Wallet"}
        </button>
      </div>

      {/* Welcome Content */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-amber-200 mb-4">Welcome to DAO Council</h1>
        <p className="text-lg text-amber-100/80">Your decentralized platform for structured debates and decision-making</p>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col gap-4 w-full max-w-md">
        <button
          onClick={() => handleAction(onCreateDebate)}
          className="px-6 py-4 bg-amber-200 text-court-brown font-semibold rounded-lg hover:bg-amber-300 transition-colors"
        >
          Create New Debate
        </button>
        <button
          onClick={() => handleAction(onJoinDebate)}
          className="px-6 py-4 bg-gray-800 text-amber-200 font-semibold rounded-lg hover:bg-gray-700 transition-colors border border-amber-200/20"
        >
          Join Existing Debate
        </button>
      </div>
    </div>
  );
};

export default WelcomePage;
