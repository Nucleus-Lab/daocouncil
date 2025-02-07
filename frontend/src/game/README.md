# Courtroom Game Logic

This folder contains the game engine and animation logic for the DAO Council courtroom.

## Structure
- `engine/` - Core game logic and state management
- `sprites/` - Character sprite animations and states
- `scenes/` - Game scene management
- `constants/` - Game-related constants and configurations
- `utils/` - Helper functions for game logic 


## Core Functions

### Juror Voting
To make jurors vote, use the GameEngine's handleJurorVote method:

```javascript
// Make a specific juror vote
engine.handleJurorVote(jurorId, voteNumber);
// Example:
engine.handleJurorVote('juror1', '1'); // Juror 1 votes for stance 1
engine.handleJurorVote('juror2', '2'); // Juror 2 votes for stance 2
```


The juror will:
- Jump animation when voting
- Show a colored speech bubble with the vote number
- Speech bubble color changes based on vote number
- Speech bubble stays visible for 3 seconds

### Judge Commands
To make the judge speak, use the GameEngine's handleJudgeSpeak method:

```javascript
// Make the judge announce something
engine.handleJudgeSpeak(command);
// Available commands:
engine.handleJudgeSpeak('START'); // Start the session
engine.handleJudgeSpeak('MINTED NFT'); // Announce NFT minting
engine.handleJudgeSpeak('TRANSFER'); // Announce transfer
engine.handleJudgeSpeak('END'); // End the session
```


The judge will:
- Show a gold speech bubble with the command text
- Speech bubble size adjusts to text length
- Speech bubble stays visible for 3 seconds

### Integration Notes
- Juror IDs are 'juror1' through 'juror5'
- Vote numbers can be any string/number (will generate unique colors)
- Judge commands should be predefined in JUDGE_COMMANDS
- All animations run at 60 FPS
- Speech bubbles have minimum display time of 1 second


# For DEV

Paste the following into `CourtRoom.jsx` to add buttons to the courtroom for testing:

```javascript
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

```





