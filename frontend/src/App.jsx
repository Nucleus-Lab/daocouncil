import React, { useState, useEffect } from 'react';
import './App.css';

// Components
import Header from './components/Header';
import CourtRoom from './components/CourtRoom';
import UserAvatar from './components/UserAvatar';
import Messages from './components/Messages';
import JurorOpinions from './components/JurorOpinions';

// Hooks
import { useMessages } from './hooks/useMessages';
import { useJurorOpinions } from './hooks/useJurorOpinions';

const App = () => {
  const {
    messages,
    setMessages,
    currentMessage,
    setCurrentMessage,
    addMessage
  } = useMessages();

  const {
    jurorOpinions,
    setJurorOpinions,
    isJurorOpinionsExpanded,
    setIsJurorOpinionsExpanded
  } = useJurorOpinions();

  const [currentRound, setCurrentRound] = useState(1);
  const [userStance, setUserStance] = useState('');
  const [walletConnected, setWalletConnected] = useState(false);
  const demoWalletAddress = "0x1234...5678";

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
    addMessage(currentMessage, userStance, currentRound);
  };

  const handleConnectWallet = () => {
    setWalletConnected(true);
  };

  return (
    <div className="fixed inset-0 flex flex-col bg-gray-100">
      <Header 
        walletConnected={walletConnected}
        demoWalletAddress={demoWalletAddress}
        onConnectWallet={handleConnectWallet}
      />

      <main className="flex-1 flex min-h-0 p-1 gap-1">
        {/* Left Column */}
        <div className="w-[50%] flex flex-col gap-1 min-h-0">
          {/* Court Room */}
          <div className="relative h-[55%] bg-white shadow-lg overflow-hidden">
            <CourtRoom jurorOpinions={jurorOpinions} />
          </div>
          
          {/* AI Jurors Opinions */}
          <div className="h-[45%] min-h-0 flex-1">
            <JurorOpinions 
              jurorOpinions={jurorOpinions} 
              isJurorOpinionsExpanded={isJurorOpinionsExpanded} 
              setIsJurorOpinionsExpanded={setIsJurorOpinionsExpanded} 
            />
          </div>
        </div>

        {/* Right Column - Discord-like Chat */}
        <div className="w-[50%] bg-white shadow-lg flex flex-col min-h-0">
          <Messages 
            messages={messages} 
            currentMessage={currentMessage} 
            setCurrentMessage={setCurrentMessage} 
            handleSubmit={handleSubmit} 
            userStance={userStance} 
            setUserStance={setUserStance} 
          />
        </div>
      </main>
    </div>
  );
};

export default App;
