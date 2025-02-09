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

      // 转换数据格式并更新状态
      const formattedHistory = {};
      historyData.forEach((jurorResults, jurorId) => {
        if (Array.isArray(jurorResults)) {  // 确保 jurorResults 是数组
          jurorResults.forEach(result => {
            const key = `${jurorId}-${result.latest_msg_id}`;
            formattedHistory[key] = {
              jurorId: String(jurorId),
              result: result.result,
              reasoning: result.reasoning,
              timestamp: new Date(result.created_at).toISOString(),
              messageId: result.latest_msg_id
            };
          });
        }
      });

      setJurorOpinions(formattedHistory);
      return historyData;
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
