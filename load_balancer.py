import socket
import argparse
from collections import deque
import threading
import time
import requests

# define host and port
HOST = "127.0.0.1"  # local host, server listens only on the loopback interface.
PORT_LB = 65433

healthy_servers = []
servers_lock = threading.Lock()


def load_balancer():
    # create a socket object
    lb_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lb_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    lb_socket.bind((HOST, PORT_LB))

    lb_socket.listen(5)  # maximum number of queued connections

    print(f"Server started. Listening on {HOST}:{PORT_LB}...")

    # having queue index of servers to perform round robin
    curr_index = 0

    try:
        while True:
            # Accept a new connections
            client_socket, client_address = lb_socket.accept()
            print(f"./lb \r\nRecieved request from {client_address[0]}")

            # recieve data from client
            request = client_socket.recv(4096)
            if not request:
                break
            print((request.decode("utf-8")).strip())

            with servers_lock:
                with socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM
                ) as backend_server:
                    # Round robin algorithm
                    server = healthy_servers[(curr_index) % len(healthy_servers)]
                    curr_index = (curr_index + 1) % len(healthy_servers)

                    host, port = server.split(":")
                    port = int(port)

                    # Create a connection to the backend server and forward request
                    backend_server.connect((host, port))
                    backend_server.sendall(request)

                    # Receive response from backend
                    backend_response = backend_server.recv(4096)
                    print(f"Response from server: {backend_response.decode()}")
                    headers, _, body = backend_response.partition(b"\r\n\r\n")

                    # parse content length from headers
                    headers_str = headers.decode()
                    headers_lines = headers_str.split("\r\n")
                    content_length = 0
                    for line in headers_lines:
                        if line.lower().startswith("content-length:"):
                            content_length = (int)(line.split(":")[1].strip())
                            break

                    # send headers to client
                    client_socket.sendall(headers + b"\r\n\r\n")

                    # send already received part
                    bytes_forwarded = len(body)
                    client_socket.sendall(body)

                    # Continue forwarding the rest of the body
                    while bytes_forwarded < content_length:
                        chunk = backend_server.recv(4096)
                        if not chunk:
                            break
                        client_socket.sendall(chunk)
                        bytes_forwarded += len(chunk)

                client_socket.close()

    except KeyboardInterrupt:
        print("\load_balancer is shutting down.")

    finally:
        # Close the server socket
        lb_socket.close()


def add_protocol(server):
    if not server.startswith("http://") or not server.startwith("https://"):
        server = "http://" + server
    return server


def server_health_check(servers, interval):
    global healthy_servers
    while True:
        temporary_healthy_servers = []
        for server in servers:
            try:
                response = requests.get(add_protocol(server), timeout=2)
                print(response)
                if response.status_code == 200:
                    temporary_healthy_servers.append(server)
            except requests.exceptions.RequestException:
                print(f"{server} is unreachable")

        with servers_lock:
            healthy_servers = temporary_healthy_servers

        time.sleep(interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Load Balancer")
    parser.add_argument(
        "-s", "--servers", nargs="+", required=True, help="backend servers"
    )
    parser.add_argument(
        "-t",
        "--interval",
        default=5,
        type=int,
        help="interval in seconds after which check servers health",
    )
    args = parser.parse_args()

    # Start the health check thread
    health_check_thread = threading.Thread(
        target=server_health_check, args=(args.servers, args.interval), daemon=True
    )
    health_check_thread.start()

    # Start load balancer
    load_balancer()
