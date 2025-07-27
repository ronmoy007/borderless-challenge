import websocket
import json
from confluent_kafka import Producer
from pre_process_message import PreProcessMessage

REDPANDA_BROKER = "redpanda:9092"
REDPANDA_TOPIC = "borderless_challenge"

msg_producer = Producer({'bootstrap.servers': REDPANDA_BROKER})
obj_pre_process = PreProcessMessage()

def on_open(ws):
    print("Connection opened")

def redpanda_response(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
    # Mmmm not sure what to do with the response, maybe log errors to a file or something?
    # Anyway, for now just print the response to show that communication with Redpanda is working

def on_message_python(ws, message):
    
    print(f"on_message_python - message: {message}")
    json_redpanda = obj_pre_process.pre_process_message(ws, message)
    msg_producer.produce(
        topic=REDPANDA_TOPIC,
        key=str(json_redpanda["trade_id"]),
        value=json.dumps(json_redpanda),
        callback=redpanda_response
    )    
    msg_producer.poll(0)

def on_close_producer_python(ws, close_status_code, close_msg):
    print("Connection closed with code:", close_status_code, "and message:", close_msg)
    msg_producer.flush()

def producer_python(symbol):
        
    try:
        socket_url = f"wss://stream.binance.com:9443/ws/{symbol}@trade"
        ws = websocket.WebSocketApp(
            socket_url,
            on_open=on_open,
            on_message=on_message_python,
            on_close=on_close_producer_python
        )
        ws.run_forever()
    except Exception as e:
        print(f"An error occurred while running WebSocket for {symbol}: {e}")
    finally:        
        # If an error occurs, flush the Redpanda producer to ensure all messages are sent        
        msg_producer.flush()