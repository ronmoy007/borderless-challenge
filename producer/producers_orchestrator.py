import threading # This library is used to run multiple WebSocket connections concurrently, because in my first approach It was blocking the main thread.
from producer import run_websocket
from pathlib import Path
import sys

def main(redpanda_connect):

    # IN order to make it more dynamic, we read the symbols from a file
    script_dir = Path(__file__).parent
    symbols_file = script_dir / 'symbols.txt'
    try:
        # update reference to the file         
        with symbols_file.open('r') as file:
            list_symbols = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print("symbols.txt not found.")
    
    threads = []
    for symbol in list_symbols:
        t = threading.Thread(target=run_websocket, args=(symbol,redpanda_connect))
        t.start()
        threads.append(t)

if __name__ == "__main__":
    
    if len(sys.argv) > 1 and sys.argv[1] == '--redpanda-connect':
        redpanda_connect = True
    else:
        redpanda_connect = False
    
    main(redpanda_connect)