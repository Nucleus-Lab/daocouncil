import React from 'react';
import { getInitials, getAvatarColor } from '../utils/avatarUtils';
import aiJurorImage from '../assets/character.png';

const UserAvatar = ({ name, size = 'normal' }) => {
  const initials = getInitials(name);
  const bgColor = getAvatarColor(name);
  const sizeClasses = size === 'small' ? 'w-6 h-6 text-xs' : 'w-8 h-8 text-sm';
  
  const isAIJuror = name.toLowerCase().includes('judge');
  
  if (isAIJuror) {
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

export default UserAvatar;
