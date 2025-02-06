import { CANVAS_WIDTH, CANVAS_HEIGHT } from '../constants/dimensions';
import { logger } from '../utils/logger';

class CourtroomScene {
    constructor(engine) {
        this.engine = engine;
        this.background = new Image();
        this.background.src = '/src/assets/bg.jpg';
        this.isLoaded = false;

        this.background.onload = () => {
            this.isLoaded = true;
            logger.info('Courtroom background loaded');
        };
    }

    initialize() {
        this.engine.canvas.width = CANVAS_WIDTH;
        this.engine.canvas.height = CANVAS_HEIGHT;
        logger.info('Courtroom scene initialized');
    }

    render(ctx) {
        if (this.isLoaded) {
            // Calculate scaling to fit the image while maintaining aspect ratio
            const scale = Math.min(
                CANVAS_WIDTH / this.background.width,
                CANVAS_HEIGHT / this.background.height
            );

            // Calculate dimensions after scaling
            const scaledWidth = this.background.width * scale;
            const scaledHeight = this.background.height * scale;

            // Calculate positioning to center the image
            const x = (CANVAS_WIDTH - scaledWidth) / 2;
            const y = (CANVAS_HEIGHT - scaledHeight) / 2;

            // Fill the background first
            ctx.fillStyle = '#2c1810';
            ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

            // Draw the background
            ctx.drawImage(
                this.background,
                x, y,
                scaledWidth,
                scaledHeight
            );

            logger.debug(`Background rendered at (${x}, ${y}) with dimensions ${scaledWidth}x${scaledHeight}`);
        } else {
            // Draw a placeholder background if image hasn't loaded
            ctx.fillStyle = '#2c1810';
            ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
        }
    }
}

export default CourtroomScene; 