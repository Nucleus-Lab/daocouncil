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

  return {
    jurorOpinions,
    setJurorOpinions,
    isJurorOpinionsExpanded,
    setIsJurorOpinionsExpanded,
    fetchJurorResponse,
    isLoading
  };
};
