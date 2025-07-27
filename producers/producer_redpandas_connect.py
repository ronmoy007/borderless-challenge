import json
import websocket
import requests
from pre_process_message import PreProcessMessage

# Redpanda configuration
REDPANDA_CONNECT_URL = "http://redpanda_connect:8080/"

obj_pre_process = PreProcessMessage()

def on_open(ws):
    print("Connection opened")

def on_message_redpanda_connect(ws, message):
    
    print(f"on_message_redpanda_connect - message: {message}")
    json_redpanda = obj_pre_process.pre_process_message(ws, message)

    # make post request to Redpanda connect
    headers = {'Content-Type': 'application/vnd.kafka.json.v2+json'} 
    response = requests.post(REDPANDA_CONNECT_URL, headers=headers, json=json_redpanda)

    if response.status_code == 200:
        print(f"Message sent to Redpanda Connect: {json_redpanda}")
    else:
        print(f"Failed to send message to Redpanda Connect: {response.status_code} - {response.text}")

def on_close_producer_redpanda_connect(ws, close_status_code, close_msg):
    print("Connection closed with code:", close_status_code, "and message:", close_msg)

def producer_redpanda_connect(symbol):
    
    try:
        socket_url = f"wss://stream.binance.com:9443/ws/{symbol}@trade"
        ws = websocket.WebSocketApp(
            socket_url,
            on_open=on_open,
            on_message=on_message_redpanda_connect,
            on_close=on_close_producer_redpanda_connect
        )
        ws.run_forever()
    except Exception as e:
        print(f"An error occurred while running WebSocket for {symbol}: {e}")
