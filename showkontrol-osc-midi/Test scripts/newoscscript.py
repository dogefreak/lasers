import curses
from pythonosc import dispatcher, osc_server
import threading
import time

# Create a dictionary to store deck parameters
deck_parameters = {
    1: {"bpm": 0.0, "active": 0},
    2: {"bpm": 0.0, "active": 0},
    3: {"bpm": 0.0, "active": 0},
    4: {"bpm": 0.0, "active": 0},
}

# Store the latest 3 OSC messages for debugging
latest_osc_messages = []

# Create the OSC message dispatcher
osc_dispatcher = dispatcher.Dispatcher()

def osc_handler(address, *args):
    latest_osc_messages.append((address, args))
    if len(latest_osc_messages) > 3:
        latest_osc_messages.pop(0)  # Remove the oldest message
    if address.startswith('/pangolin/deck'):
        # Split the address and extract the numerical part
        deck_number = int(''.join(filter(str.isdigit, address)))

        if deck_number in deck_parameters:
            if address.endswith('/bpm'):
                deck_parameters[deck_number]["bpm"] = args[0]

    if address.startswith('/pangolin/mixer/activedeck'):
        deck_number = args[0]
        for deck_num in deck_parameters:
            deck_parameters[deck_num]["active"] = 1 if deck_num == deck_number else 0

# Add the OSC message handler to the dispatcher
osc_dispatcher.set_default_handler(osc_handler)

# Function to update and display the dashboard
def update_dashboard(stdscr):
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "CDJ Deck Dashboard", curses.A_BOLD)

        for deck in range(1, 5):
            bpm = deck_parameters[deck]["bpm"]
            active = "Active" if deck_parameters[deck]["active"] == 1 else "Non-Active"
            stdscr.addstr(deck, 0, f"Deck {deck}: BPM = {bpm:.1f}, {active}")

        stdscr.addstr(9, 0, "Latest OSC Messages:")

        # Display the latest 3 messages in reverse order (latest at the top)
        message_count = len(latest_osc_messages)
        if message_count > 0:
            for i, message in enumerate(reversed(latest_osc_messages)):
                stdscr.addstr(10 + i, 0, f"{message[0]}: {message[1]}")

        stdscr.refresh()

def run_osc_server():
    server = osc_server.ThreadingOSCUDPServer(('192.168.1.255', 7000), osc_dispatcher)
    server.serve_forever()

if __name__ == '__main__':
    # Create threads for the dashboard and OSC server
    dashboard_thread = threading.Thread(target=curses.wrapper, args=(update_dashboard,))
    dashboard_thread.daemon = True
    dashboard_thread.start()

    osc_server_thread = threading.Thread(target=run_osc_server)
    osc_server_thread.daemon = True
    osc_server_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

