import sys
import random
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QGridLayout, QFrame
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import config_device
import paho.mqtt.client as mqtt

config = config_device.config["Energy"]

MQTT_CLIENT_ID = config["clientId"]
MQTT_BROKER    = "app.coreiot.io"
MQTT_USER      = config["userName"]
MQTT_PASSWORD  = config["password"]
MQTT_TOPIC     = "v1/devices/me/telemetry"
RPC_TOPIC      = "v1/devices/me/rpc/respones/+"

def mock_data():
    return {
        "amperage": round(random.uniform(14, 17), 1),
        "energy": round(random.uniform(0.05, 0.1), 2),
        "frequency": round(random.uniform(49, 55), 1),
        "power": round(random.uniform(1000, 3000), 1),
        "voltage": round(random.uniform(210, 230), 1),
    }

class PowerMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Energy Meter Monitoring")
        self.setGeometry(200, 200, 500, 300)
        self.setStyleSheet("background-color: #1e1e2f; color: #fff;")

        self.font_label = QFont("Arial", 14, QFont.Bold)
        self.font_value = QFont("Arial", 22)

        self.layout = QVBoxLayout()
        self.grid = QGridLayout()

        self.fields = ["amperage", "energy", "frequency", "power", "voltage"]
        self.units = {
            "amperage": "A",
            "energy": "kWh",
            "frequency": "Hz",
            "power": "W",
            "voltage": "V"
        }
        self.labels = {}

        row = 0
        for field in self.fields:
            label = QLabel(field.capitalize())
            label.setFont(self.font_label)
            label.setStyleSheet("color: #aaa;")
            value = QLabel("—")
            value.setFont(self.font_value)
            value.setStyleSheet("color: #00ffcc;")
            self.labels[field] = value

            box = QFrame()
            box.setStyleSheet("""
                QFrame {
                    background-color: #2a2a40;
                    border-radius: 12px;
                    padding: 10px;
                }
            """)
            box_layout = QVBoxLayout()
            box_layout.addWidget(label)
            box_layout.addWidget(value)
            box.setLayout(box_layout)
            self.grid.addWidget(box, row // 2, row % 2)
            row += 1

        self.layout.addLayout(self.grid)
        self.setLayout(self.layout)

        # Update data every 5 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(60000)
        self.init_mqtt()
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
        data = mock_data()
        payload = json.dumps(data)

        self.client.publish(MQTT_TOPIC, payload=payload)

        for key in self.fields:
            value = data[key]
            self.labels[key].setText(f"{value} {self.units[key]}")
            

if __name__ == '__main__':
    app = QApplication(sys.argv)
    monitor = PowerMonitor()
    monitor.show()
    sys.exit(app.exec_())
