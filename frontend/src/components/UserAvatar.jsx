import React from 'react';
import { getInitials, getAvatarColor } from '../utils/avatarUtils';
import aiJurorImage from '../assets/character.png';

const UserAvatar = ({ name = '?', size = 'normal' }) => {
  const isAIJuror = name?.toLowerCase()?.includes('judge') || false;
  const sizeClasses = size === 'small' ? 'w-8 h-8' : 'w-10 h-10';

  if (isAIJuror) {
    return (
      <div className={`${sizeClasses} overflow-hidden flex-none`}>
        <img 
          src={aiJurorImage} 
          alt={name || 'AI Judge'}
          className="w-full h-full object-contain"
          style={{
            imageRendering: 'pixelated'
          }}
        />
      </div>
    );
  }

  // 选择以下任一头像服务（取消注释你想要的那个）：

  // 1. Boring Avatars - 现代艺术风格（推荐）
  // const avatarUrl = `https://source.boringavatars.com/beam/120/${encodeURIComponent(name)}?colors=78a055,c15b3f,4f95a3,8b6943,d4a762`;

  // 2. UI Avatars - 简洁的文字头像
  // const avatarUrl = `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=fdf6e3&color=2c1810&bold=true&format=svg`;

  // 3. Robohash - 可爱的机器人头像
  // const avatarUrl = `https://robohash.org/${encodeURIComponent(name)}?set=set3&bgset=bg2&size=120x120`;

  // 4. DiceBear Pixel Art - 像素艺术风格
  const avatarUrl = `https://api.dicebear.com/7.x/pixel-art/svg?seed=${encodeURIComponent(name)}&backgroundColor=b6e3f4,c0aede,d1d4f9`;

  // 5. DiceBear Avataaars - 卡通人物风格
  // const avatarUrl = `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(name)}&backgroundColor=b6e3f4,c0aede,d1d4f9`;

  // 6. DiceBear Thumbs - 可爱的拇指人风格
  // const avatarUrl = `https://api.dicebear.com/7.x/thumbs/svg?seed=${encodeURIComponent(name)}&backgroundColor=b6e3f4,c0aede,d1d4f9`;

  // 7. DiceBear Fun Emoji - 有趣的表情符号风格
  // const avatarUrl = `https://api.dicebear.com/7.x/fun-emoji/svg?seed=${encodeURIComponent(name)}&backgroundColor=b6e3f4,c0aede,d1d4f9`;

  return (
    <div className={`${sizeClasses} rounded-lg overflow-hidden flex-none ring-2 ring-[#d4a762]/30 bg-[#fdf6e3]`}>
      <img
        src={avatarUrl}
        alt={name}
        className="w-full h-full object-cover"
        loading="lazy"
      />
    </div>
  );
};

export default UserAvatar;
