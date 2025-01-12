import asyncio
from shared_state import shared_state
from routing_algorithms import round_robin, weighted_round_robin


async def load_balancer():
    lb = await asyncio.start_server(handle_client, "127.0.0.1", 65433)
    print(f"Server started. Listening on 127.0.0.1:65433")

    async with lb:
        await lb.serve_forever()


async def handle_client(reader, writer):
    args = shared_state.get_args()
    try:
        request = await reader.read(4096)
        if not request:
            return

        client_address = writer.get_extra_info("peername")
        print(f"Request from {client_address[0]}:{client_address[1]}")

        async with shared_state.servers_lock:
            if not shared_state.healthy_servers:
                print("No healthy server")
                writer.close()
                await writer.wait_closed()
                return

            # Round Robin routing
            # server = round_robin()

            # Weighted Round Robin routing
            server = weighted_round_robin()

        host, port = server.split(":")
        port = int(port)
        print(f"Request routed to server {host}:{port}")

        await forward_request_to_backend(host, port, request, writer, args)

    except Exception as e:
        print(f"Error Handling Client: {e}")
    finally:
        writer.close()
        await writer.wait_closed()


def check_status_code(backend_response):
    status_line = backend_response.split(b"\r\n")[0]
    return int(status_line.split()[1])


# retry Mechanism
async def forward_request_to_backend(host, port, request, writer, args):
    backoff = args.backoff
    for attempt in range(args.retries):
        try:
            # create connection with backend and send request
            reader_backend, writer_backend = await asyncio.open_connection(host, port)
            writer_backend.write(request)
            await writer_backend.drain()

            # Response from backend
            backend_response = await asyncio.wait_for(
                reader_backend.read(4096), timeout=2
            )

            # check for status code = 200
            status_code = check_status_code(backend_response)
            if status_code != 200:
                raise Exception(f"Received HTTP {status_code} response from backend")

            # read remaining response from backend
            while backend_response:
                writer.write(backend_response)
                await writer.drain()
                backend_response = await asyncio.wait_for(
                    reader_backend.read(4096), timeout=2
                )

            break  # Successful response, exit retry loop

        except asyncio.TimeoutError:
            print(
                f"Attempt {attempt + 1} failed to connect to {host}:{port} - Timeout error"
            )

        except Exception as e:
            print(f"Attempt {attempt + 1} failed to connect to {host}:{port} - {e}")

        await asyncio.sleep(backoff)
        backoff *= args.exponential_factor
