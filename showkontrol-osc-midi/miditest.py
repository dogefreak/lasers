import mido
import time

# Scan for available MIDI output ports and enumerate them
output_ports = mido.get_output_names()
if not output_ports:
    print("No MIDI output ports found. Make sure your MIDI device is connected.")
    exit()

print("Available MIDI output ports:")
for i, port in enumerate(output_ports):
    print(f"{i + 1}: {port}")

# Ask the user to select a MIDI output port
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

# Open the selected MIDI output port
output_port = mido.open_output(output_port_name)

# Define the MIDI note number for C1
note_number = 24  # C1 is MIDI note 24

try:
    while True:
        # Create a note-on message with a timestamp and send it
        timestamp = time.time()
        note_on_message = mido.Message('note_on', note=note_number, time=timestamp)
        output_port.send(note_on_message)

        # Print the timestamp when the note is played
        print(f"Note C1 played at {timestamp:.2f} seconds")

        # Sleep for one second
        time.sleep(1)

        # Create a note-off message with a timestamp and send it
        timestamp = time.time()
        note_off_message = mido.Message('note_off', note=note_number, time=timestamp)
        output_port.send(note_off_message)

        # Print the timestamp when the note is released
        print(f"Note C1 released at {timestamp:.2f} seconds")

except KeyboardInterrupt:
    # Close the MIDI output port when the script is interrupted
    output_port.close()

