import { logger } from '../utils/logger';
import { POSITIONS } from '../constants/dimensions';

class GameEngine {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.sprites = new Map();
        this.isRunning = false;
        this.scene = null;
        
        // Bind the gameLoop
        this.gameLoop = this.gameLoop.bind(this);
    }

    setScene(scene) {
        this.scene = scene;
    }

    start() {
        if (!this.isRunning) {
            this.isRunning = true;
            this.gameLoop();
            logger.info('Game started');
        }
    }

    stop() {
        this.isRunning = false;
    }

    gameLoop() {
        if (!this.isRunning) return;

        this.update();
        this.render();
        window.requestAnimationFrame(this.gameLoop);
    }

    update() {
        for (const sprite of this.sprites.values()) {
            sprite.update();
        }
    }

    render() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        if (this.scene) {
            this.scene.render(this.ctx);
        }

        for (const sprite of this.sprites.values()) {
            sprite.draw(this.ctx);
        }
    }

    handleJurorVote(jurorId, vote) {
        console.log('GameEngine: Handling juror vote:', jurorId, vote);  
        const sprite = this.sprites.get(jurorId);
        if (!sprite) {
            console.warn(`Sprite not found for juror: ${jurorId}`);  
            console.log('Available sprites:', Array.from(this.sprites.keys()));  
            return;
        }

        // Show speech bubble with vote
        sprite.speak(vote);
    }

    handleJudgeSpeak(text) {
        const judge = this.sprites.get('judge');
        if (!judge) return;
        judge.speak(text);
    }
}

export default GameEngine; 