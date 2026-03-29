import socket
import sys
from utils.load_config import app_config as config
from utils.logger import app_logger as logger
from utils.messaging import send_message, receive_message
import threading

port = config["server"]["port"]
buffer_size = config["server"]["buffer_size"]

clients = []
clients_lock = threading.Lock()


def broadcast_message(message_dict, sender_conn=None):
    with clients_lock:
        disconnected_clients = []
        for client_info in clients:
            if client_info["conn"] == sender_conn:
                continue

            if not send_message(client_info["conn"], message_dict):
                disconnected_clients.append(client_info)

        for client in disconnected_clients:
            clients.remove(client)
            logger.info("Removed disconnected client: %s", client["username"])


def handle_client(conn, addr):
    username = None
    client_info = None

    try:
        first_message = receive_message(conn)
        if first_message and "from" in first_message:
            username = first_message["from"]
            client_info = {
                "conn": conn,
                "addr": addr,
                "username": username
            }

            with clients_lock:
                clients.append(client_info)

            logger.info("User %s connected from %s", username, addr)

            broadcast_message({
                "action": "user_joined",
                "username": username,
                "message": f"{username} has joined the chat"
            }, sender_conn=conn)

        while True:
            data = receive_message(conn)
            if not data:
                break

            logger.info("Received from %s: %s", username, data)

            broadcast_message(data, sender_conn=conn)

    except Exception as e:
        logger.error("Error handling client %s: %s", username, e)

    finally:
        if client_info:
            with clients_lock:
                if client_info in clients:
                    clients.remove(client_info)

            broadcast_message({
                "action": "user_left",
                "username": username,
                "message": f"{username} has left the chat"
            })

            logger.info("User %s disconnected", username)

        conn.close()


def main():
    sock = None
    addr_info_list = socket.getaddrinfo(
        None,
        port=port,
        family=socket.AF_UNSPEC,
        type=socket.SOCK_STREAM,
        flags=socket.AI_PASSIVE,
    )
    for addr in addr_info_list:
        # (family, type, proto, canonname, sockaddr)
        family, socktype, proto, canonname, sockaddr = addr
        try:
            sock = socket.socket(family, socktype, proto)
        except OSError:
            sock = None
            continue

        # set socket options to allow reuse of address and port
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            sock.bind(sockaddr)
            sock.listen(5)  
        except OSError:
            sock.close()
            sock = None
            continue
        break

    if sock is None:
        logger.error("Could not bind to any address.")
        sys.exit(1)

    logger.info("Server is listening on port %d", port)

    try:
        while True:
            conn, addr = sock.accept()
            logger.info("New connection from %s", addr)

            client_thread = threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True
            )
            client_thread.start()

    except KeyboardInterrupt:
        logger.info("Server shutting down...")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
