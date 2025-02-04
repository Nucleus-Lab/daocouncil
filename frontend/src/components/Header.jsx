import React from 'react';

const Header = ({ walletConnected, walletAddress, onConnectWallet }) => {
  return (
    <header className="bg-white shadow-md p-4">
      <div className="container mx-auto flex justify-between items-center">
        <h1 className="text-xl font-bold">DAO Council</h1>
        <div>
          {walletConnected ? (
            <span className="px-4 py-2 bg-gray-100 rounded-full">
              {walletAddress ? walletAddress.slice(0, 6) + '...' + walletAddress.slice(-4) : 'Connected'}
            </span>
          ) : (
            <button
              className="bg-blue-500 text-white px-4 py-2 rounded-full hover:bg-blue-600"
              onClick={onConnectWallet}
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
