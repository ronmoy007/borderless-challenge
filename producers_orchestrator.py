import threading # This library is used to run multiple WebSocket connections concurrently, because in my first approach It was blocking the main thread.
from producer import run_websocket

def main():

    # IN order to make it more dynamic, we read the symbols from a file
    try:
        with open('symbols.txt', 'r') as file:
            list_symbols = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print("symbols.txt not found.")
    
    threads = []
    for symbol in list_symbols:
        t = threading.Thread(target=run_websocket, args=(symbol,))
        t.start()
        threads.append(t)

if __name__ == "__main__":
    main()