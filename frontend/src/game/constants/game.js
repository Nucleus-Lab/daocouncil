// Game-specific constants
export const JUROR_CONFIG = [
    { id: 'juror1', character: 'F_01', order: 0 },
    { id: 'juror2', character: 'M_01', order: 1 },
    { id: 'juror3', character: 'M_02', order: 2 },
    { id: 'juror4', character: 'F_02', order: 3 },
    { id: 'juror5', character: 'F_03', order: 4 }
];

export const JUDGE_COMMANDS = {
    START: 'START',
    MINT_NFT: 'MINTED NFT',
    TRANSFER: 'TRANSFERRED',
    END: 'END'
};

export const VOTE_DELAY = 300; // ms between each juror vote 