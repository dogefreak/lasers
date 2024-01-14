from pythonosc import dispatcher, osc_server
import threading
import os

# Create a dictionary to store deck parameters
deck_parameters = {
    1: {"bpm": 128.0, "active": 0},
    2: {"bpm": 128.0, "active": 0},
    3: {"bpm": 128.0, "active": 0},
    4: {"bpm": 128.0, "active": 0},
}

# OSC message handler
def osc_handler(address, *args):
    if address.startswith('/pangolin/deck'):
        deck_number = int(address.split('/')[3])
        if address.endswith('/bpm'):
            deck_parameters[deck_number]["bpm"] = args[0]
        elif address.endswith('/activedeck'):
            deck_parameters[deck_number]["active"] = args[0]

# Create an OSC server to receive messages
dispatcher = dispatcher.Dispatcher()
dispatcher.set_default_handler(osc_handler)
server = osc_server.ThreadingOSCUDPServer(('127.0.0.1', 9000), dispatcher)

# Function to update and display the dashboard
def update_dashboard():
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        print("CDJ Deck Dashboard")
        for deck in range(1, 5):
            bpm = deck_parameters[deck]["bpm"]
            active = "Active" if deck_parameters[deck]["active"] == 1 else "Non-Active"
            print(f"Deck {deck}: BPM = {bpm:.1f}, {active}")
        print("Press Ctrl+C to quit")

if __name__ == '__main__':
    dashboard_thread = threading.Thread(target=update_dashboard)
    dashboard_thread.daemon = True
    dashboard_thread.start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

