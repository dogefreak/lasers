import curses
from pythonosc import dispatcher, osc_server
import threading
import socket
import mido

def get_local_broadcast_address():
    local_ip = socket.gethostbyname(socket.gethostname())
    local_ip_parts = local_ip.split('.')
    local_ip_parts[-1] = '255'
    return '.'.join(local_ip_parts)

def get_ip_address():
    default_broadcast_ip = get_local_broadcast_address()
    user_ip = input(f"Enter the IP address (press Enter for default {default_broadcast_ip}): ").strip()
    return user_ip if user_ip else default_broadcast_ip

def get_port():
    default_port = 7000
    user_port = input(f"Enter the port (press Enter for default {default_port}): ").strip()
    return int(user_port) if user_port else default_port

def select_midi_output_port():
    output_ports = mido.get_output_names()
    if not output_ports:
        print("No MIDI output ports found. Make sure your MIDI device is connected.")
        exit()

    print("Available MIDI output ports:")
    for i, port in enumerate(output_ports):
        print(f"{i + 1}: {port}")

    selected_port_index = input("Select the desired MIDI output port (enter the corresponding number): ")
    try:
        selected_port_index = int(selected_port_index) - 1
        if 0 <= selected_port_index < len(output_ports):
            output_port_name = output_ports[selected_port_index]
        else:
            print("Invalid port number. Exiting.")
            exit()
    except ValueError:
        print("Invalid input. Exiting.")
        exit()

    return mido.open_output(output_port_name)

def send_midi_notes(output_port, active_deck, bpm, feedback_list):
    note_number = 60  # You can change this to the MIDI note you want to use
    notes_per_beat = 4  # Number of notes per beat (adjust as needed)
    beats = 4  # Total beats

    time_interval = 60 / bpm / notes_per_beat

    for beat in range(beats):
        for note in range(notes_per_beat):
            note_on_timestamp = time_interval * (beat + note / notes_per_beat)
            note_off_timestamp = time_interval * (beat + (note + 1) / notes_per_beat)

            note_on_message = mido.Message('note_on', note=note_number, velocity=64, time=note_on_timestamp)
            output_port.send(note_on_message)

            note_off_message = mido.Message('note_off', note=note_number, time=note_off_timestamp)
            output_port.send(note_off_message)

            feedback_list.append(f"Note {note_number} played at {note_on_timestamp:.2f} seconds and released at {note_off_timestamp:.2f} seconds")

deck_parameters = {
    1: {"bpm": 0.00, "active": 0},
    2: {"bpm": 0.00, "active": 0},
    3: {"bpm": 0.00, "active": 0},
    4: {"bpm": 0.00, "active": 0},
}

latest_osc_messages = []
midi_feedback = []

osc_dispatcher = dispatcher.Dispatcher()

def osc_handler(address, *args):
    latest_osc_messages.append((address, args))
    if len(latest_osc_messages) > 3:
        latest_osc_messages.pop(0)
    if address.startswith('/pangolin/deck'):
        deck_number = int(''.join(filter(str.isdigit, address)))
        if deck_number in deck_parameters:
            if address.endswith('/bpm'):
                deck_parameters[deck_number]["bpm"] = args[0]
                active_deck = None
                for deck_num, params in deck_parameters.items():
                    if params["active"] == 1:
                        active_deck = deck_num
                if active_deck is not None:
                    send_midi_notes(output_port, active_deck, bpm, midi_feedback)
    if address.startswith('/pangolin/mixer/activedeck'):
        deck_number = args[0]
        for deck_num in deck_parameters:
            deck_parameters[deck_num]["active"] = 1 if deck_num == deck_number else 0

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
        message_count = len(latest_osc_messages)
        if message_count > 0:
            for i, message in enumerate(reversed(latest_osc_messages)):
                stdscr.addstr(9 + i, 0, f"{message[0]}: {message[1]}")
        stdscr.addstr(12, 0, "MIDI Feedback:")
        if midi_feedback:
            for i, feedback in enumerate(midi_feedback):
                stdscr.addstr(13 + i, 0, feedback)
        stdscr.refresh()

def run_osc_server(ip, port):
    server = osc_server.ThreadingOSCUDPServer((ip, port), osc_dispatcher)
    server.serve_forever()

if __name__ == '__main':
    osc_server_ip = get_ip_address()
    osc_server_port = get_port()
    output_port = select_midi_output_port()
    
    dashboard_thread = threading.Thread(target=curses.wrapper, args=(update_dashboard, osc_server_ip, osc_server_port))
    dashboard_thread.daemon = True
    dashboard_thread.start()

    osc_server_thread = threading.Thread(target=run_osc_server, args=(osc_server_ip, osc_server_port))
    osc_server_thread.daemon = True
    osc_server_thread.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        pass

