import argparse
from pythonosc import osc_server, dispatcher

# Initialize variables for active deck and BPM for each deck
active_deck = 0
bpm_data = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}

# Callback function to handle active deck data
def handle_active_deck(address, *args):
    global active_deck
    active_deck = args[0]
    print(f"Active Deck: {active_deck}")

# Callback function to handle BPM data for each deck
def handle_bpm(address, *args):
    # Extract the deck number from the address
    deck_num = int(address.split("/deck")[1].split("/")[0])
    bpm_data[deck_num] = args[0]
    print(f"Deck {deck_num} - BPM: {bpm_data[deck_num]}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="0.0.0.0", help="The IP address to listen on")
    parser.add_argument("--port", type=int, default=7000, help="The port to listen on")

    args = parser.parse_args()

    # Create an OSC dispatcher to handle incoming messages
    osc_dispatcher = dispatcher.Dispatcher()
    osc_dispatcher.map("/pangolin/mixer/activedeck", handle_active_deck)
    for i in range(1, 5):
        osc_dispatcher.map(f"/pangolin/deck{i}/bpm", handle_bpm)

    # Create an OSC server
    osc_server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), osc_dispatcher)
    print(f"Listening for OSC data on {args.ip}:{args.port}")

    # Start the OSC server
    osc_server.serve_forever()
