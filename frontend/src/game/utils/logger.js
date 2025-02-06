export const logger = {
    debug: (message) => {
        console.debug(`[Game] ${message}`);
    },
    info: (message) => {
        console.info(`[Game] ${message}`);
    },
    warn: (message) => {
        console.warn(`[Game] ${message}`);
    },
    error: (message) => {
        console.error(`[Game] ${message}`);
    }
}; 