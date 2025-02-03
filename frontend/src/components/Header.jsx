import React from 'react';

const Header = ({ walletConnected, demoWalletAddress, onConnectWallet }) => {
  return (
    <header className="bg-court-brown text-white py-1.5 px-3 shadow-lg flex-none">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        <h1 className="text-xl font-bold tracking-wide">DAOCouncil Virtual Court</h1>
        <div>
          {walletConnected ? (
            <div className="flex items-center gap-1.5 bg-court-brown border border-amber-200 px-2 py-0.5">
              <div className="w-1.5 h-1.5 bg-green-400"></div>
              <span className="text-xs font-medium text-amber-200">{demoWalletAddress}</span>
            </div>
          ) : (
            <button
              onClick={onConnectWallet}
              className="text-xs font-medium bg-amber-600 hover:bg-amber-700 text-white px-3 py-1 transition-colors"
            >
              Connect Wallet
            </button>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
