import asyncio
import logging
from shared_state import shared_state
from routing_algorithms import (
    round_robin,
    weighted_round_robin,
    least_connection_request_sent,
    least_connection_response_received,
    consistent_hashing,
)


async def load_balancer():
    lb = await asyncio.start_server(handle_client, "127.0.0.1", 65433)
    logging.info(f"Server started. Listening on 127.0.0.1:65433")

    async with lb:
        await lb.serve_forever()


async def handle_client(reader, writer):
    args = shared_state.get_args()
    try:
        request = await reader.read(4096)
        if not request:
            return

        client_address = writer.get_extra_info("peername")
        logging.info(f"Request from {client_address[0]}:{client_address[1]}")

        async with shared_state.servers_lock:
            # routing algorithm
            if args.routing_algorithm == "round_robin":
                server = round_robin()
            elif args.routing_algorithm == "weighted_round_robin":
                server = weighted_round_robin()
            elif args.routing_algorithm == "least_connection":
                server = await least_connection_request_sent()
            elif args.routing_algorithm == "consistent_hashing":
                server = await consistent_hashing(
                    f"{client_address[0]}:{client_address[1]}"
                )
            else:
                raise ValueError(f"Invalid algorithm {server.routing_algorithm}.")
            if not server:
                logging.error("No healthy server")
                writer.close()
                await writer.wait_closed()
                return

        logging.info(f"Request routed to server {server}")
        await forward_request_to_backend(server, request, writer, args)

    except Exception as e:
        logging.error(f"Error Handling Client: {e}")
    finally:
        writer.close()
        await writer.wait_closed()


def check_status_code(backend_response):
    status_line = backend_response.split(b"\r\n")[0]
    return int(status_line.split()[1])


# retry Mechanism
async def forward_request_to_backend(server, request, writer, args):
    logging.debug(f"Attempting to forward request to {server}")
    host, port = server.split(":")
    port = int(port)
    backoff = args.backoff
    for attempt in range(args.retries):
        try:
            # create connection with backend and send request
            reader_backend, writer_backend = await asyncio.open_connection(host, port)
            writer_backend.write(request)
            await writer_backend.drain()
            logging.info(f"Request forwarded to {server} successfully")

            # Response from backend
            backend_response = await asyncio.wait_for(
                reader_backend.read(), timeout=args.timeout
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
                    reader_backend.read(), timeout=args.timeout
                )
            if args.routing_algorithm == "least_connection":
                await least_connection_response_received(server)
            logging.info(f"Successful response from {server}")
            break  # Successful response, exit retry loop

        except asyncio.TimeoutError:
            logging.error(
                f"Attempt {attempt + 1} failed to connect to {host}:{port} - Timeout error"
            )

        except Exception as e:
            logging.error(
                f"Attempt {attempt + 1} failed to connect to {host}:{port} - {e}"
            )

        await asyncio.sleep(backoff)
        backoff *= args.exponential_factor
