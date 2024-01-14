import curses
from pythonosc import dispatcher, osc_server
import threading
import socket
import time

# Function to get the local broadcast address
def get_local_broadcast_address():
    local_ip = socket.gethostbyname(socket.gethostname())
    local_ip_parts = local_ip.split('.')
    local_ip_parts[-1] = '255'  # Change the last octet to 255 for broadcast
    return '.'.join(local_ip_parts)

# Function to obtain a custom IP address or use the local broadcast address
def get_ip_address():
    default_broadcast_ip = get_local_broadcast_address()
    user_ip = input(f"Enter the IP address (press Enter for default {default_broadcast_ip}): ").strip()
    return user_ip if user_ip else default_broadcast_ip

# Function to obtain a custom port or use the default port
def get_port():
    default_port = 7000
    user_port = input(f"Enter the port (press Enter for default {default_port}): ").strip()
    return int(user_port) if user_port else default_port

# Create a dictionary to store deck parameters
deck_parameters = {
    1: {"bpm": 0.00, "active": 0},
    2: {"bpm": 0.00, "active": 0},
    3: {"bpm": 0.00, "active": 0},
    4: {"bpm": 0.00, "active": 0},
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
def update_dashboard(stdscr, osc_server_ip, osc_server_port):
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "CDJ Deck Dashboard", curses.A_BOLD)

        for deck in range(1, 5):
            bpm = deck_parameters[deck]["bpm"]
            active = "Active" if deck_parameters[deck]["active"] == 1 else "Non-Active"
            stdscr.addstr(deck, 0, f"Deck {deck}: BPM = {bpm:.1f}, {active}")

        stdscr.addstr(6, 0, f"Listening on {osc_server_ip}:{osc_server_port}")
        
        stdscr.addstr(8, 0, "Latest OSC Messages:")
        # Display the latest 3 messages in reverse order (latest at the top)
        message_count = len(latest_osc_messages)
        if message_count > 0:
            for i, message in enumerate(reversed(latest_osc_messages)):
                stdscr.addstr(9 + i, 0, f"{message[0]}: {message[1]}")

        stdscr.refresh()

def run_osc_server(ip, port):
    server = osc_server.ThreadingOSCUDPServer((ip, port), osc_dispatcher)
    server.serve_forever()

if __name__ == '__main__':
    osc_server_ip = get_ip_address()
    osc_server_port = get_port()

    # Create threads for the dashboard and OSC server
    dashboard_thread = threading.Thread(target=curses.wrapper, args=(update_dashboard, osc_server_ip, osc_server_port))
    dashboard_thread.daemon = True
    dashboard_thread.start()

    osc_server_thread = threading.Thread(target=run_osc_server, args=(osc_server_ip, osc_server_port))
    osc_server_thread.daemon = True
    osc_server_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

