import socket
import argparse
from collections import deque

# define host and port
HOST = "127.0.0.1"  # local host, server listens only on the loopback interface.
PORT_LB = 65433


def load_balancer(server_count):
    # create a socket object
    lb_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lb_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    lb_socket.bind((HOST, PORT_LB))

    lb_socket.listen(5)  # maximum number of queued connections

    print(f"Server started. Listening on {HOST}:{PORT_LB}...")

    # having queue of servers to perform round robin
    queue = deque([])
    for i in range(0, server_count):
        queue.append(i)

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

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as backend_server:
                # Round robin algorithm
                port = queue[0] + 8080
                queue.append(queue[0])
                queue.popleft()

                # Create a connection to the backend server and forward request
                backend_server.connect((HOST, port))
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Load Balancer")
    parser.add_argument(
        "-s", "--server-count", default=1, type=int, help="Number of backend servers"
    )
    args = parser.parse_args()
    load_balancer(args.server_count)
