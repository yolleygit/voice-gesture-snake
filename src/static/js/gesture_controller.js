class GestureController {
    constructor(game) {
        this.game = game;
        this.video = null;
        this.canvas = null;
        this.ctx = null;
        this.isEnabled = false;
        this.lastGesture = null;
        this.lastCommandTime = 0;
        this.commandCooldown = 100;  // 命令冷却时间（毫秒）
        
        this.setupVideoElement();
        this.setupGestureCanvas();
    }

    setupVideoElement() {
        // 创建视频元素
        this.video = document.createElement('video');
        this.video.setAttribute('playsinline', '');
        this.video.style.transform = 'scaleX(-1)';  // 镜像显示
        this.video.style.display = 'none';
        document.body.appendChild(this.video);
    }

    setupGestureCanvas() {
        // 创建手势显示画布
        this.canvas = document.createElement('canvas');
        this.canvas.width = 320;
        this.canvas.height = 240;
        this.canvas.style.position = 'fixed';
        this.canvas.style.right = '20px';
        this.canvas.style.bottom = '20px';
        this.canvas.style.border = '2px solid #333';
        this.canvas.style.borderRadius = '8px';
        this.canvas.style.display = 'none';
        this.ctx = this.canvas.getContext('2d');
        
        // 添加手势提示文本
        this.canvas.style.position = 'relative';
        const gestureHint = document.createElement('div');
        gestureHint.style.position = 'absolute';
        gestureHint.style.bottom = '260px';
        gestureHint.style.right = '20px';
        gestureHint.style.backgroundColor = 'rgba(0,0,0,0.7)';
        gestureHint.style.color = 'white';
        gestureHint.style.padding = '10px';
        gestureHint.style.borderRadius = '5px';
        gestureHint.style.fontSize = '14px';
        gestureHint.innerHTML = '手势提示：<br>• 食指指向控制方向<br>• 手掌完全张开切换暂停/继续';
        document.body.appendChild(gestureHint);
        this.gestureHint = gestureHint;
        
        document.body.appendChild(this.canvas);
    }

    async start() {
        if (this.isEnabled) return;
        
        try {
            // 获取摄像头权限
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: 320,
                    height: 240,
                    facingMode: 'user'
                }
            });
            
            this.video.srcObject = stream;
            await this.video.play();
            
            this.isEnabled = true;
            this.canvas.style.display = 'block';
            this.gestureHint.style.display = 'block';
            
            // 开始手势检测循环
            this.detectGestures();
            
        } catch (error) {
            console.error('无法访问摄像头:', error);
            alert('无法访问摄像头，请确保已授予摄像头权限。');
        }
    }

    stop() {
        if (!this.isEnabled) return;
        
        // 停止视频流
        const stream = this.video.srcObject;
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
        
        this.video.srcObject = null;
        this.canvas.style.display = 'none';
        this.gestureHint.style.display = 'none';
        this.isEnabled = false;
        this.lastGesture = null;
    }

    async detectGestures() {
        if (!this.isEnabled) return;

        // 在画布上绘制视频帧
        this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
        
        // 发送帧数据到服务器进行手势识别
        try {
            const imageData = this.canvas.toDataURL('image/jpeg', 0.5);
            const response = await fetch('/detect_gesture', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ image: imageData })
            });
            
            const result = await response.json();
            if (result.processed_image) {
                // 显示处理后的图像（包含手部关键点标记）
                const img = new Image();
                img.onload = () => {
                    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
                    this.ctx.drawImage(img, 0, 0, this.canvas.width, this.canvas.height);
                };
                img.src = result.processed_image;
            }
            
            this.handleGestureResult(result);
            
        } catch (error) {
            console.error('手势识别错误:', error);
        }
        
        // 继续下一帧检测
        requestAnimationFrame(() => this.detectGestures());
    }

    handleGestureResult(result) {
        if (!result.gesture) return;
        
        const currentTime = Date.now();
        if (currentTime - this.lastCommandTime < this.commandCooldown) {
            return; // 如果在冷却时间内，忽略新的命令
        }
        
        const gesture = result.gesture;
        if (gesture !== this.lastGesture) {
            this.lastGesture = gesture;
            
            switch (gesture) {
                case 'UP':
                    this.game.changeDirection({x: 0, y: -1});
                    break;
                case 'DOWN':
                    this.game.changeDirection({x: 0, y: 1});
                    break;
                case 'LEFT':
                    this.game.changeDirection({x: -1, y: 0});
                    break;
                case 'RIGHT':
                    this.game.changeDirection({x: 1, y: 0});
                    break;
                case 'TOGGLE_PAUSE':
                    this.game.togglePause();
                    break;
            }
            
            this.lastCommandTime = currentTime;
        }
    }
} 