import socket


# define host and port
HOST = "127.0.0.1"  # local host, server listens only on the loopback interface.
PORT_BE = 65434


def backend_server():
    be_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    be_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    be_socket.bind((HOST, PORT_BE))
    be_socket.listen(5)

    print(f"Server started. Listening on {HOST}:{PORT_BE}...")

    try:
        while True:
            lb_socket, lb_address = be_socket.accept()
            print(f"./be \r\n Received request from {lb_address[0]}")

            # receive data from load_balancer
            request = lb_socket.recv(1024)
            if not request:
                break
            print(request.decode())

            # Create a valid HTTP response
            response_body = "Hello From Backend Server"
            response_headers = (
                "HTTP/1.1 200 OK\r\n"
                f"Content-Length: {len(response_body)}\r\n"
                "Content-Type: text/plain\r\n"
                "Connection: close\r\n\r\n"
            )
            response = response_headers + response_body
            lb_socket.sendall(response.encode())

            print("Replied with Hello Message")
            lb_socket.close()

    except KeyboardInterrupt:
        print("\nBackend Server is shutting down.")

    finally:
        # Close the server socket
        be_socket.close()


if __name__ == "__main__":
    backend_server()
