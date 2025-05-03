import sys
import json

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QHBoxLayout, QSlider
)
from PyQt5.QtCore import QTimer, Qt

import paho.mqtt.client as mqtt

import config_device
from thirdparty.QSwitchControl import SwitchControl

config = config_device.config["TestDV2"]

MQTT_CLIENT_ID = config["clientId"]
MQTT_BROKER    = "app.coreiot.io"
MQTT_USER      = config["userName"]
MQTT_PASSWORD  = config["password"] 
MQTT_TOPIC     = "v1/devices/me/telemetry"
RPC_TOPIC      = "v1/devices/me/rpc/request/+"
PORT = 1883

class HVACSimulator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HVAC System Simulator")
        self.setGeometry(100, 100, 400, 300)

        self.enabled = True
        self.air_flow = 50
        self.target_temp = 24

        self.layout = QVBoxLayout()

        self.toggle_label = QLabel("HVAC Control")
        self.toggle_switch = SwitchControl(bg_color="#ff0000", 
                                           active_color="#00ff00",
                                           checked=self.enabled)
        
        self.toggle_switch.stateChanged.connect(self.toggle_hvac)
        # Create a horizontal layout for label and switch
        switch_layout = QHBoxLayout()
        switch_layout.addWidget(self.toggle_switch)
        switch_layout.setSpacing(30)
        
        switch_layout.addWidget(self.toggle_label)
        self.layout.addLayout(switch_layout)

        # Target Temp Slider
        self.temp_label = QLabel(f"Target Temp: {self.target_temp} °C")
        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setMinimum(16)
        self.temp_slider.setMaximum(40)
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

        self.setLayout(self.layout)

        # Timer to auto-send every 5s
        self.timer = QTimer()
        self.timer.timeout.connect(self.send_data)
        self.timer.start(5000)

        self.toggle_hvac(self.enabled)
        self.init_mqtt()

    def init_mqtt(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,client_id = MQTT_CLIENT_ID)
        self.client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        try:
            self.client.connect(MQTT_BROKER, 1883, 60)
            self.client.loop_start()
        except Exception as e:
            print(f"MQTT connect error: {e}")
    
    def on_connect(self, client, userdata, flags, rc, properties=None):
        print("ON CONNECT")
        if rc == 0:
            self.client.subscribe(RPC_TOPIC)
            print("Connected to MQTT broker")
        else:
            print(f"Connect failed: {rc}")


    def toggle_hvac(self, state):
        self.enabled = bool(state)
        self.temp_slider.setEnabled(self.enabled)
        self.flow_slider.setEnabled(self.enabled)
        self.toggle_label.setText("HVAC Enabled" if self.enabled else "HVAC Disabled")
        self.toggle_switch.setEnable(self.enabled)

    def update_target_temp(self, value):
        self.target_temp = value
        self.temp_label.setText(f"Target Temp: {value} °C")

    def update_air_flow(self, value):
        self.air_flow = value
        self.flow_label.setText(f"Air Flow: {value}%")

    def on_message(self, client, userdata, msg):
        try:  
            payload = json.loads(msg.payload.decode())
            method = payload.get("method")
            params = payload.get("params")

            print("RECEIVE",method, params)
            if method == "setEnabled":
                self.set_enabled(params)
            elif method == "setTemperature":
                self.set_temperature(params)
            elif method == "getTemperature":
                self.get_temperature(msg)
            else:
                print(f"⚠️ Unknown method: {method}")
        except Exception as e:
            print(f"❌ RPC Error: {e}")

    def set_enabled(self, enabled):
        print("RPC set enabled", enabled)
        self.toggle_hvac(enabled)

    def set_temperature(self, temp):
        temp = int(temp)
        self.temp_slider.setValue(temp)
        print(f"RPC: Set Temp to {temp}°C")

    def get_temperature(self,msg):
        request_id = msg.topic.split("/")[-1]
        # print("--",msg.topic.split("/"))
        self.client.publish(f"v1/devices/me/rpc/response/{request_id}", str(self.target_temp))

    def send_data(self):
        payload = json.dumps({
            "enabled": self.enabled,
            "airFlow": self.air_flow,
            "targetTemperature": self.target_temp
        })
        self.client.publish(MQTT_TOPIC, payload, qos=1)
        print(f"Sent: {payload}")

# --- Run App ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HVACSimulator()
    window.show()
    sys.exit(app.exec_())
