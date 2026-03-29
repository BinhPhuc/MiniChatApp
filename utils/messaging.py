import json
import struct
from utils.logger import app_logger as logger


def recvall(sock, n):
    """Receive exactly n bytes from socket."""
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return bytes(data)


def receive_message(sock):
    """Receive a message from socket with length-prefixed protocol."""
    raw_header = recvall(sock, 4)
    if not raw_header:
        return None

    payload_length = struct.unpack(">I", raw_header)[0]

    raw_payload = recvall(sock, payload_length)
    if not raw_payload:
        return None

    json_string = raw_payload.decode("utf-8")
    message_dict = json.loads(json_string)

    return message_dict


def send_message(sock, message_dict):
    """Send a message to socket with length-prefixed protocol."""
    try:
        # Handle both dict and objects with to_json() method
        if hasattr(message_dict, 'to_json'):
            payload = message_dict.to_json().encode("utf-8")
        elif isinstance(message_dict, dict):
            payload = json.dumps(message_dict).encode("utf-8")
        else:
            raise ValueError("Message must be a dict or have to_json() method")

        payload_length = len(payload)
        header = struct.pack(">I", payload_length)
        sock.sendall(header + payload)
        return True
    except Exception as e:
        logger.error("Error sending message: %s", e)
        return False
