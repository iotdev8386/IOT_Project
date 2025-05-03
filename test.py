import json
import time
import paho.mqtt.client as mqtt
import config_device
config = config_device.config["TestDV2"]

MQTT_CLIENT_ID = config["clientId"]
MQTT_BROKER    = "app.coreiot.io"
MQTT_USER      = config["userName"]
MQTT_PASSWORD  = config["password"]
MQTT_TOPIC     = "v1/devices/me/telemetry"
RPC_TOPIC      = "v1/devices/me/rpc/request/"
RPC_RES_TOPIC      = "v1/devices/me/rpc/response/+"
# --- MQTT Setup ---
PORT = 1883

# Generate unique client ID

def on_connect(client, userdata, flags, rc, property):
    print(f"Connected with result code {rc}")

    # Subscribe to RPC request topic (server -> device)
    client.subscribe("v1/devices/me/rpc/request/+")
    print("Subscribed to RPC requests")

def on_message(client, userdata, msg):
    print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")

def make_rpc_call(client, method, params):
    return None

def main():
    # Initialize MQTT client
    client = mqtt.Client(client_id=MQTT_CLIENT_ID, protocol=mqtt.MQTTv5)
    client.on_connect = on_connect
    client.on_message = on_message
    
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    
    client.connect(MQTT_BROKER, PORT, 400)

    client.loop_start()
    try:
        time.sleep(200)  # Wait for response
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()