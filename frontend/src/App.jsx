import React, { useState, useEffect } from 'react';
import bgImage from './assets/bg.jpg';
import aiJurorImage from './assets/character.png';
import characterSprite from './assets/character.png';

const App = () => {
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [jurorOpinions, setJurorOpinions] = useState([]);
  const [currentRound, setCurrentRound] = useState(1);
  const [userStance, setUserStance] = useState(''); // 'yes', 'no', or ''
  const [participantCounter, setParticipantCounter] = useState(1);
  const [walletConnected, setWalletConnected] = useState(false);
  const [isJurorOpinionsExpanded, setIsJurorOpinionsExpanded] = useState(false);
  const demoWalletAddress = "0x1234...5678";

  // Helper function to get initials from name
  const getInitials = (name) => {
    return name
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase();
  };

  // Helper function to get avatar background color based on name
  const getAvatarColor = (name) => {
    const colors = [
      'bg-blue-500', 'bg-green-500', 'bg-yellow-500', 'bg-purple-500',
      'bg-pink-500', 'bg-indigo-500', 'bg-red-500', 'bg-teal-500'
    ];
    const index = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return colors[index % colors.length];
  };

  // Avatar component
  const UserAvatar = ({ name, size = 'normal' }) => {
    const initials = getInitials(name);
    const bgColor = getAvatarColor(name);
    const sizeClasses = size === 'small' ? 'w-6 h-6 text-xs' : 'w-8 h-8 text-sm';
    
    // Check if it's an AI Juror
    const isAIJuror = name.toLowerCase().includes('judge');
    
    if (isAIJuror) {
      // Use larger size for AI Jurors in the opinions section
      const aiJurorSize = size === 'small' ? 'w-8 h-8' : 'w-10 h-10';
      return (
        <div className={`${aiJurorSize} overflow-hidden flex-none`}>
          <img 
            src={aiJurorImage} 
            alt={name}
            className="w-full h-full object-contain"
            style={{
              imageRendering: 'pixelated'
            }}
          />
        </div>
      );
    }

    return (
      <div className={`${sizeClasses} ${bgColor} rounded-full flex items-center justify-center text-white font-medium flex-none`}>
        {initials}
      </div>
    );
  };

  // Initialize with demo content
  useEffect(() => {
    setMessages([
      {
        id: 1,
        text: "Today we are discussing about Cardano's future. The two sides are Yes (Change voting to participation-based) and No (Keep ADA-based voting).",
        sender: 'Moderator',
        timestamp: '4:00 PM',
        stance: null,
        isSystem: true
      },
      {
        id: 2,
        text: "The current voting mechanism based on ADA holdings creates an oligarchy where wealthy token holders have disproportionate power. By shifting to participation-based voting, we can ensure more diverse voices are heard.",
        sender: 'Alice',
        timestamp: '4:02 PM',
        stance: 'yes',
        round: 1
      },
      {
        id: 3,
        text: "ADA-based voting ensures stakeholders with the most investment in the ecosystem's success have appropriate influence. These holders have strong financial incentive to make good decisions.",
        sender: 'Bob',
        timestamp: '4:03 PM',
        stance: 'no',
        round: 1
      },
      {
        id: 4,
        text: "I'm still researching both sides of the argument. Both have valid points about governance.",
        sender: 'Charlie',
        timestamp: '4:04 PM',
        stance: '',
        round: 1
      },
      {
        id: 5,
        text: "We've seen examples in other DAOs where wealth-based voting led to decisions favoring large holders at the expense of the broader community. Look at what happened with MakerDAO.",
        sender: 'David',
        timestamp: '4:05 PM',
        stance: 'yes',
        round: 1
      },
      {
        id: 6,
        text: "But participation-based voting could be easily manipulated through sock puppet accounts and artificial engagement. How would we prevent that?",
        sender: 'Eve',
        timestamp: '4:06 PM',
        stance: 'no',
        round: 1
      },
      {
        id: 7,
        text: "We could implement a reputation system combined with proof-of-personhood to prevent manipulation. Several projects are already working on this.",
        sender: 'Alice',
        timestamp: '4:07 PM',
        stance: 'yes',
        round: 1
      },
      {
        id: 8,
        text: "The technology for secure reputation-based voting exists. Zero-knowledge proofs could help verify participation while preserving privacy.",
        sender: 'Frank',
        timestamp: '4:08 PM',
        stance: 'yes',
        round: 1
      },
      {
        id: 9,
        text: "Cardano's methodical approach to development is a key strength. Major governance changes should only happen with overwhelming consensus.",
        sender: 'Bob',
        timestamp: '4:09 PM',
        stance: 'no',
        round: 1
      },
      {
        id: 10,
        text: "What about a hybrid system? Keep some voting power tied to ADA holdings but add weight for active participation and contributions?",
        sender: 'Grace',
        timestamp: '4:10 PM',
        stance: '',
        round: 1
      },
      {
        id: 11,
        text: "After reviewing the arguments, I'm leaning towards supporting the change. The risks of plutocracy seem greater than the implementation challenges.",
        sender: 'Charlie',
        timestamp: '4:11 PM',
        stance: 'yes',
        round: 1
      },
      {
        id: 12,
        text: "We could start with a pilot program in certain governance decisions to test the new system before full implementation.",
        sender: 'David',
        timestamp: '4:12 PM',
        stance: 'yes',
        round: 1
      },
      {
        id: 13,
        text: "The current system isn't perfect, but it's proven stable. We should focus on improving delegation and voter participation instead of a complete overhaul.",
        sender: 'Eve',
        timestamp: '4:13 PM',
        stance: 'no',
        round: 1
      }
    ]);

    // Initial juror opinions
    setJurorOpinions([
      {
        id: 1,
        juror: 'Judge 1',
        opinion: "As a Cardano holder, I believe in decentralized governance and community-driven decision making. The proposal to shift voting power from ADA holdings to participation resonates with these values.",
        vote: 'yes',
        score: 85
      },
      {
        id: 2,
        juror: 'Judge 2',
        opinion: "From an investor's perspective focusing on long-term value creation, a more equitable and participatory governance model could foster better growth.",
        vote: 'yes',
        score: 75
      },
      {
        id: 3,
        juror: 'Judge 3',
        opinion: "Given the emphasis on formal verification and security, maintaining the current stable system aligns better with these priorities.",
        vote: 'no',
        score: 65
      }
    ]);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!currentMessage.trim()) return;

    const newParticipantNumber = participantCounter;
    setParticipantCounter(prev => prev + 1);

    setMessages([...messages, {
      id: Date.now(),
      text: currentMessage,
      sender: `Participant ${newParticipantNumber}`,
      timestamp: new Date().toLocaleTimeString(),
      stance: userStance,
      round: currentRound
    }]);
    
    setCurrentMessage('');
  };

  const handleConnectWallet = () => {
    setWalletConnected(true);
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-gray-100 overflow-hidden">
      {/* Header */}
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
                onClick={handleConnectWallet}
                className="text-xs font-medium bg-amber-600 hover:bg-amber-700 text-white px-3 py-1 transition-colors"
              >
                Connect Wallet
        </button>
            )}
          </div>
        </div>
      </header>

      <main className="flex-1 flex p-1 gap-1 min-h-0">
        {/* Left Column */}
        <div className="w-[50%] flex flex-col gap-1 min-h-0">

          {/* Court Image with Overlay Bar */}
          <div className="relative h-[55%] bg-white shadow-lg overflow-hidden flex-none">
            {/* Character Sprite */}
            <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-12 h-12 z-[5]">
              <img 
                src={characterSprite}
                alt="Character"
                className="w-full h-full object-cover"
                style={{
                  imageRendering: 'pixelated',
                  transform: 'scale(1.75)'
                }}
              />
            </div>

            {/* Inclination Bar Overlay */}
            <div className="absolute bottom-0 left-0 right-0 z-10 bg-gray-900/90 py-1 px-2 backdrop-blur-sm">
              <div className="flex items-center gap-1.5">
                <div className="text-green-400 text-[10px] font-['Source_Code_Pro',monospace]">YES</div>
                <div className="flex-1 h-1 bg-gray-800 overflow-hidden relative">
                  {/* Calculate the percentage based on juror votes and scores */}
                  {(() => {
                    const totalScore = jurorOpinions.reduce((acc, opinion) => acc + opinion.score, 0);
                    const yesScore = jurorOpinions
                      .filter(opinion => opinion.vote === 'yes')
                      .reduce((acc, opinion) => acc + opinion.score, 0);
                    const percentage = (yesScore / totalScore) * 100;

                    return (
                      <>
                        <div 
                          className="absolute inset-y-0 left-0 bg-green-500 transition-all duration-500"
                          style={{ width: `${percentage}%` }}
                        />
                        <div 
                          className="absolute inset-y-0 right-0 bg-red-500 transition-all duration-500"
                          style={{ width: `${100 - percentage}%`, left: `${percentage}%` }}
                        />
                      </>
                    );
                  })()}
                </div>
                <div className="text-red-400 text-[10px] font-['Source_Code_Pro',monospace]">NO</div>
              </div>
            </div>

            <img 
              src={bgImage} 
              alt="Virtual Courtroom" 
              className="w-full h-full object-cover"
            />
      </div>

          {/* AI Jurors Opinions */}
          <div className={`font-['Source_Code_Pro','IBM_Plex_Mono',monospace] antialiased ${isJurorOpinionsExpanded ? 'fixed inset-4 z-50 bg-gradient-to-br from-gray-900 to-court-brown shadow-2xl p-4' : 'flex-1 h-[45%] bg-gradient-to-br from-gray-900 to-court-brown shadow-lg p-1.5'} min-h-0 flex flex-col transition-all duration-300`}>
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
              {jurorOpinions.map((opinion, index) => (
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
        </div>

        {/* Right Column - Discord-like Chat */}
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
      </main>
    </div>
  );
};

export default App;
