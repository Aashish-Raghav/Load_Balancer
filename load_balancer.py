import socket

# define host and port
HOST = "127.0.0.1" # local host, server listens only on the loopback interface.
PORT_LB = 65433
PORT_BE = 65434

def load_balancer():
    # create a socket object
    lb_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    lb_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

    lb_socket.bind((HOST,PORT_LB))

    lb_socket.listen(5) # maximum number of queued connections

    print(f"Server started. Listening on {HOST}:{PORT_LB}...")

    try:
        while True:
            # Accept a new connections
            client_socket,client_address = lb_socket.accept()
            print(f"./lb \r\nRecieved request from {client_address[0]}")

            # recieve data from client
            request = client_socket.recv(1024)
            if not request:
                break
            print((request.decode('utf-8')).strip())
            
            with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as backend_server:
                backend_server.connect((HOST,PORT_BE))
                backend_server.sendall(request)

                backend_response = backend_server.recv(1024)
                print(f"Response from server: {backend_response.decode()}")

                client_socket.sendall(backend_response)

            client_socket.close()


    except KeyboardInterrupt:
        print("\load_balancer is shutting down.")

    finally:
        # Close the server socket
        lb_socket.close()

if __name__ == '__main__':
    load_balancer()