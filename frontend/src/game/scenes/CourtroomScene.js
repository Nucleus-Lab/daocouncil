import { CANVAS_WIDTH, CANVAS_HEIGHT } from '../constants/dimensions';
import { logger } from '../utils/logger';
import { ASSETS } from '../constants/assets';

class CourtroomScene {
    constructor(engine) {
        this.engine = engine;
        this.background = null;
    }

    setBackground(image) {
        this.background = image;
        logger.info('Background image set');
    }

    draw(ctx) {
        // Draw background first
        if (this.background) {
            ctx.drawImage(
                this.background, 
                0, 
                0, 
                this.engine.canvas.width, 
                this.engine.canvas.height
            );
        }
        
        // Draw other sprites and elements
        // ... rest of your drawing code
    }

    initialize() {
        this.engine.canvas.width = CANVAS_WIDTH;
        this.engine.canvas.height = CANVAS_HEIGHT;
        logger.info('Courtroom scene initialized');
    }

    render(ctx) {
        if (this.background) {
            // Fill the background first
            ctx.fillStyle = '#2c1810';
            ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

            // Get the actual canvas dimensions from the DOM
            const canvasRect = this.engine.canvas.getBoundingClientRect();
            const canvasAspectRatio = canvasRect.width / canvasRect.height;
            
            // Calculate scaling to fit the width while maintaining aspect ratio
            const scale = CANVAS_WIDTH / this.background.width;
            
            // Calculate the portion of the image to show based on canvas aspect ratio
            const sourceHeight = this.background.height * (canvasAspectRatio / (this.background.width / this.background.height));
            
            // Calculate the middle portion to show
            const sourceY = (this.background.height - sourceHeight) / 2;

            // Draw the middle portion of the background
            ctx.drawImage(
                this.background,
                0,                      // source x
                sourceY,                // source y - start from the middle portion
                this.background.width,  // source width
                sourceHeight,          // source height - adjusted for aspect ratio
                0,                      // destination x
                0,                      // destination y
                CANVAS_WIDTH,           // destination width
                CANVAS_HEIGHT           // destination height
            );

            logger.debug(`Background rendered with scale ${scale}, sourceY: ${sourceY}, aspect ratio: ${canvasAspectRatio}`);
        } else {
            // Draw a placeholder background if image hasn't loaded
            ctx.fillStyle = '#2c1810';
            ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
        }
    }
}

export default CourtroomScene; 