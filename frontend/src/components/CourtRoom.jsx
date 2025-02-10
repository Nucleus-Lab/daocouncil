import React, { useRef } from 'react';

const CourtRoom = React.memo(({ handleJurorVote, handleJudgeCommand, onCanvasReady }) => {
    const canvasRef = useRef(null);

    // Set up canvas ref callback
    const setCanvasRef = (element) => {
        canvasRef.current = element;
        if (element) {
            onCanvasReady(element);
        }
    };


    return (
        <div className="relative w-full h-full bg-court-brown flex items-center justify-center">
            <div className="relative w-full h-full">
                <canvas
                    ref={setCanvasRef}
                    className="w-full h-full"
                    style={{ imageRendering: 'pixelated' }}
                />
            </div>
        </div>
    );
}, (prevProps, nextProps) => {
    // Custom comparison function to determine if component should update
    return (
        prevProps.handleJurorVote === nextProps.handleJurorVote &&
        prevProps.handleJudgeCommand === nextProps.handleJudgeCommand &&
        prevProps.onCanvasReady === nextProps.onCanvasReady
    );
});

export default CourtRoom;
