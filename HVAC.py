import sys
import json
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QHBoxLayout, QPushButton, QSlider
)
from PyQt5.QtCore import QTimer, Qt
import paho.mqtt.client as mqtt

# --- MQTT Setup ---
BROKER = "appz.coreiot.io"
PORT = 1883
TOPIC = "v1/devices/me/telemetry"
ACCESS_TOKEN = "z"  # 👉 Nhớ thay bằng token thật

client = mqtt.Client()
# client.username_pw_set(ACCESS_TOKEN)
# client.connect(BROKER, PORT, 60)
client.loop_start()

# --- PyQt HVAC Simulator ---
class HVACSimulator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌬️ HVAC System Simulator")
        self.setGeometry(100, 100, 400, 300)

        self.enabled = True
        self.air_flow = 50
        self.target_temp = 24

        self.layout = QVBoxLayout()

        # Enable/Disable button
        self.toggle_button = QPushButton("Disable HVAC", self)
        self.toggle_button.clicked.connect(self.toggle_hvac)
        self.layout.addWidget(self.toggle_button)

        # Target Temp Slider
        self.temp_label = QLabel(f"Target Temp: {self.target_temp} °C")
        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setMinimum(18)
        self.temp_slider.setMaximum(30)
        self.temp_slider.setValue(self.target_temp)
        self.temp_slider.valueChanged.connect(self.update_target_temp)
        self.layout.addWidget(self.temp_label)
        self.layout.addWidget(self.temp_slider)

        # Air Flow Slider
        self.flow_label = QLabel(f"Air Flow: {self.air_flow}%")
        self.flow_slider = QSlider(Qt.Horizontal)
        self.flow_slider.setMinimum(0)
        self.flow_slider.setMaximum(100)
        self.flow_slider.setValue(self.air_flow)
        self.flow_slider.valueChanged.connect(self.update_air_flow)
        self.layout.addWidget(self.flow_label)
        self.layout.addWidget(self.flow_slider)

        # Status Label
        self.status_label = QLabel("Waiting to send...")
        self.layout.addWidget(self.status_label)

        self.setLayout(self.layout)

        # Timer to auto-send every 5s
        self.timer = QTimer()
        self.timer.timeout.connect(self.send_data)
        self.timer.start(5000)

    def toggle_hvac(self):
        self.enabled = not self.enabled
        state_text = "Enable HVAC" if not self.enabled else "Disable HVAC"
        self.toggle_button.setText(state_text)

    def update_target_temp(self, value):
        self.target_temp = value
        self.temp_label.setText(f"Target Temp: {value} °C")

    def update_air_flow(self, value):
        self.air_flow = value
        self.flow_label.setText(f"Air Flow: {value}%")

    def send_data(self):
        payload = json.dumps({
            "enabled": self.enabled,
            "airFlow": self.air_flow,
            "targetTemperature": self.target_temp
        })
        client.publish(TOPIC, payload, qos=1)
        self.status_label.setText(f"📤 Sent: {payload}")

# --- Run App ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HVACSimulator()
    window.show()
    sys.exit(app.exec_())
