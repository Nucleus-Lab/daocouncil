import React, { useEffect, useRef, useState, useCallback } from 'react';
import GameEngine from '../game/engine/GameEngine';
import CourtroomScene from '../game/scenes/CourtroomScene';
import JurorSprite from '../game/sprites/JurorSprite';
import JudgeSprite from '../game/sprites/JudgeSprite';
import { POSITIONS, SPRITE_WIDTH, SPRITE_HEIGHT } from '../game/constants/dimensions';
import { JUROR_CONFIG, JUDGE_COMMANDS, VOTE_DELAY } from '../game/constants/game';
import { BUTTON_STYLES } from '../game/constants/ui';
import { logger } from '../game/utils/logger';
import { ASSETS } from '../game/constants/assets';  // Import ASSETS instead of direct image import

const CourtRoom = ({ onJurorVote, onWebSocketInit }) => {
    const canvasRef = useRef(null);
    const engineRef = useRef(null);
    const [isLoading, setIsLoading] = useState(true);

    // 初始化游戏引擎
    useEffect(() => {
        if (!canvasRef.current) return;

        const initializeGame = () => {
            // Set canvas size
            canvasRef.current.width = POSITIONS.CANVAS_WIDTH;
            canvasRef.current.height = POSITIONS.CANVAS_HEIGHT;

            const engine = new GameEngine(canvasRef.current);
            const scene = new CourtroomScene(engine);

            // Load and set background image
            const bgImage = new Image();
            bgImage.src = ASSETS.BACKGROUND;  // Use path from ASSETS
            bgImage.onload = () => {
                scene.setBackground(bgImage);
                setIsLoading(false);
                logger.info('Background image loaded successfully');
            };
            bgImage.onerror = (error) => {
                logger.error('Error loading background image:', error);
                setIsLoading(false);
            };

            engine.setScene(scene);
            scene.initialize();

            engineRef.current = engine;
            return engine;
        };

        const setupSprites = (engine) => {
            // Calculate positions for jurors
            const totalWidth = SPRITE_WIDTH * 7;
            const leftOffset = SPRITE_WIDTH * - 0.45;
            const startX = (POSITIONS.CENTER.x - (totalWidth / 2)) - leftOffset;
            const spacing = SPRITE_WIDTH * 1.28;
            
            // Adjust vertical positions for taller sprites
            const judgeY = POSITIONS.CENTER.y - SPRITE_HEIGHT * 0.3;  // Adjusted for taller sprites
            const jurorY = POSITIONS.CENTER.y + SPRITE_HEIGHT * 1.5; // Adjusted for taller sprites

            // Create and position judge - move left by adding an offset
            const judgeXOffset = SPRITE_WIDTH * 0.03; // Adjust this value to move judge more/less left
            const judge = new JudgeSprite(
                POSITIONS.CENTER.x - (SPRITE_WIDTH/2) - judgeXOffset, // Subtract offset to move left
                judgeY
            );
            engine.sprites.set('judge', judge);

            // Create and position jurors
            JUROR_CONFIG.forEach((juror) => {
                const sprite = new JurorSprite(
                    juror.id,
                    startX + (spacing * juror.order),
                    jurorY,
                    juror.character
                );
                engine.sprites.set(juror.id, sprite);
            });

            logger.debug('Sprites positioned with new scale - Judge at Y:', judgeY, 'Jurors at Y:', jurorY);
        };

        const engine = initializeGame();
        setupSprites(engine);
        engine.start();

        return () => engine.stop();
    }, []);

    // Memoize handleVote
    const handleVote = useCallback((jurorId, vote) => {
        console.log('CourtRoom: Handling vote for juror:', jurorId, 'vote:', vote);  
        if (!engineRef.current) {
            console.warn('Game engine not initialized');  
            return;
        }
        
        // Map server juror index (0-4) to sprite ID (juror1-juror5)
        const spriteId = `juror${parseInt(jurorId) + 1}`;
        console.log('Mapped jurorId to spriteId:', spriteId);  
        
        // 确保精灵存在
        const sprite = engineRef.current.sprites.get(spriteId);
        if (!sprite) {
            console.warn(`Sprite not found for juror ${spriteId}`);
            return;
        }

        // 如果精灵正在动画中，先重置
        if (sprite.isJumping || sprite.showSpeech) {
            sprite.isJumping = false;
            sprite.showSpeech = false;
            sprite.y = sprite.initialY;
        }

        // 触发动画
        engineRef.current.handleJurorVote(spriteId, vote);
        
        // 通知父组件
        if (onJurorVote) {
            onJurorVote(handleVote);
        }
    }, [onJurorVote]);

    // 在组件挂载和 handleVote 更新时注册回调函数
    useEffect(() => {
        console.log('CourtRoom: Setting up handlers');
        if (onJurorVote) {
            console.log('Registering vote handler with parent');
            onJurorVote(handleVote);
        }
    }, [handleVote, onJurorVote]);

    const handleJudgeCommand = useCallback((command) => {
        if (!engineRef.current) return;
        engineRef.current.handleJudgeSpeak(command);
    }, []);

    // 在组件挂载时注册回调函数
    useEffect(() => {
        console.log('CourtRoom: Setting up handlers');
        if (onWebSocketInit) {
            console.log('Registering judge command handler');
            onWebSocketInit(handleJudgeCommand);
        }
    }, [onWebSocketInit, handleJudgeCommand]);

    return (
        <div className="relative w-full h-full bg-court-brown flex items-center justify-center">
            {isLoading && (
                <div className="absolute inset-0 flex items-center justify-center bg-court-brown">
                    <p className="text-white">Loading courtroom...</p>
                </div>
            )}
            <div className="relative w-full h-full">
                <canvas
                    ref={canvasRef}
                    className="w-full h-full"
                    style={{ imageRendering: 'pixelated' }}
                />
            </div>
        </div>
    );
};

export default CourtRoom;
