export const CANVAS_WIDTH = 800;
export const CANVAS_HEIGHT = 600;
export const BASE_SPRITE_WIDTH = 16;  // Updated to match actual sprite size
export const BASE_SPRITE_HEIGHT = 17;  // Updated to match actual sprite size
export const SPRITE_SCALE = 3;  // Increased from 2 to 3 for larger, clearer sprites
export const SPRITE_WIDTH = BASE_SPRITE_WIDTH * SPRITE_SCALE;
export const SPRITE_HEIGHT = BASE_SPRITE_HEIGHT * SPRITE_SCALE;

export const POSITIONS = {
    CANVAS_WIDTH,
    CANVAS_HEIGHT,
    CENTER: {
        x: CANVAS_WIDTH / 2,
        y: CANVAS_HEIGHT * 0.45  // Position slightly above center
    }
}; 