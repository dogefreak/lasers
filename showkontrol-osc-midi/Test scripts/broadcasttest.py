import argparse
from pythonosc import udp_client
from pythonosc import dispatcher
from pythonosc import osc_server
import socket

def receive_osc_message(address, *args):
    print(f"Received OSC message: {address}, {args}")

def main(host, port, broadcast_address, receive_port):
    try:
        # Create an OSC server to listen on the receive port
        dispatcher_ = dispatcher.Dispatcher()
        dispatcher_.set_default_handler(receive_osc_message)
        server = osc_server.ThreadingOSCUDPServer((host, receive_port), dispatcher_)
        print(f"Listening for OSC messages on {host}:{receive_port}")
        
        # Set up the UDP client to send broadcast messages
        client = udp_client.SimpleUDPClient(broadcast_address, port)

        # Start the OSC server in a separate thread
        server_thread = server.serve_forever()

        # Broadcast an example OSC message
        client.send_message("/example", 42, 3.14, "Hello, World!")

        # Wait for user input to exit
        input("Press Enter to exit...")
        
        # Stop the OSC server
        server.shutdown()
        server_thread.join()

    except socket.error as e:
        print(f"Socket error: {e}")
    except KeyboardInterrupt:
        print("OSC server terminated.")
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0", help="The host to listen on (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=5005, help="The port to send broadcast messages to (default: 5005)")
    parser.add_argument("--broadcast_address", default="255.255.255.255", help="The broadcast address (default: 255.255.255.255)")
    parser.add_argument("--receive_port", type=int, default=5006, help="The port to listen for OSC messages (default: 5006)")
    args = parser.parse_args()

    main(args.host, args.port, args.broadcast_address, args.receive_port)

