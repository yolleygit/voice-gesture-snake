class SnakeGame {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.gridSize = 20;
        this.snake = [{x: 15, y: 15}];
        this.direction = {x: 0, y: 0};
        this.food = this.generateFood();
        this.score = 0;
        this.gameLoop = null;
        this.isPaused = false;
        this.isGameOver = false;

        // 初始化控制按钮
        this.startBtn = document.getElementById('startBtn');
        this.pauseBtn = document.getElementById('pauseBtn');
        this.restartBtn = document.getElementById('restartBtn');
        this.gestureBtn = document.getElementById('gestureBtn');
        this.scoreElement = document.getElementById('score');

        // 初始化手势控制器
        this.gestureController = new GestureController(this);

        // 绑定事件处理
        this.bindEvents();
    }

    bindEvents() {
        // 键盘控制
        document.addEventListener('keydown', (e) => this.handleKeyPress(e));

        // 按钮控制
        this.startBtn.addEventListener('click', () => this.startGame());
        this.pauseBtn.addEventListener('click', () => this.togglePause());
        this.restartBtn.addEventListener('click', () => this.restartGame());
        this.gestureBtn.addEventListener('click', () => this.toggleGestureControl());

        // 触摸控制
        let touchStartX = 0;
        let touchStartY = 0;
        this.canvas.addEventListener('touchstart', (e) => {
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
        });

        this.canvas.addEventListener('touchmove', (e) => {
            e.preventDefault();
            if (this.isPaused || !this.gameLoop) return;

            const touchEndX = e.touches[0].clientX;
            const touchEndY = e.touches[0].clientY;
            const dx = touchEndX - touchStartX;
            const dy = touchEndY - touchStartY;

            if (Math.abs(dx) > Math.abs(dy)) {
                if (dx > 0 && this.direction.x === 0) this.direction = {x: 1, y: 0};
                else if (dx < 0 && this.direction.x === 0) this.direction = {x: -1, y: 0};
            } else {
                if (dy > 0 && this.direction.y === 0) this.direction = {x: 0, y: 1};
                else if (dy < 0 && this.direction.y === 0) this.direction = {x: 0, y: -1};
            }
        });
    }

    handleKeyPress(e) {
        if (this.isPaused || !this.gameLoop) return;

        switch (e.key) {
            case 'ArrowUp':
                if (this.direction.y === 0) this.direction = {x: 0, y: -1};
                break;
            case 'ArrowDown':
                if (this.direction.y === 0) this.direction = {x: 0, y: 1};
                break;
            case 'ArrowLeft':
                if (this.direction.x === 0) this.direction = {x: -1, y: 0};
                break;
            case 'ArrowRight':
                if (this.direction.x === 0) this.direction = {x: 1, y: 0};
                break;
        }
    }

    generateFood() {
        const maxX = this.canvas.width / this.gridSize - 1;
        const maxY = this.canvas.height / this.gridSize - 1;
        let food;
        do {
            food = {
                x: Math.floor(Math.random() * maxX),
                y: Math.floor(Math.random() * maxY)
            };
        } while (this.snake.some(segment => segment.x === food.x && segment.y === food.y));
        return food;
    }

    update() {
        if (this.isPaused || this.isGameOver) return;

        // 计算新的蛇头位置
        const head = {
            x: (this.snake[0].x + this.direction.x + this.canvas.width / this.gridSize) % (this.canvas.width / this.gridSize),
            y: (this.snake[0].y + this.direction.y + this.canvas.height / this.gridSize) % (this.canvas.height / this.gridSize)
        };

        // 检查碰撞
        if (this.snake.some(segment => segment.x === head.x && segment.y === head.y)) {
            this.gameOver();
            return;
        }

        // 移动蛇
        this.snake.unshift(head);

        // 检查是否吃到食物
        if (head.x === this.food.x && head.y === this.food.y) {
            this.score += 10;
            this.scoreElement.textContent = this.score;
            this.food = this.generateFood();
        } else {
            this.snake.pop();
        }
    }

    draw() {
        // 清空画布
        this.ctx.fillStyle = '#000';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // 绘制蛇
        this.ctx.fillStyle = '#0f0';
        this.snake.forEach(segment => {
            this.ctx.fillRect(
                segment.x * this.gridSize,
                segment.y * this.gridSize,
                this.gridSize - 2,
                this.gridSize - 2
            );
        });

        // 绘制食物
        this.ctx.fillStyle = '#f00';
        this.ctx.fillRect(
            this.food.x * this.gridSize,
            this.food.y * this.gridSize,
            this.gridSize - 2,
            this.gridSize - 2
        );

        // 游戏结束显示
        if (this.isGameOver) {
            this.ctx.fillStyle = '#fff';
            this.ctx.font = '48px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText('游戏结束!', this.canvas.width/2, this.canvas.height/2);
        }
    }

    startGame() {
        if (this.gameLoop) return;
        
        this.direction = {x: 1, y: 0};
        this.gameLoop = setInterval(() => {
            this.update();
            this.draw();
        }, 100);

        this.startBtn.disabled = true;
        this.pauseBtn.disabled = false;
        this.restartBtn.disabled = false;
    }

    togglePause() {
        this.isPaused = !this.isPaused;
        this.pauseBtn.textContent = this.isPaused ? '继续' : '暂停';
    }

    gameOver() {
        this.isGameOver = true;
        clearInterval(this.gameLoop);
        this.gameLoop = null;
        this.startBtn.disabled = true;
        this.pauseBtn.disabled = true;
        this.restartBtn.disabled = false;
    }

    restartGame() {
        clearInterval(this.gameLoop);
        this.snake = [{x: 15, y: 15}];
        this.direction = {x: 0, y: 0};
        this.food = this.generateFood();
        this.score = 0;
        this.scoreElement.textContent = '0';
        this.gameLoop = null;
        this.isPaused = false;
        this.isGameOver = false;
        this.pauseBtn.textContent = '暂停';
        this.startBtn.disabled = false;
        this.pauseBtn.disabled = true;
        this.restartBtn.disabled = true;
        this.draw();
    }

    toggleGestureControl() {
        if (this.gestureBtn.classList.contains('active')) {
            this.gestureController.stop();
            this.gestureBtn.classList.remove('active');
            this.gestureBtn.textContent = '启用手势控制';
        } else {
            this.gestureController.start();
            this.gestureBtn.classList.add('active');
            this.gestureBtn.textContent = '关闭手势控制';
        }
    }

    changeDirection(newDirection) {
        // 防止直接反向移动
        if ((newDirection.x * -1 !== this.direction.x) || (newDirection.y * -1 !== this.direction.y)) {
            this.direction = newDirection;
        }
    }
}

// 初始化游戏
window.onload = () => {
    new SnakeGame();
}; 