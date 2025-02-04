import React from 'react';

const Header = ({ onConnectWallet, walletAddress, debateId }) => {
  return (
    <header className="bg-gradient-to-r from-[#fdf6e3] to-[#f5e6d3] shadow-sm border-b border-[#d4a762]/20">
      <div className="w-full px-8">
        <div className="relative w-full flex items-center justify-between h-16">
          {/* Title and Debate ID */}
          <div className="flex items-center space-x-4">
            <a
              href="/"
              className="text-[#2c1810] hover:text-[#4a3223] px-3 py-2 rounded-md text-lg font-medium transition-colors"
            >
              DAO Council
            </a>
            {debateId && (
              <div className="flex items-center">
                <div className="h-4 w-px bg-[#d4a762]/30" />
                <div className="flex items-center space-x-2 ml-4">
                  <span className="text-sm font-medium text-[#6b4423]">Debate ID:</span>
                  <code className="px-2 py-1 text-sm font-medium text-[#4a3223] bg-[#2c1810]/5 rounded-md border border-[#d4a762]/30">
                    {debateId}
                  </code>
                </div>
              </div>
            )}
          </div>

          {/* Wallet Connection */}
          <div className="flex items-center">
            {walletAddress ? (
              <div className="flex items-center gap-2 px-3 py-1.5 bg-[#2c1810]/5 rounded-lg border border-[#d4a762]/30">
                <div className="w-2 h-2 rounded-full bg-[#78a055]" />
                <span className="text-sm font-medium text-[#4a3223]">
                  {`${walletAddress.slice(0, 6)}...${walletAddress.slice(-4)}`}
                </span>
              </div>
            ) : (
              <button
                onClick={onConnectWallet}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-[#78a055] to-[#6b8c47] text-[#f5e6d3] rounded-lg hover:from-[#6b8c47] hover:to-[#5d7a3e] transition-all shadow-sm hover:shadow focus:outline-none focus:ring-2 focus:ring-[#78a055] focus:ring-offset-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
                Connect Wallet
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
