import React from 'react';

const WelcomePage = ({ onCreateDebate, onJoinDebate, isWalletConnected, walletAddress, onConnectWallet }) => {
  return (
    <div className="min-h-screen bg-gray-900 bg-gradient-to-br from-gray-900 to-gray-800 flex flex-col items-center justify-center p-4 relative">
      <div className="absolute top-4 right-4">
        <button
          onClick={onConnectWallet}
          className={`px-4 py-2 rounded-md ${
            isWalletConnected 
              ? 'bg-gray-800 text-gray-300' 
              : 'bg-amber-500 text-gray-900 hover:bg-amber-400'
          }`}
        >
          {isWalletConnected 
            ? (walletAddress ? `${walletAddress.slice(0, 6)}...${walletAddress.slice(-4)}` : 'Connected') 
            : "Connect Wallet"}
        </button>
      </div>

      <div className="text-center space-y-12 max-w-xl">
        <div className="space-y-4">
          <h1 className="text-4xl font-bold text-amber-400">Welcome to DAO Council</h1>
          <p className="text-gray-400 text-lg">Your decentralized platform for structured debates and decision-making</p>
        </div>

        <div className="space-y-4 w-full max-w-md mx-auto">
          <button
            onClick={onCreateDebate}
            className="w-full bg-amber-400 text-gray-900 px-6 py-3 rounded-md hover:bg-amber-300 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={!isWalletConnected}
          >
            Create New Debate
          </button>
          <button
            onClick={onJoinDebate}
            className="w-full bg-gray-800 text-amber-400 px-6 py-3 rounded-md hover:bg-gray-700 transition-colors font-medium border border-amber-400/30 disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={!isWalletConnected}
          >
            Join Existing Debate
          </button>
        </div>
      </div>
    </div>
  );
};

export default WelcomePage;
