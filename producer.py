import websocket

def on_message(ws, message):
    print(f"Received: {message}")

def on_open(ws):
    print("Connection opened")

def on_close(ws, close_status_code, close_msg):
    print("Connection closed with code:", close_status_code, "and message:", close_msg)

def run_websocket(symbol):
    print(f"Starting WebSocket for symbol: {symbol}")
    
    socket_url = f"wss://stream.binance.com:9443/ws/{symbol}@trade"
    ws = websocket.WebSocketApp(
        socket_url,
        on_open=on_open,
        on_message=on_message,
        on_close=on_close
    )
    ws.run_forever()