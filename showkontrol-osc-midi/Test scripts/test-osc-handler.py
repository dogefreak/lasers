from pythonosc import dispatcher, osc_server
import threading

# Create a dictionary to store deck parameters
deck_parameters = {
    1: {"bpm": 128.0, "active": 0},
    2: {"bpm": 128.0, "active": 0},
    3: {"bpm": 128.0, "active": 0},
    4: {"bpm": 128.0, "active": 0},
}

# Store received OSC messages for debugging
received_osc_messages = []

# Create the OSC message dispatcher
osc_dispatcher = dispatcher.Dispatcher()

def osc_handler(address, *args):
    received_osc_messages.append((address, args))
    if address.startswith('/pangolin/deck'):
        # Split the address and extract the numerical part
        deck_number = int(''.join(filter(str.isdigit, address)))

        if deck_number in deck_parameters:
            if address.endswith('/bpm'):
                deck_parameters[deck_number]["bpm"] = args[0]
                print(f"Updated BPM for Deck {deck_number}: {args[0]}")

    if address.startswith('/pangolin/mixer/activedeck'):
        deck_number = args[0]
        for deck_num in deck_parameters:
            deck_parameters[deck_num]["active"] = 1 if deck_num == deck_number else 0
        print(f"Updated Active Deck for Deck {deck_number}: {deck_parameters[deck_number]['active']}")

# Add the OSC message handler to the dispatcher
osc_dispatcher.set_default_handler(osc_handler)

def run_osc_server():
    server = osc_server.ThreadingOSCUDPServer(('127.0.0.1', 9000), osc_dispatcher)
    server.serve_forever()

if __name__ == '__main__':
    osc_server_thread = threading.Thread(target=run_osc_server)
    osc_server_thread.daemon = True
    osc_server_thread.start()

    try:
        while True:
            # Print received OSC messages for debugging
            if received_osc_messages:
                for message in received_osc_messages:
                    print(f"Received OSC Message: {message[0]}: {message[1]}")
                    print(deck_parameters)
                received_osc_messages = []  # Clear the list
            pass
    except KeyboardInterrupt:
        pass

