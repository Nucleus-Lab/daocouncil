import React, { useState } from 'react';
import { useLogout, usePrivy } from '@privy-io/react-auth';

const WelcomePage = ({ onCreateDebate, onJoinDebate, isWalletConnected, walletAddress, onConnectWallet, wallet }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { logout } = useLogout({
    onSuccess: () => {
      console.log('Successfully logged out');
      // 清理本地状态
      localStorage.removeItem('username');
      localStorage.removeItem('walletAddress');
      setIsMenuOpen(false);
    }
  });

  const handleDisconnect = async () => {
    try {
      // 1. 尝试调用钱包的断开连接方法（如果支持）
      if (wallet?.disconnect) {
        try {
          await wallet.disconnect();
        } catch (error) {
          console.warn('Wallet disconnect failed, proceeding with logout:', error);
        }
      }
      
      // 2. 使用 Privy 的登出功能
      await logout();
      
    } catch (error) {
      console.error('Error disconnecting:', error);
      // 即使出错也关闭菜单
      setIsMenuOpen(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 bg-gradient-to-br from-gray-900 to-gray-800 flex flex-col items-center justify-center p-4 relative">
      <div className="absolute top-4 right-4">
        {isWalletConnected ? (
          <div className="relative">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="px-4 py-2 rounded-md bg-gray-800 text-gray-300 hover:bg-gray-700"
            >
              {walletAddress ? `${walletAddress.slice(0, 6)}...${walletAddress.slice(-4)}` : 'Connected'}
            </button>
            
            {/* 钱包菜单 */}
            {isMenuOpen && (
              <div className="absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-gray-800 ring-1 ring-black ring-opacity-5">
                <div className="py-1" role="menu" aria-orientation="vertical">
                  <button
                    onClick={handleDisconnect}
                    className="w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-gray-700"
                    role="menuitem"
                  >
                    Disconnect Wallet
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <button
            onClick={onConnectWallet}
            className="px-4 py-2 rounded-md bg-amber-500 text-gray-900 hover:bg-amber-400"
          >
            Connect Wallet
          </button>
        )}
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
