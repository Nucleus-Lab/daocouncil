import { logger } from '../utils/logger';
import { 
    SPRITE_WIDTH, 
    SPRITE_HEIGHT, 
    BASE_SPRITE_WIDTH, 
    BASE_SPRITE_HEIGHT,
    SPRITE_SCALE 
} from '../constants/dimensions';
import JurorSprite from './JurorSprite';

class JudgeSprite extends JurorSprite {
    constructor(initialX, initialY) {
        super('judge', initialX, initialY, 'M_03');
        this.zIndex = 2; // Higher z-index to render above jurors

        // Increase the height of the speech bubble even more
        this.speechBubbleHeight = 80; // Increased from 60 to 80
        this.speechBubbleWidth = 120; // Keep width the same
        this.speechBubbleY = initialY - this.speechBubbleHeight - 10;
    }

    // Override drawSpeechBubble to make it larger for longer text
    drawSpeechBubble(ctx) {
        const pixelSize = 2;
        const minBubbleWidth = 100;  // Minimum bubble width
        const bubbleHeight = 68;     // Increased from 48 to 68
        const padding = 24;  // Padding on each side of the text
        
        // Measure text width
        ctx.font = "18px 'Press Start 2P', monospace";
        const textWidth = ctx.measureText(this.speechText).width;
        
        // Calculate bubble width based on text (with minimum width)
        const bubbleWidth = Math.max(minBubbleWidth, textWidth + (padding * 2));
        
        // Position bubble above sprite
        const bubbleX = this.x + SPRITE_WIDTH/2 - bubbleWidth/2;
        const bubbleY = this.y - bubbleHeight - 25;

        ctx.save();
        ctx.imageSmoothingEnabled = false;
        ctx.webkitImageSmoothingEnabled = false;
        ctx.mozImageSmoothingEnabled = false;

        // Judge uses a consistent gold color scheme
        const judgeColors = {
            bg: '#FFE5B5',     // Soft gold
            border: '#FFD700'  // Darker gold
        };

        // Draw bubble background
        ctx.fillStyle = judgeColors.bg;
        ctx.fillRect(bubbleX + pixelSize, bubbleY + pixelSize, 
                    bubbleWidth - pixelSize*2, bubbleHeight - pixelSize*2);

        // Draw pixelated border
        ctx.fillStyle = judgeColors.border;
        
        // Draw all borders
        // Top border
        ctx.fillRect(bubbleX + pixelSize*2, bubbleY, bubbleWidth - pixelSize*4, pixelSize);
        // Bottom border
        ctx.fillRect(bubbleX + pixelSize*2, bubbleY + bubbleHeight - pixelSize, 
                    bubbleWidth - pixelSize*4, pixelSize);
        // Left border
        ctx.fillRect(bubbleX, bubbleY + pixelSize*2, pixelSize, 
                    bubbleHeight - pixelSize*4);
        // Right border
        ctx.fillRect(bubbleX + bubbleWidth - pixelSize, bubbleY + pixelSize*2, 
                    pixelSize, bubbleHeight - pixelSize*4);

        // Draw corners
        // Top-left
        ctx.fillRect(bubbleX + pixelSize, bubbleY + pixelSize, pixelSize, pixelSize);
        // Top-right
        ctx.fillRect(bubbleX + bubbleWidth - pixelSize*2, bubbleY + pixelSize, 
                    pixelSize, pixelSize);
        // Bottom-left
        ctx.fillRect(bubbleX + pixelSize, bubbleY + bubbleHeight - pixelSize*2, 
                    pixelSize, pixelSize);
        // Bottom-right
        ctx.fillRect(bubbleX + bubbleWidth - pixelSize*2, 
                    bubbleY + bubbleHeight - pixelSize*2, pixelSize, pixelSize);

        // Draw pixelated pointer
        const pointerX = bubbleX + bubbleWidth/2 - pixelSize*2;
        const pointerY = bubbleY + bubbleHeight;
        ctx.fillRect(pointerX, pointerY, pixelSize*4, pixelSize);
        ctx.fillRect(pointerX + pixelSize, pointerY + pixelSize, pixelSize*2, pixelSize);
        ctx.fillRect(pointerX + pixelSize*1.5, pointerY + pixelSize*2, pixelSize, pixelSize);

        // Draw text
        ctx.fillStyle = '#000000';
        // Font is already set above when measuring text
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(
            this.speechText,
            bubbleX + bubbleWidth/2,
            bubbleY + bubbleHeight/2
        );

        ctx.restore();
    }
}

export default JudgeSprite; 