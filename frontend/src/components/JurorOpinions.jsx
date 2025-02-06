import React, { useState } from 'react';
import UserAvatar from './UserAvatar';
import VotingTrends from './VotingTrends';
import AIVotingTrends from './AIVotingTrends';

const JurorOpinions = ({ 
  jurorOpinions = {}, 
  isJurorOpinionsExpanded, 
  setIsJurorOpinionsExpanded,
  votingTrends,
  messages,
  debateSides,
  aiVotingTrends
}) => {
  const [currentView, setCurrentView] = useState('opinions'); // 'opinions' or 'trends'

  // Sort opinions by timestamp
  const sortedOpinions = Object.values(jurorOpinions)
    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

  return (
    <div className={`h-full font-['Source_Code_Pro','IBM_Plex_Mono',monospace] antialiased ${
      isJurorOpinionsExpanded 
        ? 'fixed inset-4 z-50 bg-gradient-to-br from-gray-900 to-court-brown shadow-2xl p-4' 
        : 'bg-gradient-to-br from-gray-900 to-court-brown shadow-lg p-1.5'
    } flex flex-col min-h-0`}>
      <div className="flex-none flex items-center justify-between mb-2">
        <h2 className="text-sm text-amber-200 flex items-center gap-1 tracking-wide">
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          {'>>'} {currentView === 'opinions' ? "AI Jurors' Opinions" : 'Voting Trends'}
        </h2>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setCurrentView(currentView === 'opinions' ? 'trends' : 'opinions')}
            className="text-sm text-amber-200 hover:text-amber-100 transition-colors bg-gray-900/50 px-1.5 py-0.5 border border-amber-200/20 flex items-center gap-1 tracking-wide"
            title="Switch View"
          >
            {currentView === 'opinions' ? (
              <>
                <span>[</span>
                <span>📈</span>
                <span>]</span>
              </>
            ) : (
              <>
                <span>[</span>
                <span>💭</span>
                <span>]</span>
              </>
            )}
          </button>
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
      </div>
      <div className={`flex-1 overflow-y-auto min-h-0 pr-1.5 ${isJurorOpinionsExpanded ? 'p-2' : ''}`}>
        {currentView === 'opinions' ? (
          <div className="flex-1 overflow-y-auto min-h-0 space-y-2">
            {sortedOpinions.map((opinion) => (
              <div key={opinion.id} className="p-3 bg-white/5 rounded">
                <div className="flex items-start">
                  <div className="flex-1">
                    <div className="flex justify-between items-center">
                      <h3 className="text-amber-200/90 text-sm">
                        Juror #{parseInt(opinion.jurorId) + 1}
                      </h3>
                      <span className="text-amber-50/40 text-xs">
                        {opinion.timestamp}
                      </span>
                    </div>
                    <p className="text-amber-50/80 text-sm mt-1">{opinion.reasoning}</p>
                    <p className="text-amber-50/60 text-xs mt-2">
                      Stance: {opinion.result}
                    </p>
                  </div>
                </div>
              </div>
            ))}
            {sortedOpinions.length === 0 && (
              <div className="text-amber-50/60 text-sm text-center p-4">
                No juror opinions yet. Start the debate to see their thoughts.
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            <VotingTrends 
              messages={messages} 
              debateSides={debateSides} 
              votingData={votingTrends} 
            />
            <AIVotingTrends aiVotingTrends={aiVotingTrends} />
          </div>
        )}
      </div>
    </div>
  );
};

export default JurorOpinions;
