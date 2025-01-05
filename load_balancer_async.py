import socket
import argparse
from collections import deque
import threading
import asyncio
import time
import requests
import aiohttp

# define host and port
HOST = "127.0.0.1"  # local host, server listens only on the loopback interface.
PORT_LB = 65433

curr_index = 0
healthy_servers = []
servers_lock = asyncio.Lock()


async def load_balancer():
    # create and bind server socket
    lb = await asyncio.start_server(handle_client, HOST, PORT_LB)
    print(f"Server started. Listening on {HOST}:{PORT_LB}")

    async with lb:
        await lb.serve_forever()


# these reader and writer are high level, built on socket internally
async def handle_client(reader, writer):
    global healthy_servers
    global curr_index
    try:
        request = await reader.read(4096)
        if not request:
            return

        client_address = writer.get_extra_info("peername")
        print(f"Request from {client_address[0]}:{client_address[1]}")

        # find the next server to route request
        async with servers_lock:
            if not healthy_servers:
                print("No healthy server")
                writer.close()
                await writer.wait_closed()

            # Round Robin
            server = healthy_servers[(curr_index) % len(healthy_servers)]
            curr_index = (curr_index + 1) % len(healthy_servers)

        host, port = server.split(":")
        port = int(port)
        print(f"Request routed to server {host}:{port}")

        try:
            reader_backend, writer_backend = await asyncio.open_connection(host, port)
            writer_backend.write(request)
            await writer_backend.drain()

            # Response from backend
            while True:
                backend_response = await reader_backend.read(4096)
                if not backend_response:
                    break

                writer.write(backend_response)
                await writer.drain()
        except Exception as e:
            print(f"Failed to connect to {host}:{port} - {e}")
    except:
        print(f"Error Handling Client: {e}")
    finally:
        writer.close()
        await writer.wait_closed()


def add_protocol(server):
    if not server.startswith("http://") or not server.startwith("https://"):
        server = "http://" + server
    return server


async def server_health_check(servers, interval):
    global healthy_servers
    while True:
        temporary_healthy_servers = []
        async with aiohttp.ClientSession() as session:
            for server in servers:
                try:
                    # print(add_protocol(server))
                    async with session.get(add_protocol(server), timeout=2) as response:
                        assert response.status == 200
                        print(f"{server} status: 200")
                        temporary_healthy_servers.append(server)
                except Exception as e:
                    print(f"{server} is unreachable")

        async with servers_lock:
            healthy_servers = temporary_healthy_servers
        await asyncio.sleep(interval)


async def main():
    # Start the health check task
    task1 = asyncio.create_task(server_health_check(args.servers, args.interval))

    # Start load balancer
    task2 = asyncio.create_task(load_balancer())

    await task1
    await task2


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

    asyncio.run(main())
