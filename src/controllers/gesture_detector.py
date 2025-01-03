import cv2
import numpy as np
import mediapipe as mp
import base64
import time

class GestureDetector:
    def __init__(self):
        # 初始化MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.last_gesture = None
        
        # 手掌状态追踪
        self.palm_start_time = None
        self.palm_hold_duration = 0.5  # 需要手掌打开持续0.5秒才触发
        self.is_palm_triggered = False
        
    def process_image(self, image_data):
        """处理图像数据并识别手势"""
        try:
            # 解码Base64图像数据
            image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # 转换颜色空间
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 处理图像
            results = self.hands.process(frame_rgb)
            
            if results.multi_hand_landmarks:
                landmarks = results.multi_hand_landmarks[0]
                
                # 绘制手部关键点和连接线
                self.mp_draw.draw_landmarks(
                    frame,
                    landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )
                
                # 识别手势
                gesture = self._recognize_gesture(landmarks)
                
                # 将处理后的图像编码为Base64
                _, buffer = cv2.imencode('.jpg', frame)
                processed_image = base64.b64encode(buffer).decode('utf-8')
                
                return {
                    'gesture': gesture,
                    'processed_image': f'data:image/jpeg;base64,{processed_image}'
                }
            else:
                # 如果没有检测到手，重置状态
                self.palm_start_time = None
                self.is_palm_triggered = False
            
            return {'gesture': None, 'processed_image': None}
            
        except Exception as e:
            print(f"手势识别错误: {str(e)}")
            return {'gesture': None, 'processed_image': None}
    
    def _recognize_gesture(self, landmarks):
        """识别手势类型"""
        # 检查是否是手掌打开手势
        is_palm_open = self._is_palm_open(landmarks)
        current_time = time.time()
        
        if is_palm_open:
            if self.palm_start_time is None:
                # 开始手掌打开计时
                self.palm_start_time = current_time
            elif not self.is_palm_triggered and (current_time - self.palm_start_time) >= self.palm_hold_duration:
                # 手掌打开持续时间达到阈值且未触发过
                self.is_palm_triggered = True
                return 'TOGGLE_PAUSE'
        else:
            # 不是手掌打开，重置状态
            self.palm_start_time = None
            self.is_palm_triggered = False
            
            # 检查方向控制
            direction = self._check_direction(landmarks)
            if direction:
                return direction
            
        return None
    
    def _is_palm_open(self, landmarks):
        """检查是否是手掌打开手势（所有手指伸直）"""
        # 获取所有手指的关键点
        finger_tips = [
            self.mp_hands.HandLandmark.INDEX_FINGER_TIP,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
            self.mp_hands.HandLandmark.RING_FINGER_TIP,
            self.mp_hands.HandLandmark.PINKY_TIP
        ]
        finger_pips = [
            self.mp_hands.HandLandmark.INDEX_FINGER_PIP,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
            self.mp_hands.HandLandmark.RING_FINGER_PIP,
            self.mp_hands.HandLandmark.PINKY_PIP
        ]
        
        # 检查所有手指是否伸直
        for tip_id, pip_id in zip(finger_tips, finger_pips):
            tip = landmarks.landmark[tip_id]
            pip = landmarks.landmark[pip_id]
            
            # 如果指尖不是明显高于PIP关节，说明手指没有伸直
            if tip.y >= pip.y - 0.02:  # 添加一个小的容差值
                return False
        
        # 特别检查拇指是否伸直（与其他手指分开）
        thumb_tip = landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
        thumb_ip = landmarks.landmark[self.mp_hands.HandLandmark.THUMB_IP]
        thumb_mcp = landmarks.landmark[self.mp_hands.HandLandmark.THUMB_MCP]
        
        # 检查拇指是否张开（与其他手指成一定角度）
        thumb_angle = self._calculate_angle(thumb_mcp, thumb_ip, thumb_tip)
        if thumb_angle < 150:  # 拇指需要足够伸直
            return False
        
        return True
    
    def _calculate_angle(self, point1, point2, point3):
        """计算三个点形成的角度"""
        vector1 = np.array([point1.x - point2.x, point1.y - point2.y])
        vector2 = np.array([point3.x - point2.x, point3.y - point2.y])
        
        cos_angle = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))
        angle = np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))
        return angle
    
    def _check_direction(self, landmarks):
        """检查方向控制手势"""
        # 获取食指关键点
        index_tip = landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        index_pip = landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_PIP]
        wrist = landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
        
        # 检查食指是否伸直
        if index_tip.y < index_pip.y:
            # 计算方向
            dx = index_tip.x - wrist.x
            dy = index_tip.y - wrist.y
            threshold = 0.05
            
            if abs(dx) > abs(dy):  # 水平方向
                if abs(dx) > threshold:
                    return 'LEFT' if dx > 0 else 'RIGHT'
            else:  # 垂直方向
                if abs(dy) > threshold:
                    return 'DOWN' if dy > 0 else 'UP'
        
        return None
    
    def __del__(self):
        """清理资源"""
        self.hands.close() 