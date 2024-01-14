import argparse
from pythonosc import osc_server, dispatcher
import mido
import time
import threading

# Initialize variables for active deck and BPM for each deck
active_deck = 0
bpm_data = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}

# Function to send MIDI notes
def send_midi_notes(bpm, output_port):
    if bpm < 40:
        print("BPM is below 40, not sending MIDI notes.")
        return

    # Calculate the time delay between notes based on the BPM
    note_interval = 60.0 / bpm
    with mido.open_output(output_port) as midi_port:
        while True:
            if active_deck != 0:
                for note in range(16):
                    # Send a MIDI note-on message for each note (adjust the note number as needed)
                    midi_port.send(mido.Message('note_on', note=60 + note, velocity=64))
                    time.sleep(note_interval)
                    # Send a MIDI note-off message to stop the note
                    midi_port.send(mido.Message('note_off', note=60 + note, velocity=64))
                    time.sleep(0.01)

# Callback function to handle active deck data
def handle_active_deck(address, *args):
    global active_deck
    active_deck = args[0]
    print(f"Active Deck: {active_deck}")
    # Start the MIDI thread when active_deck receives a valid value
    if active_deck in bpm_data and bpm_data[active_deck] >= 40:
        midi_thread = threading.Thread(target=send_midi_notes, args=(bpm_data[active_deck], args.output_port))
        midi_thread.start()

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
    parser.add_argument("--output_port", help="The name of the MIDI output port")

    args = parser.parse_args()

    # Create an OSC dispatcher to handle incoming messages
    osc_dispatcher = dispatcher.Dispatcher()
    osc_dispatcher.map("/pangolin/mixer/activedeck", handle_active_deck)
    for i in range(1, 5):
        osc_dispatcher.map(f"/pangolin/deck{i}/bpm", handle_bpm)

    # Start the OSC server in a separate thread
    osc_server_thread = threading.Thread(target=lambda: osc_server.ThreadingOSCUDPServer((args.ip, args.port), osc_dispatcher).serve_forever)
    osc_server_thread.start()
    
    print(f"Listening for OSC data on {args.ip}:{args.port}")

