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
  const [currentView, setCurrentView] = useState('opinions');
  const [selectedJuror, setSelectedJuror] = useState(null);

  // 获取每个 juror 的最新意见
  const latestOpinions = {};
  const jurorHistory = {};

  // 处理数据，按 juror 分组
  Object.values(jurorOpinions).forEach(opinion => {
    const jurorId = parseInt(opinion.jurorId);
    if (!jurorHistory[jurorId]) {
      jurorHistory[jurorId] = [];
    }
    jurorHistory[jurorId].push(opinion);

    // 更新最新意见
    if (!latestOpinions[jurorId] || new Date(opinion.timestamp) > new Date(latestOpinions[jurorId].timestamp)) {
      latestOpinions[jurorId] = opinion;
    }
  });

  // 对每个 juror 的历史记录按时间排序
  Object.keys(jurorHistory).forEach(jurorId => {
    jurorHistory[jurorId].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  });

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
          {'>>'} {selectedJuror !== null ? `Juror #${selectedJuror + 1} History` : "AI Jurors' Latest Opinions"}
        </h2>
        <div className="flex items-center gap-2">
          {selectedJuror !== null && (
            <button
              onClick={() => setSelectedJuror(null)}
              className="text-sm text-amber-200 hover:text-amber-100 transition-colors bg-gray-900/50 px-1.5 py-0.5 border border-amber-200/20 flex items-center gap-1 tracking-wide"
            >
              Back
            </button>
          )}
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
          selectedJuror !== null ? (
            // 显示选中 juror 的历史记录
            <div className="space-y-2">
              {jurorHistory[selectedJuror]?.map((opinion, index) => (
                <div key={index} className="p-3 bg-white/5 rounded">
                  <div className="flex items-start">
                    <div className="flex-1">
                      <div className="flex justify-between items-center">
                        <span className="text-amber-50/40 text-xs">
                          {new Date(opinion.timestamp).toLocaleTimeString()}
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
            </div>
          ) : (
            // 显示所有 juror 的最新意见
            <div className="grid grid-cols-1 gap-2">
              {Array.from({ length: 5 }, (_, i) => (
                <div 
                  key={i}
                  onClick={() => latestOpinions[i] && setSelectedJuror(i)}
                  className={`p-3 bg-white/5 rounded ${latestOpinions[i] ? 'cursor-pointer hover:bg-white/10' : 'opacity-50'}`}
                >
                  <div className="flex items-start">
                    <div className="flex-1">
                      <div className="flex justify-between items-center">
                        <h3 className="text-amber-200/90 text-sm">
                          Juror #{i + 1}
                        </h3>
                        {latestOpinions[i] && (
                          <span className="text-amber-50/40 text-xs">
                            {new Date(latestOpinions[i].timestamp).toLocaleTimeString()}
                          </span>
                        )}
                      </div>
                      {latestOpinions[i] ? (
                        <>
                          <p className="text-amber-50/80 text-sm mt-1 line-clamp-2">{latestOpinions[i].reasoning}</p>
                          <p className="text-amber-50/60 text-xs mt-2">
                            Stance: {latestOpinions[i].result}
                          </p>
                        </>
                      ) : (
                        <p className="text-amber-50/40 text-sm mt-1">No opinion yet</p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )
        ) : (
          <div className="space-y-4">
            <AIVotingTrends aiVotingTrends={aiVotingTrends} />
            <VotingTrends 
              messages={messages} 
              debateSides={debateSides} 
              votingData={votingTrends} 
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default JurorOpinions;
