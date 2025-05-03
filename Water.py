import json
import sys
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QGridLayout, QFrame, QHBoxLayout
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
import config_device
import paho.mqtt.client as mqtt

config = config_device.config["Water"]

MQTT_CLIENT_ID = config["clientId"]
MQTT_BROKER    = "app.coreiot.io"
MQTT_USER      = config["userName"]
MQTT_PASSWORD  = config["password"]
MQTT_TOPIC     = "v1/devices/me/telemetry"
RPC_TOPIC      = "v1/devices/me/rpc/respones/+"


def mock_water_data():
    return {
        "voltage": round(random.uniform(3.5, 4.5), 2),
        "water": round(random.uniform(0.5, 3.0), 2)
    }

class WaterMeterUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("💧 Water Meter Monitor")
        self.setGeometry(200, 200, 400, 250)
        self.setStyleSheet("background-color: #1c2530; color: #ffffff;")

        font_label = QFont("Arial", 13, QFont.Bold)
        font_value = QFont("Arial", 24)

        self.layout = QVBoxLayout()
        self.grid = QGridLayout()

        self.data_fields = {
            "voltage": {"label": "🔋 Voltage", "unit": "V"},
            "water": {"label": "💧 Water Flow", "unit": "gal"},
        }

        self.labels = {}

        for i, key in enumerate(self.data_fields):
            box = QFrame()
            box.setStyleSheet("""
                QFrame {
                    background-color: #2a3442;
                    border-radius: 12px;
                    padding: 15px;
                }
            """)
            vbox = QVBoxLayout()

            label = QLabel(self.data_fields[key]["label"])
            label.setFont(font_label)
            label.setStyleSheet("color: #aad;")

            value = QLabel("—")
            value.setFont(font_value)
            value.setStyleSheet("color: #00ccff;")

            vbox.addWidget(label)
            vbox.addWidget(value)
            box.setLayout(vbox)
            self.grid.addWidget(box, i // 2, i % 2)
            self.labels[key] = value

        self.layout.addLayout(self.grid)
        self.setLayout(self.layout)
        self.init_mqtt()

        # Realtime update
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(60000)
        self.update_data()

    def init_mqtt(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,client_id = MQTT_CLIENT_ID)
        self.client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

        try:
            self.client.connect(MQTT_BROKER, 1883, 60)
            self.client.loop_start()
        except Exception as e:
            self.status_label.setText(f"MQTT connect error: {e}")   

    def update_data(self):
        data = mock_water_data()
        payload = json.dumps(data)
        self.client.publish(MQTT_TOPIC, payload, qos=1)
        # print(data)
        for key in self.data_fields:
            val = f"{data[key]} {self.data_fields[key]['unit']}"
            self.labels[key].setText(val)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WaterMeterUI()
    window.show()
    sys.exit(app.exec_())
