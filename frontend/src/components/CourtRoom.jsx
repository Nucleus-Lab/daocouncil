import React from 'react';
import characterSprite from '../assets/character.png';
import bgImage from '../assets/bg.jpg';

const CourtRoom = ({ jurorOpinions }) => {
  const calculateVotePercentages = () => {
    const totalScore = jurorOpinions.reduce((acc, opinion) => acc + opinion.score, 0);
    const yesScore = jurorOpinions
      .filter(opinion => opinion.vote === 'yes')
      .reduce((acc, opinion) => acc + opinion.score, 0);
    return (yesScore / totalScore) * 100;
  };

  const percentage = calculateVotePercentages();

  return (
    <div className="relative h-full">
      {/* Background Image */}
      <img 
        src={bgImage} 
        alt="Virtual Courtroom" 
        className="absolute inset-0 w-full h-full object-cover"
      />

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
            <div 
              className="absolute inset-y-0 left-0 bg-green-500 transition-all duration-500"
              style={{ width: `${percentage}%` }}
            />
            <div 
              className="absolute inset-y-0 right-0 bg-red-500 transition-all duration-500"
              style={{ width: `${100 - percentage}%`, left: `${percentage}%` }}
            />
          </div>
          <div className="text-red-400 text-[10px] font-['Source_Code_Pro',monospace]">NO</div>
        </div>
      </div>
    </div>
  );
};

export default CourtRoom;
