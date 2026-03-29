import socket
import sys
from utils.load_config import app_config as config
from utils.messaging import send_message, receive_message
import json
import threading

port = config["server"]["port"]
host = config["server"]["host"]


class Message:
    def __init__(self, action, from_user, to_user, msg):
        self.message_dict = {
            "action": action,
            "from": from_user,
            "to": to_user,
            "message": msg,
        }

    def to_json(self):
        return json.dumps(self.message_dict)


class GreetingMessage(Message):
    def __init__(self, from_user):
        super().__init__("greeting", from_user, None, "Hello, server!")


class BroadcastMessage(Message):
    def __init__(self, from_user, msg):
        super().__init__("broadcast", from_user, None, msg)


def listen_for_messages(sock, username):
    try:
        while True:
            message = receive_message(sock)
            if not message:
                print("\n[Disconnected from server]")
                break

            if message.get("action") == "broadcast":
                from_user = message.get("from", "Unknown")
                msg_content = message.get("message", "")
                print(f"\n{from_user}: {msg_content}")
                print(f"{username}: ", end="", flush=True)

            elif message.get("action") == "user_joined":
                print(f"\n[{message.get('message')}]")
                print(f"{username}: ", end="", flush=True)

            elif message.get("action") == "user_left":
                print(f"\n[{message.get('message')}]")
                print(f"{username}: ", end="", flush=True)

    except Exception as e:
        print(f"\n[Error receiving messages: {e}]")


def main():
    sock = None
    addr_info_list = socket.getaddrinfo(
        host,
        port=port,
        family=socket.AF_UNSPEC,
        type=socket.SOCK_STREAM,
    )
    for addr in addr_info_list:
        family, socktype, proto, canonname, sockaddr = addr
        try:
            sock = socket.socket(family, socktype, proto)
        except OSError:
            sock = None
            continue
        try:
            sock.connect(sockaddr)
        except OSError:
            sock.close()
            sock = None
            continue
        break

    if sock is None:
        print("Could not connect to any address.")
        sys.exit(1)

    try:
        name = input("Enter your name: ")

        send_message(sock, GreetingMessage(name))

        listen_thread = threading.Thread(
            target=listen_for_messages, args=(sock, name), daemon=True
        )
        listen_thread.start()

        while True:
            msg = input(f"{name}: ")
            if msg.lower() == "quit":
                break
            send_message(sock, BroadcastMessage(name, msg))

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
