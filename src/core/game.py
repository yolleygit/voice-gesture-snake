import pygame
import random
import numpy as np
from controllers.voice_controller import VoiceController

class SnakeGame:
    """贪吃蛇游戏核心类"""
    
    def __init__(self, width=800, height=600, grid_size=20):
        """
        初始化游戏
        
        Args:
            width (int): 游戏窗口宽度
            height (int): 游戏窗口高度
            grid_size (int): 网格大小
        """
        self.width = width
        self.height = height
        self.grid_size = grid_size
        
        # 初始化语音控制器
        self.voice_controller = VoiceController()
        self.voice_enabled = False
        
        self.reset()
        
        # 初始化Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('语音手势贪吃蛇')
        self.clock = pygame.time.Clock()
        
        # 颜色定义
        self.colors = {
            'background': (0, 0, 0),
            'snake': (0, 255, 0),
            'food': (255, 0, 0),
            'text': (255, 255, 255)
        }
    
    def reset(self):
        """重置游戏状态"""
        self.snake = [(self.width // 2, self.height // 2)]
        self.direction = (self.grid_size, 0)  # 初始向右移动
        self.food = self._generate_food()
        self.score = 0
        self.game_over = False
        self.paused = False
    
    def _generate_food(self):
        """生成食物的位置"""
        while True:
            x = random.randrange(0, self.width, self.grid_size)
            y = random.randrange(0, self.height, self.grid_size)
            if (x, y) not in self.snake:
                return (x, y)
    
    def update(self):
        """更新游戏状态"""
        if self.game_over or self.paused:
            return
            
        # 移动蛇
        new_head = (
            (self.snake[0][0] + self.direction[0]) % self.width,
            (self.snake[0][1] + self.direction[1]) % self.height
        )
        
        # 检查碰撞
        if new_head in self.snake:
            self.game_over = True
            if self.voice_enabled:
                self.voice_controller.speak("游戏结束")
            return
            
        self.snake.insert(0, new_head)
        
        # 检查是否吃到食物
        if new_head == self.food:
            self.score += 1
            if self.voice_enabled:
                self.voice_controller.speak(f"得分：{self.score}")
            self.food = self._generate_food()
        else:
            self.snake.pop()
    
    def change_direction(self, new_direction):
        """
        改变蛇的移动方向
        
        Args:
            new_direction (tuple): 新的方向，如(grid_size, 0)表示向右
        """
        # 防止直接反向移动
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction
    
    def draw(self):
        """绘制游戏画面"""
        self.screen.fill(self.colors['background'])
        
        # 绘制蛇
        for segment in self.snake:
            pygame.draw.rect(self.screen, self.colors['snake'],
                           (segment[0], segment[1], self.grid_size-2, self.grid_size-2))
        
        # 绘制食物
        pygame.draw.rect(self.screen, self.colors['food'],
                        (self.food[0], self.food[1], self.grid_size-2, self.grid_size-2))
        
        # 绘制分数
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'分数: {self.score}', True, self.colors['text'])
        self.screen.blit(score_text, (10, 10))
        
        # 绘制语音控制状态
        voice_status = "语音控制: 开启" if self.voice_enabled else "语音控制: 关闭"
        voice_text = font.render(voice_status, True, self.colors['text'])
        self.screen.blit(voice_text, (10, 50))
        
        if self.game_over:
            game_over_text = font.render('游戏结束！按R重新开始', True, self.colors['text'])
            text_rect = game_over_text.get_rect(center=(self.width/2, self.height/2))
            self.screen.blit(game_over_text, text_rect)
        
        pygame.display.flip()
    
    def handle_voice_command(self):
        """处理语音命令"""
        if not self.voice_enabled:
            return
            
        command = self.voice_controller.get_command()
        if command:
            if command == 'UP':
                self.change_direction((0, -self.grid_size))
            elif command == 'DOWN':
                self.change_direction((0, self.grid_size))
            elif command == 'LEFT':
                self.change_direction((-self.grid_size, 0))
            elif command == 'RIGHT':
                self.change_direction((self.grid_size, 0))
            elif command == 'PAUSE':
                self.paused = True
            elif command == 'RESUME':
                self.paused = False
            elif command == 'START' and self.game_over:
                self.reset()
    
    def handle_input(self):
        """处理键盘输入"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.reset()
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_v:  # 切换语音控制
                    self.voice_enabled = not self.voice_enabled
                    if self.voice_enabled:
                        self.voice_controller.start_listening()
                    else:
                        self.voice_controller.stop_listening()
                elif not self.paused and not self.game_over:
                    if event.key == pygame.K_UP:
                        self.change_direction((0, -self.grid_size))
                    elif event.key == pygame.K_DOWN:
                        self.change_direction((0, self.grid_size))
                    elif event.key == pygame.K_LEFT:
                        self.change_direction((-self.grid_size, 0))
                    elif event.key == pygame.K_RIGHT:
                        self.change_direction((self.grid_size, 0))
        
        return True

    def run(self):
        """运行游戏主循环"""
        running = True
        while running:
            running = self.handle_input()
            self.handle_voice_command()
            self.update()
            self.draw()
            self.clock.tick(10)  # 控制游戏速度
        
        # 清理资源
        if self.voice_enabled:
            self.voice_controller.stop_listening()
        pygame.quit() 