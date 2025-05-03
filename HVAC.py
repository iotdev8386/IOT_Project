import sys
import json
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QHBoxLayout, QPushButton, QSlider, QCheckBox
)
from PyQt5.QtCore import QTimer, Qt
import paho.mqtt.client as mqtt
import config_device
config = config_device.config["HVAC"]

MQTT_CLIENT_ID = config["clientId"]
print("MQTT_CLINENT",MQTT_CLIENT_ID)
MQTT_BROKER    = "app.coreiot.io"
MQTT_USER      = config["userName"]
MQTT_PASSWORD  = config["password"]
MQTT_TOPIC     = "v1/devices/me/telemetry"
RPC_TOPIC      = "v1/devices/me/rpc/respones/+"
# --- MQTT Setup ---
PORT = 1883
ACCESS_TOKEN = "z"  # 👉 Replace with real token

# # client = mqtt.Client()
# client = mqtt.Client(client_id=MQTT_CLIENT_ID)
# client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
# client.connect(MQTT_BROKER, PORT, 60)
# client.loop_start()

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

        # Toggle Switch for Enable/Disable
        self.toggle_switch = QCheckBox("HVAC Enabled")
        self.toggle_switch.setChecked(True)
        self.toggle_switch.stateChanged.connect(self.toggle_hvac)
        self.toggle_switch.setStyleSheet("""
            QCheckBox::indicator {
                width: 40px;
                height: 40px;
                margin-right: 20px;
            }
            QCheckBox::indicator:unchecked {
                image: url(none); background-color: #ccc; border-radius: 40px;
            }
            QCheckBox::indicator:checked {
                image: url(none); background-color: #4CAF50; border-radius: 40px;
            }
        """)
        self.layout.addWidget(self.toggle_switch)

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
        self.init_mqtt()

    def init_mqtt(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1,client_id = MQTT_CLIENT_ID)
        self.client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        try:
            self.client.connect(MQTT_BROKER, 1883, 60)
            self.client.loop_start()
        except Exception as e:
            self.status_label.setText(f"❌ MQTT connect error: {e}")
    
    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.client.subscribe(RPC_TOPIC)
            print("✅ Connected to MQTT broker")
        else:
            self.status_label.setText(f"❌ Connect failed: {rc}")


    def toggle_hvac(self, state):
        self.enabled = bool(state)
        self.temp_slider.setEnabled(self.enabled)
        self.flow_slider.setEnabled(self.enabled)
        self.toggle_switch.setText("HVAC Enabled" if self.enabled else "HVAC Disabled")

    def update_target_temp(self, value):
        self.target_temp = value
        self.temp_label.setText(f"Target Temp: {value} °C")

    def update_air_flow(self, value):
        self.air_flow = value
        self.flow_label.setText(f"Air Flow: {value}%")

    def on_message(self, client, userdata, msg):
        print("RECEIVE")
        try:  
            payload = json.loads(msg.payload.decode())
            method = payload.get("method")
            params = payload.get("params")

            if method == "setHVAC":
                self.set_hvac(params.get("enabled", True))
            elif method == "setTemperature":
                self.set_temperature(params)
            elif method == "setAirFlow":
                self.set_air_flow(params)
            else:
                self.status_label.setText(f"⚠️ Unknown method: {method}")
        except Exception as e:
            self.status_label.setText(f"❌ RPC Error: {e}")

    def set_hvac(self, enabled):
        self.toggle_switch.setChecked(enabled)
        self.status_label.setText(f"🔄 RPC: HVAC {'enabled' if enabled else 'disabled'}")

    def set_temperature(self, temp):
        if isinstance(temp, int):
            self.temp_slider.setValue(temp)
            self.status_label.setText(f"🌡️ RPC: Set Temp to {temp}°C")

    def set_air_flow(self, flow):
        if isinstance(flow, int):
            self.flow_slider.setValue(flow)
            self.status_label.setText(f"💨 RPC: Set Air Flow to {flow}%")

    
    def send_data(self):
        payload = json.dumps({
            "enabled": self.enabled,
            "airFlow": self.air_flow,
            "targetTemperature": self.target_temp
        })
        self.client.publish(MQTT_TOPIC, payload, qos=1)
        self.status_label.setText(f"📤 Sent: {payload}")

# --- Run App ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HVACSimulator()
    window.show()
    sys.exit(app.exec_())
