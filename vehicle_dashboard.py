from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
import time
import cv2
from deepface import DeepFace
from mtcnn import MTCNN
import pandas as pd
from twilio.rest import Client  #  Import Twilio

app = Flask(__name__)
socketio = SocketIO(app)

#  Twilio credentials (Replace with actual values)
TWILIO_SID = "AB12345... "
TWILIO_AUTH_TOKEN = "26ab345ed..."
TWILIO_PHONE_NUMBER = "+1..."  # Twilio number
TARGET_PHONE_NUMBER = "+91..."  # Your phone number

# Initialize emotion detector
detector = MTCNN()
heart_rate_file = "Heart rate_Dec252024-Jan72025.html"

def send_sms_alert(message):
    """ Sends an SMS alert via Twilio"""
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=TARGET_PHONE_NUMBER
        )
        print(" SMS Alert Sent!")
    except Exception as e:
        print(f" Failed to send SMS: {e}")

def analyze_heart_rate():
    """Reads the latest heart rate from the file."""
    try:
        tables = pd.read_html(heart_rate_file)
        heart_rate_table = tables[0]
        heart_rate_table.columns = ['Date', 'Time', 'Heart rate (bpm)', 'Tag', 'Notes']
        today_data = heart_rate_table[heart_rate_table['Date'] == 'Today'].copy()
        today_data.loc[:, 'Heart rate (bpm)'] = pd.to_numeric(today_data['Heart rate (bpm)'], errors='coerce')
        today_data.dropna(subset=['Heart rate (bpm)'], inplace=True)

        if not today_data.empty:
            latest_heart_rate = today_data.iloc[-1]['Heart rate (bpm)']
            return latest_heart_rate
    except Exception as e:
        print(f"Heart rate analysis error: {e}")
    return None

def analyze_emotion():
    """Captures a frame from the webcam and detects emotion."""
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print(" Warning: Could not capture webcam frame")
        return "Unknown"

    try:
        detections = detector.detect_faces(frame)
        if detections:
            face_region = frame[
                detections[0]['box'][1]:detections[0]['box'][1] + detections[0]['box'][3],
                detections[0]['box'][0]:detections[0]['box'][0] + detections[0]['box'][2]
            ]
            result = DeepFace.analyze(face_region, actions=['emotion'], enforce_detection=False)
            return result[0]['dominant_emotion']
    except Exception as e:
        print(f" Emotion analysis error: {e}")

    return "Neutral"


def monitor_health():
    """Monitors heart rate and emotion for 3 consecutive frames before triggering an alert."""
    alert_buffer = []  #  Stores the last 3 readings

    while True:
        time.sleep(5)  #  Check every 5 sec
        heart_rate = analyze_heart_rate()
        emotion = analyze_emotion()

        if heart_rate and emotion:
            #  Check if the current frame shows distress
            if (heart_rate > 110 or heart_rate < 70) and emotion in ["sad", "fear", "angry"]:
                alert_buffer.append((emotion, heart_rate))  #  Store reading

                if len(alert_buffer) >= 3:  #  If 3 consecutive distress frames
                    alert_msg = f" EMERGENCY! Emotion: {emotion}, Heart Rate: {heart_rate} BPM"
                    print(alert_msg)
                    socketio.emit("update_alert", alert_msg)  #  Send to webpage
                    send_sms_alert(alert_msg)  #  Send SMS alert
                    alert_buffer.clear()  #  Reset buffer after sending alert
            else:
                alert_buffer.clear()  #  Reset buffer if a normal reading appears


#  Start monitoring in the background
threading.Thread(target=monitor_health, daemon=True).start()

@app.route("/")
def index():
    return render_template("dashboard.html")

if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0")
