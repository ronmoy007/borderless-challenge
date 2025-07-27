import json
import websocket
import requests
from confluent_kafka import Producer

# Defining classes for custom exceptions
class MissingFieldException(Exception):
    def __init__(self, field):
        super().__init__(f"Missing field: {field}")

class MissingValueException(Exception):
    def __init__(self, field):
        super().__init__(f"Field '{field}' is None")

class DuplicateTradeIDException(Exception):
    def __init__(self, trade_id):
        super().__init__(f"Trade ID {trade_id} already received")

class InvalidJSONException(Exception):
    def __init__(self, message):
        super().__init__(f"Invalid JSON message: {message}")

# Redpanda configuration
REDPANDA_TOPIC = "borderless_challenge"
REDPANDA_BROKER = "redpanda:9092"
REDPANDA_CONNECT_URL = "http://redpanda_connect:8080/"

msg_producer = Producer({'bootstrap.servers': REDPANDA_BROKER})

list_trade_id_received = set()

def redpanda_response(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
    # Mmmm not sure what to do with the response, maybe log errors to a file or something?
    # Anyway, for now just print the response to show that communication with Redpanda is working

def pre_process_message(ws, message):
    print(f"Received: {message}")
    try:
        trade_data = json.loads(message)

        # Example trade data structure (just for reference and get familiar with the expected format):
        # {
        #     "e": "trade",       // Event type
        #     "E": 1672515782136, // Event time
        #     "s": "BNBBTC",      // Symbol
        #     "t": 12345,         // Trade ID
        #     "p": "0.001",       // Price
        #     "q": "100",         // Quantity
        #     "T": 1672515782136, // Trade time
        #     "m": true,          // Is the buyer the market maker?
        #     "M": true           // Ignore
        # }

        # First validation: check if the message contains the expected fields
        list_valid_fields = ["e", "E", "s", "t", "p", "q", "T", "m", "M"]
        for field in list_valid_fields:
            if field not in trade_data:
                print(f"Trade data missing field: {field}")
                # Raise an exception or handle it as needed
                raise MissingFieldException(field)
            
            # Second validation: Check if the field is not None
            if trade_data[field] is None:
                print(f"Trade data field '{field}' is None:", trade_data)
                # Raise an exception or handle it as needed
                raise MissingValueException(field)
        
        # Third validation: Check if the trade ID has already been received        
        trade_id = trade_data["t"]
        if trade_id in list_trade_id_received:
            print(f"Trade ID {trade_id} already received, skipping.")
            raise DuplicateTradeIDException(trade_id)  # Raise an exception or handle it as needed            

        # If all validations pass, process the trade data
        json_redpanda = {
            "event_type": trade_data["e"],
            "event_time": trade_data["E"],
            "symbol": trade_data["s"],
            "trade_id": trade_id,
            "price": trade_data["p"],
            "quantity": trade_data["q"],
            "trade_time": trade_data["T"],
            "is_market_maker": trade_data["m"],
            "ignore": trade_data["M"] # Not sure what this field is for, but included for completeness
        }

        # Add the trade ID to the set of received IDs
        list_trade_id_received.add(json_redpanda["trade_id"])
        
        return json_redpanda
            
    except json.JSONDecodeError:
        print("Error decoding JSON message:", message)
        raise InvalidJSONException(message)

def producer_python(ws, message):
    
    json_redpanda = pre_process_message(ws, message)
    msg_producer.produce(
        topic=REDPANDA_TOPIC,
        key=str(json_redpanda["trade_id"]),
        value=json.dumps(json_redpanda),
        callback=redpanda_response
    )    
    
    msg_producer.poll(0)

def producer_redpanda_connect(ws, message):
    json_redpanda = pre_process_message(ws, message)

    # make post request to Redpanda connect
    headers = {'Content-Type': 'application/vnd.kafka.json.v2+json'} 
    response = requests.post(REDPANDA_CONNECT_URL, headers=headers, json=json_redpanda)

    if response.status_code == 200:
        print(f"Message sent to Redpanda Connect: {json_redpanda}")
    else:
        print(f"Failed to send message to Redpanda Connect: {response.status_code} - {response.text}")

def on_open(ws):
    print("Connection opened")

def on_close_producer_python(ws, close_status_code, close_msg):
    print("Connection closed with code:", close_status_code, "and message:", close_msg)
    msg_producer.flush()

def on_close_producer_redpanda_connect(ws, close_status_code, close_msg):
    print("Connection closed with code:", close_status_code, "and message:", close_msg)

def run_websocket(symbol, redpanda_connect=False):
    print(f"Starting WebSocket for symbol: {symbol}, redpanda_connect={redpanda_connect}")

    if redpanda_connect:
        on_message_function = producer_redpanda_connect
        on_close_function = on_close_producer_redpanda_connect
    else:
        on_message_function = producer_python
        on_close_function = on_close_producer_python

    try:
        socket_url = f"wss://stream.binance.com:9443/ws/{symbol}@trade"
        ws = websocket.WebSocketApp(
            socket_url,
            on_open=on_open,
            on_message=on_message_function,
            on_close=on_close_function
        )
        ws.run_forever()
    except Exception as e:
        print(f"An error occurred while running WebSocket for {symbol}: {e}")
    finally:        
        # If an error occurs, flush the Redpanda producer to ensure all messages are sent
        if not redpanda_connect:
            msg_producer.flush()