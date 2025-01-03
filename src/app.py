from flask import Flask, render_template, request, jsonify
import os
from controllers.gesture_detector import GestureDetector

app = Flask(__name__)
gesture_detector = GestureDetector()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detect_gesture', methods=['POST'])
def detect_gesture():
    try:
        data = request.json
        image_data = data.get('image')
        if not image_data:
            return jsonify({'error': '没有收到图像数据'}), 400
            
        result = gesture_detector.process_image(image_data)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080) 