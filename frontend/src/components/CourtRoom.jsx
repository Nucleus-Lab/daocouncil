import React, { useEffect, useRef, useState } from 'react';
import GameEngine from '../game/engine/GameEngine';
import CourtroomScene from '../game/scenes/CourtroomScene';
import JurorSprite from '../game/sprites/JurorSprite';
import JudgeSprite from '../game/sprites/JudgeSprite';
import { POSITIONS, SPRITE_WIDTH, SPRITE_HEIGHT } from '../game/constants/dimensions';
import { JUROR_CONFIG, JUDGE_COMMANDS, VOTE_DELAY } from '../game/constants/game';
import { BUTTON_STYLES } from '../game/constants/ui';
import { logger } from '../game/utils/logger';
import { ASSETS } from '../game/constants/assets';  // Import ASSETS instead of direct image import

const CourtRoom = () => {
    const canvasRef = useRef(null);
    const engineRef = useRef(null);
    const [isLoading, setIsLoading] = useState(true);

    // Initialize game engine
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

            // Create and position judge
            const judge = new JudgeSprite(
                POSITIONS.CENTER.x - (SPRITE_WIDTH/2),
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

    const handleVote = (vote) => {
        if (!engineRef.current) return;

        JUROR_CONFIG.forEach((juror, index) => {
            setTimeout(() => {
                engineRef.current.handleJurorVote(juror.id, vote);
            }, index * VOTE_DELAY);
        });
    };

    const handleJudgeCommand = (command) => {
        if (!engineRef.current) return;
        engineRef.current.handleJudgeSpeak(command);
    };

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
