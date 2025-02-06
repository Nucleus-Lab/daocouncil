import { AVATAR_COLORS } from '../constants/avatarColors';

export const getInitials = (name) => {
  if (!name) return '?';  // 处理 name 为空的情况
  
  return name
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase();
};

export const getAvatarColor = (name) => {
  if (!name) return AVATAR_COLORS[0];  // 处理 name 为空的情况
  
  const index = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return AVATAR_COLORS[index % AVATAR_COLORS.length];
};
