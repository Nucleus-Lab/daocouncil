import React, { useState, useEffect } from 'react';
import { ASSETS } from '../game/constants/assets';
import { SPRITE_IMAGES } from '../game/constants/sprites';
import { API_CONFIG } from '../config/api';

const LoadingScreen = ({ onLoadComplete, debateId }) => {
  const [progress, setProgress] = useState(0);
  const [loadedAssets, setLoadedAssets] = useState(new Set());
  const [loadingStage, setLoadingStage] = useState('assets'); // 'assets' | 'history' | 'complete'
  const [error, setError] = useState(null);
  
  const allAssets = {
    ...ASSETS,
    ...SPRITE_IMAGES
  };
  const totalAssets = Object.values(allAssets).length;
  const totalStages = debateId ? 3 : 1; // 如果有 debateId，需要加载资源、消息历史和陪审团历史

  // 计算总进度
  const calculateTotalProgress = (assetProgress, historyProgress = 0, jurorProgress = 0) => {
    if (!debateId) return assetProgress;
    return (assetProgress + historyProgress + jurorProgress) / totalStages;
  };

  useEffect(() => {
    const loadAssets = async () => {
      const loadImage = (src) => {
        return new Promise((resolve, reject) => {
          const img = new Image();
          img.src = src;
          img.onload = () => {
            setLoadedAssets(prev => {
              const newSet = new Set(prev);
              newSet.add(src);
              // 更新资源加载进度
              const assetProgress = (newSet.size / totalAssets) * 100;
              setProgress(calculateTotalProgress(assetProgress));
              return newSet;
            });
            resolve(img);
          };
          img.onerror = (error) => {
            console.error(`Failed to load image: ${src}`, error);
            reject(new Error(`Failed to load image: ${src}`));
          };
        });
      };

      try {
        // 1. 加载图片资源
        setLoadingStage('assets');
        await Promise.all(Object.values(allAssets).map(loadImage));
        
        if (!debateId) {
          setLoadingStage('complete');
          onLoadComplete();
          return;
        }

        // 2. 加载消息历史
        setLoadingStage('history');
        const messagePromise = fetch(`${API_CONFIG.BACKEND_URL}/msg/${debateId}`);
        setProgress(calculateTotalProgress(100, 50));

        // 3. 加载陪审团历史
        const jurorPromise = fetch(`${API_CONFIG.BACKEND_URL}/juror_results/${debateId}`);
        setProgress(calculateTotalProgress(100, 100, 50));

        // 等待所有历史记录加载完成
        const [messageResponse, jurorResponse] = await Promise.all([
          messagePromise,
          jurorPromise
        ]);

        if (!messageResponse.ok || !jurorResponse.ok) {
          throw new Error('Failed to load debate history');
        }

        setProgress(100);
        setLoadingStage('complete');
        onLoadComplete();
      } catch (error) {
        console.error('Error loading:', error);
        setError(error.message);
      }
    };

    loadAssets();
  }, [debateId, onLoadComplete, totalAssets, totalStages]);

  const getLoadingMessage = () => {
    switch (loadingStage) {
      case 'assets':
        return 'Loading court room assets...';
      case 'history':
        return 'Loading debate history...';
      case 'complete':
        return 'Loading complete!';
      default:
        return 'Loading...';
    }
  };

  return (
    <div className="fixed inset-0 bg-black/90 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-white mb-2">Loading Court Room</h2>
          <p className="text-gray-300">{getLoadingMessage()}</p>
        </div>

        {/* 进度条 */}
        <div className="w-full bg-gray-700 rounded-full h-4 overflow-hidden">
          <div 
            className="bg-court-brown h-full transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* 加载详情 */}
        <div className="text-center text-gray-400">
          {loadingStage === 'assets' && (
            <p>Loading assets: {loadedAssets.size} / {totalAssets}</p>
          )}
          <p>{Math.round(progress)}%</p>
        </div>

        {/* 加载动画 */}
        <div className="flex justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-court-brown"></div>
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="text-center text-red-500 mt-4">
            <p>{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-2 px-4 py-2 bg-court-brown text-white rounded-md hover:bg-court-brown-dark"
            >
              Retry
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default LoadingScreen;
