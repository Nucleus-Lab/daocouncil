import { useState } from 'react';

export const useJurorOpinions = () => {
  const [jurorOpinions, setJurorOpinions] = useState({});
  const [isJurorOpinionsExpanded, setIsJurorOpinionsExpanded] = useState(false);

  return {
    jurorOpinions,
    setJurorOpinions,
    isJurorOpinionsExpanded,
    setIsJurorOpinionsExpanded
  };
};
