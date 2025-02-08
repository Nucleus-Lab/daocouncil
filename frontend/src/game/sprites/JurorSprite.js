import { logger } from '../utils/logger';
import { 
    SPRITE_WIDTH, 
    SPRITE_HEIGHT, 
    BASE_SPRITE_WIDTH, 
    BASE_SPRITE_HEIGHT,
    SPRITE_SCALE 
} from '../constants/dimensions';

class JurorSprite {
    constructor(id, initialX, initialY, characterId = 'F_01') {
        this.id = id;
        this.x = initialX;
        this.y = initialY;
        this.initialY = initialY;  // Store initial Y position
        this.state = 'idle';
        this.characterId = characterId;
        
        // Speech bubble properties
        this.showSpeech = false;
        this.speechText = '';
        this.speechDuration = Infinity; // 设置为无限，让气泡保持显示
        this.speechCounter = 0;
        this.minSpeechTime = 60; // Keep minimum time at 1 second
        
        // Jump animation properties
        this.isJumping = false;
        this.jumpHeight = 10;  // Maximum jump height in pixels
        this.jumpCounter = 0;
        this.jumpDuration = 15;  // Duration of jump animation in frames
        
        // Load sprite image
        this.sprite = new Image();
        this.sprite.src = `src/assets/32_Characters/cropped/${characterId}/front_idle.png`;
        
        // Debug: Log when sprite is loaded
        this.sprite.onload = () => {
            logger.info(`Sprite image loaded successfully for ${characterId}`);
        };
        this.sprite.onerror = (e) => {
            logger.error(`Failed to load sprite image for ${characterId}:`, e);
        };
        
        logger.info(`Created ${characterId} juror at position (${initialX}, ${initialY})`);

        // Increase the height of the speech bubble even more
        this.speechBubbleHeight = 80; // Increased from 60 to 80
        this.speechBubbleWidth = 120; // Keep width the same
        this.speechBubbleY = initialY - this.speechBubbleHeight - 10;
    }

    speak(text) {
        this.showSpeech = true;
        this.speechText = text;
        this.speechCounter = this.speechDuration;
        
        // Start jump animation when speaking
        this.isJumping = true;
        this.jumpCounter = this.jumpDuration;
        
        logger.info(`Juror speaking: ${text}`);
    }

    update() {
        // 移除了 speech bubble 的消失逻辑，只保留跳动动画
        if (this.isJumping) {
            if (this.jumpCounter > 0) {
                // Parabolic jump motion
                const progress = (this.jumpDuration - this.jumpCounter) / this.jumpDuration;
                const jumpOffset = Math.sin(progress * Math.PI) * this.jumpHeight;
                this.y = this.initialY - jumpOffset;
                
                this.jumpCounter--;
            } else {
                this.isJumping = false;
                this.y = this.initialY;  // Reset to original position
            }
        }
    }

    draw(ctx) {
        if (this.sprite && this.sprite.complete) {
            ctx.save();
            
            // Disable image smoothing for crisp pixel art
            ctx.imageSmoothingEnabled = false;
            ctx.webkitImageSmoothingEnabled = false;
            ctx.mozImageSmoothingEnabled = false;
            ctx.msImageSmoothingEnabled = false;
            
            // Draw character sprite
            ctx.translate(this.x, this.y);
            ctx.scale(SPRITE_SCALE, SPRITE_SCALE);
            ctx.drawImage(
                this.sprite,
                0,
                0,
                BASE_SPRITE_WIDTH,
                BASE_SPRITE_HEIGHT
            );
            
            ctx.restore();

            // Draw speech bubble if active
            if (this.showSpeech) {
                this.drawSpeechBubble(ctx);
            }
        } else {
            // Fallback rectangle if sprite hasn't loaded
            ctx.fillStyle = '#FFD700';
            ctx.strokeStyle = '#000';
            ctx.lineWidth = 2;
            ctx.fillRect(this.x, this.y, SPRITE_WIDTH, SPRITE_HEIGHT);
            ctx.strokeRect(this.x, this.y, SPRITE_WIDTH, SPRITE_HEIGHT);
        }
    }

    drawSpeechBubble(ctx) {
        const bubbleWidth = 48;
        const bubbleHeight = 52;  // Increased from 32 to 52
        const pixelSize = 2;
        
        // Position bubble above sprite
        const bubbleX = this.x + SPRITE_WIDTH/2 - bubbleWidth/2;
        const bubbleY = this.y - bubbleHeight - 15;

        ctx.save();
        ctx.imageSmoothingEnabled = false;
        ctx.webkitImageSmoothingEnabled = false;
        ctx.mozImageSmoothingEnabled = false;

        // Generate pastel colors based on stance number
        const getStanceColors = (stance) => {
            // Convert stance to number (in case it's a string)
            const stanceNum = parseInt(stance);
            if (isNaN(stanceNum)) return { bg: '#FFFFFF', border: '#000000' };

            // Use HSL for easy pastel color generation
            // Start at 0 (red) and rotate around color wheel, skipping gold/yellow range
            let hue = (stanceNum * 100) % 360;  // Larger spacing between colors
            
            // Skip colors too close to judge's gold (around 45-65 degrees)
            if (hue > 30 && hue < 80) {
                hue += 50;  // Skip past the gold range
            }
            
            // Pastel background (adjusted saturation and lightness)
            const bg = `hsl(${hue}, 75%, 80%)`;
            // Slightly darker border
            const border = `hsl(${hue}, 80%, 70%)`;

            return { bg, border };
        };

        const voteColor = getStanceColors(this.speechText);

        // Draw bubble background
        ctx.fillStyle = voteColor.bg;
        ctx.fillRect(bubbleX + pixelSize, bubbleY + pixelSize, 
                    bubbleWidth - pixelSize*2, bubbleHeight - pixelSize*2);

        // Draw pixelated border
        ctx.fillStyle = voteColor.border;
        
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

        // Draw text - increase font size from 16px to 20px
        ctx.fillStyle = '#000000';
        ctx.font = "20px 'Press Start 2P', monospace";
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(
            this.speechText,  // Will show '1' or '2'
            bubbleX + bubbleWidth/2,
            bubbleY + bubbleHeight/2 - 2
        );

        ctx.restore();
    }
}

export default JurorSprite; 