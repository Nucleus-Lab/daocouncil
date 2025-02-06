export const CANVAS_WIDTH = 800;
export const CANVAS_HEIGHT = 600;
export const BASE_SPRITE_WIDTH = 32;  // Original sprite width
export const BASE_SPRITE_HEIGHT = 32; // Original sprite height
export const SPRITE_SCALE = 2.5;  // Increase from default (likely 2.0)
export const SPRITE_WIDTH = BASE_SPRITE_WIDTH * SPRITE_SCALE;
export const SPRITE_HEIGHT = BASE_SPRITE_HEIGHT * SPRITE_SCALE;

export const POSITIONS = {
    CANVAS_WIDTH,
    CANVAS_HEIGHT,
    CENTER: {
        x: CANVAS_WIDTH / 2,
        y: CANVAS_HEIGHT / 2
    }
}; 