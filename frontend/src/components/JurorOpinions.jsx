import React from 'react';
import UserAvatar from './UserAvatar';

const JurorOpinions = ({ 
  jurorOpinions, 
  isJurorOpinionsExpanded, 
  setIsJurorOpinionsExpanded 
}) => {
  return (
    <div className={`font-['Source_Code_Pro','IBM_Plex_Mono',monospace] antialiased ${
      isJurorOpinionsExpanded 
        ? 'fixed inset-4 z-50 bg-gradient-to-br from-gray-900 to-court-brown shadow-2xl p-4' 
        : 'flex-1 h-[45%] bg-gradient-to-br from-gray-900 to-court-brown shadow-lg p-1.5'
    } min-h-0 flex flex-col transition-all duration-300`}>
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-sm text-amber-200 flex items-center gap-1 tracking-wide">
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          {'>>'} AI Jurors' Opinions
        </h2>
        <button
          onClick={() => setIsJurorOpinionsExpanded(!isJurorOpinionsExpanded)}
          className="text-sm text-amber-200 hover:text-amber-100 transition-colors bg-gray-900/50 px-1.5 py-0.5 border border-amber-200/20 flex items-center gap-1 tracking-wide"
          title={isJurorOpinionsExpanded ? "Minimize" : "Expand"}
        >
          {isJurorOpinionsExpanded ? (
            <>
              <span>[</span>
              <span>×</span>
              <span>]</span>
            </>
          ) : (
            <>
              <span>[</span>
              <span>□</span>
              <span>]</span>
            </>
          )}
        </button>
      </div>
      <div className={`flex-1 overflow-y-auto min-h-0 pr-1.5 ${isJurorOpinionsExpanded ? 'p-2' : ''}`}>
        {jurorOpinions.map((opinion) => (
          <div key={opinion.id} className="mb-2 last:mb-0">
            <div className="flex flex-col gap-1">
              <div className="flex items-center gap-2 text-amber-200">
                <UserAvatar name={opinion.juror} size="normal" />
                <span className="tracking-wide">{opinion.juror}</span>
                <span className="text-amber-200/30">─</span>
                <span className={`px-1.5 text-xs ${
                  opinion.vote === 'yes' 
                    ? 'text-green-300' 
                    : 'text-red-300'
                }`}>
                  {opinion.vote.toUpperCase()}
                </span>
                <span className="text-amber-200/30 text-xs">score: {opinion.score}/100</span>
              </div>
              <div className="text-gray-300 pl-1">
                <span className="text-amber-200/50">{'>'}{'>'}</span>
                <span className="ml-2 tracking-wide text-sm">{opinion.opinion}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default JurorOpinions;
