import asyncio
import aiohttp
import logging
from shared_state import shared_state


def add_protocol(server, args):
    if not (server.startswith("http://") or server.startswith("https://")):
        server = "http://" + server

    # for checking least connections
    if args.routing_algorithm == "least_connection":
        server = server + "/health"
    return server


async def server_health_check():
    args = shared_state.get_args()
    servers = shared_state.servers
    interval = args.interval

    while True:
        async with aiohttp.ClientSession() as session:
            for server in servers:
                async with shared_state.servers_lock:
                    try:
                        async with session.get(
                            add_protocol(server, args), timeout=args.timeout
                        ) as response:
                            assert response.status == 200
                            logging.info(f"{server} status: 200")

                            if args.routing_algorithm == "least_connection":
                                # if server become healhty add it to conn_pool
                                async with shared_state.queue_lock:
                                    if shared_state.servers_health[server] == False:
                                        shared_state.least_conn_queue.add((0, server))

                            elif args.routing_algorithm == "consistent_hashing":
                                await shared_state.add_server_consistent_hashing(server)

                            shared_state.servers_health[server] = True

                    except Exception:
                        if args.routing_algorithm == "least_connection":
                            # if server become unhealty remove it from connection list
                            async with shared_state.queue_lock:
                                if shared_state.servers_health[server] == True:
                                    shared_state.least_conn_queue.remove(
                                        (shared_state.servers_conn[server], server)
                                    )

                        elif args.routing_algorithm == "consistent_hashing":
                            await shared_state.remove_server_consistent_hashing(server)

                        shared_state.servers_health[server] = False
                        logging.info(f"{server} is unreachable")

        await asyncio.sleep(interval)
