import { useState } from 'react';

export const useJurorOpinions = () => {
  const [jurorOpinions, setJurorOpinions] = useState({});
  const [isJurorOpinionsExpanded, setIsJurorOpinionsExpanded] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const fetchJurorResponse = async (messageId) => {
    try {
      setIsLoading(true);
      const response = await fetch(`http://localhost:8000/juror_response/${messageId}`, {
        method: 'POST',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to get juror response');
      }

      const responseData = await response.json();
      console.log('Juror response:', responseData);
      
      // Update juror opinions with the new responses
      setJurorOpinions(prevOpinions => ({
        ...prevOpinions,
        ...Object.entries(responseData).reduce((acc, [jurorId, data]) => ({
          ...acc,
          [jurorId]: {
            ...data,
            timestamp: new Date().toISOString()
          }
        }), {})
      }));

      return responseData;
    } catch (error) {
      console.error('Error getting juror response:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  // 新增：获取历史记录
  const fetchJurorHistory = async (discussionId) => {
    try {
      setIsLoading(true);
      // 将 discussionId 转换为整数
      const numericDiscussionId = parseInt(discussionId, 10);
      const response = await fetch(`http://localhost:8000/juror_results/${numericDiscussionId}`);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to get juror history');
      }

      const historyData = await response.json();
      console.log('Juror history:', historyData);

      // Get debate info to map result indices to side names
      const debateResponse = await fetch(`http://localhost:8000/debate/${discussionId}`);
      if (!debateResponse.ok) {
        throw new Error('Failed to get debate info');
      }
      const { debate } = await debateResponse.json();
      
      if (!debate || !debate.sides) {
        throw new Error('Debate info is missing sides data');
      }

      // 转换数据格式并更新状态
      const formattedHistory = {};
      const votingTrends = new Map();

      // Sort all results by message ID to ensure chronological order
      const allResults = [];
      historyData.forEach((jurorResults, jurorId) => {
        console.log(`Processing historical results for juror ${jurorId}:`, jurorResults);
        if (Array.isArray(jurorResults)) {
          jurorResults.forEach(result => {
            console.log(`Processing historical result:`, result);
            console.log(`Raw result value:`, result.result);
            let sideName;
            const sideIndex = result.result;

            // Check if result is a valid index in sides array
            if (sideIndex === -1) {
              sideName = "Undecided";
              console.log(`Historical vote marked as Undecided`);
            } else if (sideIndex >= 0 && sideIndex < debate.sides.length) {
              sideName = debate.sides[sideIndex];
              console.log(`Historical vote mapped to side: ${sideName}`);
            } else {
              console.error(`Invalid side index ${sideIndex} for debate sides:`, debate.sides);
              return; // Skip this invalid result
            }
            
            allResults.push({
              jurorId,
              messageId: result.latest_msg_id,
              result: sideIndex,
              sideName: sideName,
              reasoning: result.reasoning,
              timestamp: new Date(result.created_at)
            });
          });
        }
      });

      // Sort by message ID (which should correspond to chronological order)
      allResults.sort((a, b) => a.messageId - b.messageId);

      // Track votes per message
      const messageVotes = {};

      allResults.forEach(result => {
        const { messageId, sideName, jurorId } = result;

        // Initialize vote counts for this message if not exists
        if (!messageVotes[messageId]) {
          messageVotes[messageId] = {
            votes: {},
            jurors: new Set()
          };
          // Initialize all sides to 0
          debate.sides.forEach(side => {
            messageVotes[messageId].votes[side] = 0;
          });
          messageVotes[messageId].votes["Undecided"] = 0;
        }

        // Only count each juror once per message
        if (!messageVotes[messageId].jurors.has(jurorId)) {
          messageVotes[messageId].votes[sideName] = (messageVotes[messageId].votes[sideName] || 0) + 1;
          messageVotes[messageId].jurors.add(jurorId);
        }

        // Store in formatted history
        const key = `${result.jurorId}-${messageId}`;
        formattedHistory[key] = {
          jurorId: String(result.jurorId),
          result: sideName,
          stance: sideName,
          reasoning: result.reasoning,
          timestamp: result.timestamp.toISOString(),
          messageId: messageId
        };

        // Store votes for AI voting trends
        votingTrends.set(messageId, { ...messageVotes[messageId].votes });
      });

      setJurorOpinions(formattedHistory);

      // Convert votingTrends map to array format expected by AIVotingTrends
      const aiVotingTrendsData = Array.from(votingTrends.entries())
        .map(([messageId, votes]) => ({
          time: `Message ${messageId}`,
          votes: votes
        }));

      console.log('Formatted juror opinions:', formattedHistory);
      console.log('AI voting trends data:', aiVotingTrendsData);

      return {
        jurorHistory: historyData,
        aiVotingTrends: aiVotingTrendsData
      };
    } catch (error) {
      console.error('Error getting juror history:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    jurorOpinions,
    setJurorOpinions,
    isJurorOpinionsExpanded,
    setIsJurorOpinionsExpanded,
    fetchJurorResponse,
    fetchJurorHistory,  // 导出新函数
    isLoading
  };
};
