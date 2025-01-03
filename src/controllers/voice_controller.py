import speech_recognition as sr
import threading
import queue
import time
import pyttsx3
import logging

class VoiceController:
    """语音控制器类"""
    
    def __init__(self):
        """初始化语音控制器"""
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.command_queue = queue.Queue()
        self.is_listening = False
        self.thread = None
        self.tts_enabled = True
        
        # 初始化语音合成引擎
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 200)  # 设置语速
        except Exception as e:
            logging.warning(f"语音合成引擎初始化失败: {str(e)}")
            self.tts_enabled = False
            self.engine = None
        
        # 命令映射
        self.command_map = {
            '上': 'UP',
            '向上': 'UP',
            '下': 'DOWN',
            '向下': 'DOWN',
            '左': 'LEFT',
            '向左': 'LEFT',
            '右': 'RIGHT',
            '向右': 'RIGHT',
            '开始': 'START',
            '暂停': 'PAUSE',
            '继续': 'RESUME',
            '结束': 'END'
        }
        
        try:
            # 调整麦克风的环境噪声阈值
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
        except Exception as e:
            logging.error(f"麦克风初始化失败: {str(e)}")
    
    def start_listening(self):
        """开始监听语音命令"""
        if not self.is_listening:
            self.is_listening = True
            self.thread = threading.Thread(target=self._listen_loop)
            self.thread.daemon = True
            self.thread.start()
            self.speak("语音控制已启动")
            print("语音控制已启动")
    
    def stop_listening(self):
        """停止监听语音命令"""
        if self.is_listening:
            self.is_listening = False
            if self.thread:
                self.thread.join()
                self.thread = None
            self.speak("语音控制已停止")
            print("语音控制已停止")
    
    def _listen_loop(self):
        """持续监听语音命令的循环"""
        while self.is_listening:
            try:
                with self.microphone as source:
                    print("正在监听...")
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=2)
                
                try:
                    # 使用本地识别引擎
                    text = self.recognizer.recognize_sphinx(audio, language='zh-CN')
                    print(f"识别到的文本: {text}")
                    self._process_command(text)
                except sr.UnknownValueError:
                    pass  # 无法识别的语音
                except sr.RequestError as e:
                    print(f"语音识别服务出现问题: {str(e)}")
                    self.speak("语音识别服务出现问题")
            except Exception as e:
                print(f"语音识别错误: {str(e)}")
                time.sleep(1)
    
    def _process_command(self, text):
        """处理识别到的语音命令"""
        text = text.strip()
        for key, value in self.command_map.items():
            if key in text:
                self.command_queue.put(value)
                self.speak(f"收到命令：{key}")
                print(f"收到命令：{key}")
                return
    
    def get_command(self):
        """获取最新的语音命令"""
        try:
            return self.command_queue.get_nowait()
        except queue.Empty:
            return None
    
    def speak(self, text):
        """语音播报"""
        if self.tts_enabled and self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"语音播报失败: {str(e)}")
                print(text)  # 如果语音播报失败，至少打印文本
        else:
            print(text)  # 如果语音合成不可用，打印文本
    
    def __del__(self):
        """清理资源"""
        try:
            self.stop_listening()
            if self.tts_enabled and hasattr(self, 'engine') and self.engine:
                self.engine.stop()
        except Exception as e:
            print(f"清理资源时出错: {str(e)}") 