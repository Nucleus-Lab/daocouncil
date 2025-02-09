import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import { API_CONFIG } from './config/api';
import LoadingScreen from './components/LoadingScreen';

// Components
import Header from './components/Header';
import CourtRoom from './components/CourtRoom';
import Messages from './components/Messages';
import JurorOpinions from './components/JurorOpinions';
import WelcomePage from './components/WelcomePage';
import CreateDebateForm from './components/CreateDebateForm';
import JoinDebateForm from './components/JoinDebateForm';
import UsernameSetup from './components/UsernameSetup';

// Hooks
import { useMessages } from './hooks/useMessages';
import { useJurorOpinions } from './hooks/useJurorOpinions';
import { useWebSocket } from './hooks/useWebSocket';

// Privy
import { usePrivy, useWallets } from '@privy-io/react-auth';

const App = () => {
  const { login, ready, authenticated, user, wallet } = usePrivy();
  const { wallets, ready: walletsReady } = useWallets();
  
  // State for debate management
  const [currentView, setCurrentView] = useState('welcome');
  const [walletConnected, setWalletConnected] = useState(false);
  const [walletAddress, setWalletAddress] = useState('');
  const [currentDebateId, setCurrentDebateId] = useState('');
  const [username, setUsername] = useState(() => {
    // 从 localStorage 读取缓存的用户名
    const cachedUsername = localStorage.getItem('username');
    return cachedUsername || '';
  });
  const [usernameSet, setUsernameSet] = useState(() => {
    // 从 localStorage 读取缓存的状态
    return !!localStorage.getItem('username');
  });
  const [debateSides, setDebateSides] = useState([
    { id: '1', name: 'Side 1' },
    { id: '2', name: 'Side 2' }
  ]);
  const [currentDebateInfo, setCurrentDebateInfo] = useState({}); 
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [userStance, setUserStance] = useState('');
  const [replyingTo, setReplyingTo] = useState(null);
  const demoWalletAddress = "0x1234...5678";
  const [isLoading, setIsLoading] = useState(false);

  const { addMessage, loadMessages } = useMessages(walletAddress, username);

  useEffect(() => {
    if (ready && authenticated && user?.wallet?.address) {
      setWalletConnected(true);
      setWalletAddress(user.wallet.address);
      
      // 先检查本地缓存
      const cachedUsername = localStorage.getItem('username');
      const cachedWallet = localStorage.getItem('walletAddress');
      
      if (cachedUsername && cachedWallet === user.wallet.address) {
        // 如果缓存存在且钱包地址匹配，直接使用缓存的用户名
        setUsername(cachedUsername);
        setUsernameSet(true);
      } else {
        // 如果没有缓存或钱包地址不匹配，则查询后端
        checkUsername(user.wallet.address);
      }
    } else {
      setWalletConnected(false);
      setWalletAddress('');
      setUsername('');
      setUsernameSet(false);
      // 清除缓存
      localStorage.removeItem('username');
      localStorage.removeItem('walletAddress');
    }
  }, [ready, authenticated, user]);

  useEffect(() => {
    if (walletsReady) {
      const externalWallet = wallets?.find(w => w.walletClientType !== 'privy');
      if (externalWallet) {
        setWalletAddress(externalWallet.address);
        setWalletConnected(true);
      } else {
        setWalletAddress('');
        setWalletConnected(false);
      }
    }
  }, [wallets, walletsReady]);

  const checkUsername = async (address) => {
    try {
      const response = await fetch(`${API_CONFIG.BACKEND_URL}/user/${address}`);
      if (response.ok) {
        const data = await response.json();
        if (data.username) {
          setUsername(data.username);
          setUsernameSet(true);
          // 缓存用户名和钱包地址
          localStorage.setItem('username', data.username);
          localStorage.setItem('walletAddress', address);
        }
      }
    } catch (error) {
      console.error('Error checking username:', error);
    }
  };

  const handleUsernameSet = (newUsername) => {
    setUsername(newUsername);
    setUsernameSet(true);
    // 缓存用户名和钱包地址
    localStorage.setItem('username', newUsername);
    localStorage.setItem('walletAddress', walletAddress);
  };

  // Existing state and hooks
  const {
    jurorOpinions,
    setJurorOpinions,
    isJurorOpinionsExpanded,
    setIsJurorOpinionsExpanded,
    fetchJurorResponse,
    fetchJurorHistory,
    isLoading: isJurorLoading
  } = useJurorOpinions();

  const [currentRound, setCurrentRound] = useState(1);

  // Add voting trends data
  const [votingTrends, setVotingTrends] = useState([
    { time: '4:00 PM', yes: 0, no: 0 },
    { time: '4:02 PM', yes: 2, no: 1 },
    { time: '4:04 PM', yes: 3, no: 2 },
    { time: '4:06 PM', yes: 4, no: 4 },
    { time: '4:08 PM', yes: 6, no: 5 },
    { time: '4:10 PM', yes: 8, no: 6 },
    { time: '4:12 PM', yes: 10, no: 7 },
    { time: '4:14 PM', yes: 12, no: 8 }
  ]);

  const [handleJurorVote, setHandleJurorVote] = useState(null);

  // Add AI voting trends state
  const [aiVotingTrends, setAiVotingTrends] = useState([]);

  // Memoize the callback
  const onJurorVote = useCallback((handleVote) => {
    setHandleJurorVote(() => handleVote);
  }, []); // Empty dependency array since it doesn't depend on any values

  // Initialize with demo content when joining existing debate
  const initializeDemoContent = () => {
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
  };

  // Update voting trends when new messages are added
  useEffect(() => {
    // 初始化或更新投票趋势
    const updateVotingTrends = () => {
      if (!messages.length) return;

      // 按时间排序消息
      const sortedMessages = [...messages].sort((a, b) => 
        new Date(a.timestamp) - new Date(b.timestamp)
      );

      // 计算每个时间点的累计投票
      const newTrends = [];
      let yesCount = 0;
      let noCount = 0;

      sortedMessages.forEach(msg => {
        if (msg.stance === 'yes') yesCount++;
        if (msg.stance === 'no') noCount++;
        
        newTrends.push({
          time: msg.timestamp,
          yes: yesCount,
          no: noCount
        });
      });

      // 更新投票趋势
      if (newTrends.length > 0) {
        setVotingTrends(newTrends);
      }
    };

    updateVotingTrends();
  }, [messages]);

  const handleConnectWallet = async () => {
    try {
      await login();
    } catch (error) {
      console.error('Error connecting wallet:', error);
    }
  };

  const handleCreateDebateSubmit = async (debateInfo) => {
    try {
      console.log('Received debate info:', debateInfo);  // 添加日志
      
      // 确保所有必要的字段都存在
      if (!debateInfo || !debateInfo.discussion_id || !debateInfo.sides) {
        throw new Error('Invalid debate information received');
      }

      // 先设置辩论信息
      const debateId = debateInfo.discussion_id.toString();
      setCurrentDebateId(debateId);
      setCurrentDebateInfo(debateInfo);
      
      // 更新 URL
      window.history.pushState({}, '', `/debate/${debateId}`);
      
      // 设置辩论双方
      const formattedSides = debateInfo.sides.map((side, index) => ({
        id: (index + 1).toString(),
        name: side
      }));
      setDebateSides(formattedSides);
      
      // 设置初始消息
      const initialMessage = `Debate Topic: ${debateInfo.topic}\nAction: ${debateInfo.action}`;
      await addMessage(initialMessage, null, 0, null, debateInfo);

      // 加载历史消息
      const response = await fetch(`${API_CONFIG.BACKEND_URL}/msg/${debateId}`);
      if (!response.ok) {
        throw new Error('Failed to load messages');
      }
      const messages = await response.json();
      let messageCounter = 0;
      setMessages(messages.map(msg => ({
        id: msg.id || `${Date.now()}-${messageCounter++}`,
        text: msg.message,
        sender: msg.user_address,
        username: msg.username || 'Anonymous',
        timestamp: new Date(msg.timestamp).toLocaleTimeString(),
        stance: msg.stance || 'neutral',
        round: msg.round || 1
      })));

      // 最后切换视图
      console.log('Switching to debate view');  // 添加日志
      setCurrentView('debate');
    } catch (error) {
      console.error('Error in handleCreateDebateSubmit:', error);
      alert('Failed to create debate: ' + error.message);  // 添加用户提示
    }
  };

  const handleJoinDebate = async ({ debateId, debateInfo }) => {
    setIsLoading(true);
    setCurrentDebateId(debateId);
    setCurrentDebateInfo(debateInfo);

    // 更新 URL
    window.history.pushState({}, '', `/debate/${debateId}`);

    // 加载历史消息
    try {
      const response = await fetch(`${API_CONFIG.BACKEND_URL}/msg/${debateId}`);
      if (!response.ok) {
        throw new Error('Failed to load messages');
      }
      const messages = await response.json();
      let messageCounter = 0;
      setMessages(messages.map(msg => ({
        id: msg.id || `${Date.now()}-${messageCounter++}`,
        text: msg.message,
        sender: msg.user_address,
        username: msg.username || 'Anonymous',
        timestamp: new Date(msg.timestamp).toLocaleTimeString(),
        stance: msg.stance || 'neutral',
        round: msg.round || 1
      })));

      // 获取 juror opinions 历史记录
      await fetchJurorHistory(debateId);
    } catch (error) {
      console.error('Error loading messages:', error);
      setIsLoading(false);
      return;
    }
    setIsLoading(false);
    setCurrentView('debate');
  };

  const handleLoadComplete = () => {
    setIsLoading(false);
    setCurrentView('debate');
  };

  // Handle real-time message updates
  const handleNewMessage = useCallback((messageData) => {
    setMessages(prevMessages => {
      // Check if message already exists
      if (prevMessages.some(msg => msg.id === messageData.id)) {
        return prevMessages;
      }

      const newMessage = {
        id: messageData.id,
        text: messageData.message,
        sender: messageData.user_address,
        username: messageData.username || 'Anonymous',
        timestamp: new Date(messageData.timestamp).toLocaleTimeString(),
        stance: messageData.stance,
        round: currentRound
      };

      return [...prevMessages, newMessage];
    });
  }, [currentRound]);

  // Handle real-time juror response updates
  const handleJurorResponse = useCallback((responseData) => {
    const { message_id, responses } = responseData;
    const timestamp = new Date().toLocaleTimeString();

    // Update juror opinions
    Object.entries(responses).forEach(([jurorId, data]) => {
      const newOpinion = {
        id: `${Date.now()}-${jurorId}`,
        jurorId,
        reasoning: data.reasoning,
        result: data.result,
        timestamp: timestamp
      };

      setJurorOpinions(prevOpinions => ({
        ...prevOpinions,
        [newOpinion.id]: newOpinion
      }));

      // Trigger voting animation
      if (handleJurorVote) {
        handleJurorVote(jurorId, data.result);
      }
    });

    // Update AI voting trends
    setAiVotingTrends(prevTrends => [
      ...prevTrends,
      {
        time: timestamp,
        votes: Object.values(responses).reduce((acc, curr) => {
          acc[curr.result] = (acc[curr.result] || 0) + 1;
          return acc;
        }, {})
      }
    ]);
  }, [handleJurorVote]);

  // WebSocket 连接
  const { connectWebSocket, disconnectWebSocket, isConnected } = useWebSocket(
    currentDebateId,
    walletAddress || 'anonymous',
    handleNewMessage,
    handleJurorResponse
  );

  // WebSocket 重连和历史记录获取
  useEffect(() => {
    if (currentDebateId && currentView === 'debate' && !isConnected) {
      // 连接 WebSocket
      connectWebSocket();
      
      // 获取历史记录
      fetchJurorHistory(currentDebateId).catch(error => {
        console.error('Error fetching juror history:', error);
      });
    }

    return () => {
      if (isConnected) {
        disconnectWebSocket();
      }
    };
  }, [currentDebateId, currentView, isConnected, connectWebSocket, disconnectWebSocket]);

  // 检查 URL 中的 debate ID
  useEffect(() => {
    const checkUrlForDebateId = async () => {
      const path = window.location.pathname;
      const match = path.match(/^\/debate\/(\d+)$/);
      
      if (match && match[1]) {
        const debateId = match[1];
        try {
          // 获取辩论信息
          const response = await fetch(`${API_CONFIG.BACKEND_URL}/debate/${debateId}`);
          if (!response.ok) {
            throw new Error('Debate not found');
          }
          const { debate, jurors } = await response.json();
          
          // 加入辩论
          await handleJoinDebate({
            debateId,
            debateInfo: {
              ...debate,
              jurors
            }
          });
        } catch (error) {
          console.error('Error loading debate from URL:', error);
          // 如果加载失败，重定向到首页
          window.history.pushState({}, '', '/');
          setCurrentView('welcome');
        }
      }
    };

    checkUrlForDebateId();
  }, []);  // 只在组件挂载时运行一次

  // Modify handleSubmitMessage to only handle message sending
  const handleSubmitMessage = async (messageData) => {
    try {
      // Just send the message - juror responses will come through WebSocket
      await addMessage(
        messageData.text,
        messageData.stance,
        currentRound,
        null,
        currentDebateInfo
      );
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  };

  // Render different views based on currentView state
  const renderView = () => {
    if (walletConnected && !usernameSet) {
      return (
        <UsernameSetup onSubmit={handleUsernameSet} walletAddress={walletAddress} />
      );
    }

    switch (currentView) {
      case 'welcome':
        return (
          <WelcomePage
            onCreateDebate={() => setCurrentView('create')}
            onJoinDebate={() => setCurrentView('joinForm')}
            isWalletConnected={walletConnected}
            walletAddress={walletAddress}
            onConnectWallet={handleConnectWallet}
            wallet={wallets?.[0]}
          />
        );
      case 'create':
        return (
          <CreateDebateForm
            onSubmit={handleCreateDebateSubmit}
            onCancel={() => setCurrentView('welcome')}
            walletAddress={walletAddress}
            username={username}
          />
        );
      case 'joinForm':
        return (
          <JoinDebateForm
            onSubmit={handleJoinDebate}
            onCancel={() => setCurrentView('welcome')}
            walletAddress={walletAddress}
            username={username}
          />
        );
      case 'debate':
        return (
          <div className="fixed inset-0 flex flex-col bg-gray-100">
            <Header 
              walletConnected={walletConnected}
              walletAddress={walletAddress}
              onConnectWallet={handleConnectWallet}
              debateId={currentDebateId}
            />

            <main className="flex-1 flex min-h-0 p-1 gap-1">
              {/* Left Column */}
              <div className="w-[50%] flex flex-col gap-1 min-h-0">
                {/* Court Room */}
                <div className="relative h-[55%] bg-white shadow-lg overflow-hidden">
                  <CourtRoom onJurorVote={onJurorVote} />
                </div>
                
                {/* AI Jurors Opinions */}
                <div className="h-[45%] min-h-0 flex-1">
                  <JurorOpinions 
                    jurorOpinions={jurorOpinions} 
                    isJurorOpinionsExpanded={isJurorOpinionsExpanded} 
                    setIsJurorOpinionsExpanded={setIsJurorOpinionsExpanded}
                    votingTrends={votingTrends}
                    messages={messages.map(msg => ({
                      ...msg,
                      replyTo: msg.replyTo ? messages.find(m => m.id === msg.replyTo.id) : null
                    }))}
                    debateSides={debateSides}
                    aiVotingTrends={aiVotingTrends}
                  />
                </div>
              </div>

              {/* Right Column - Discord-like Chat */}
              <div className="w-[50%] bg-white shadow-lg flex flex-col min-h-0">
                <Messages 
                  messages={messages.map(msg => ({
                    ...msg,
                    replyTo: msg.replyTo ? messages.find(m => m.id === msg.replyTo.id) : null
                  }))}
                  currentMessage={currentMessage}
                  setCurrentMessage={setCurrentMessage}
                  onSubmit={handleSubmitMessage}
                  userStance={userStance}
                  setUserStance={setUserStance}
                  debateSides={debateSides}
                />
              </div>
            </main>
          </div>
        );
      default:
        return null;
    }
  };

  if (isLoading) {
    return (
      <LoadingScreen 
        onLoadComplete={handleLoadComplete} 
        debateId={currentDebateId}
      />
    );
  }

  if (!ready || !walletsReady) {
    return (
      <LoadingScreen 
        onLoadComplete={() => {}} 
        debateId={currentDebateId}
      />
    );
  }

  return renderView();
};

export default App;
