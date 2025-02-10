import React, { useRef } from 'react';

const CourtRoom = ({ handleJurorVote, handleJudgeCommand, onCanvasReady }) => {
    const canvasRef = useRef(null);

    // Set up canvas ref callback
    const setCanvasRef = (element) => {
        canvasRef.current = element;
        if (element) {
            onCanvasReady(element);
        }
    };

    // Add debug buttons for development
    const debugButtons = process.env.NODE_ENV === 'development' ? (
        <>
            <div className="absolute top-4 left-4 space-x-2 z-10">
                <button 
                    className="px-2 py-1 bg-blue-500 text-white rounded"
                    onClick={() => handleJurorVote(0, 0)}
                >
                    Test Juror 1
                </button>
                <button 
                    className="px-2 py-1 bg-green-500 text-white rounded"
                    onClick={() => handleJurorVote(1, 1)}
                >
                    Test Juror 2
                </button>
            </div>
            <div className="absolute top-4 right-4 space-x-2 z-10">
                <button 
                    className="px-2 py-1 bg-yellow-500 text-white rounded"
                    onClick={() => handleJudgeCommand("TEST")}
                >
                    Test Judge
                </button>
            </div>
        </>
    ) : null;

    return (
        <div className="relative w-full h-full bg-court-brown flex items-center justify-center">
            {debugButtons}
            <div className="relative w-full h-full">
                <canvas
                    ref={setCanvasRef}
                    className="w-full h-full"
                    style={{ imageRendering: 'pixelated' }}
                />
            </div>
        </div>
    );
};

export default CourtRoom;
