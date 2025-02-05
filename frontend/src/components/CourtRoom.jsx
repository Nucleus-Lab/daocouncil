import React, { useEffect, useRef } from 'react';
import GameEngine from '../game/engine/GameEngine';
import CourtroomScene from '../game/scenes/CourtroomScene';
import JurorSprite from '../game/sprites/JurorSprite';
import JudgeSprite from '../game/sprites/JudgeSprite';
import { POSITIONS, SPRITE_WIDTH, SPRITE_HEIGHT } from '../game/constants/dimensions';
import { JUROR_CONFIG, JUDGE_COMMANDS, VOTE_DELAY } from '../game/constants/game';
import { BUTTON_STYLES } from '../game/constants/ui';
import { logger } from '../game/utils/logger';

const CourtRoom = () => {
    const canvasRef = useRef(null);
    const engineRef = useRef(null);

    // Initialize game engine
    useEffect(() => {
        if (!canvasRef.current) return;

        const initializeGame = () => {
            // Set canvas size
            canvasRef.current.width = POSITIONS.CANVAS_WIDTH;
            canvasRef.current.height = POSITIONS.CANVAS_HEIGHT;

            const engine = new GameEngine(canvasRef.current);
            const scene = new CourtroomScene(engine);
            engine.setScene(scene);
            scene.initialize();

            engineRef.current = engine;
            return engine;
        };

        const setupSprites = (engine) => {
            // Calculate positions for jurors
            const totalWidth = SPRITE_WIDTH * 7;
            const startX = POSITIONS.CENTER.x - (totalWidth / 2);
            const spacing = SPRITE_WIDTH * 1.75;

            // Create and position judge
            const judge = new JudgeSprite(
                POSITIONS.CENTER.x - (SPRITE_WIDTH/2),
                POSITIONS.CENTER.y - SPRITE_HEIGHT * 2
            );
            engine.sprites.set('judge', judge);

            // Create and position jurors
            JUROR_CONFIG.forEach((juror) => {
                const sprite = new JurorSprite(
                    juror.id,
                    startX + (spacing * juror.order),
                    POSITIONS.CENTER.y - (SPRITE_HEIGHT/2),
                    juror.character
                );
                engine.sprites.set(juror.id, sprite);
            });
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
        <div className="relative w-full h-screen bg-court-brown flex items-center justify-center">
            <div className="relative w-[800px] h-[600px]">
                <canvas
                    ref={canvasRef}
                    className="w-full h-full"
                    style={{ imageRendering: 'pixelated' }}
                />
                
                {/* Vote Controls */}
                <div className="absolute top-4 left-4 space-x-2 z-10">
                    <button 
                        className={BUTTON_STYLES.vote1}
                        onClick={() => handleVote('1')}
                    >
                        Vote 1
                    </button>
                    <button 
                        className={BUTTON_STYLES.vote2}
                        onClick={() => handleVote('2')}
                    >
                        Vote 2
                    </button>
                    <button 
                        className={BUTTON_STYLES.vote3}
                        onClick={() => handleVote('3')}
                    >
                        Vote 3
                    </button>
                </div>

                {/* Judge Commands */}
                <div className="absolute top-4 right-4 space-x-2 z-10">
                    <button 
                        className={BUTTON_STYLES.judgeStart}
                        onClick={() => handleJudgeCommand(JUDGE_COMMANDS.START)}
                    >
                        Start
                    </button>
                    <button 
                        className={BUTTON_STYLES.judgeMint}
                        onClick={() => handleJudgeCommand(JUDGE_COMMANDS.MINT_NFT)}
                    >
                        Mint NFT
                    </button>
                    <button 
                        className={BUTTON_STYLES.judgeTransfer}
                        onClick={() => handleJudgeCommand(JUDGE_COMMANDS.TRANSFER)}
                    >
                        Transfer
                    </button>
                    <button 
                        className={BUTTON_STYLES.judgeEnd}
                        onClick={() => handleJudgeCommand(JUDGE_COMMANDS.END)}
                    >
                        End
                    </button>
                </div>

                {/* Debug Info */}
                <div className="absolute bottom-4 left-4 text-white text-sm">
                    <p>Sprite should be at: ({POSITIONS.CENTER.x}, {POSITIONS.CENTER.y})</p>
                </div>
            </div>
        </div>
    );
};

export default CourtRoom;
