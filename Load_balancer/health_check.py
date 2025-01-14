import asyncio
import aiohttp
from shared_state import shared_state


def add_protocol(server):
    if not (server.startswith("http://") or server.startswith("https://")):
        server = "http://" + server

    # for checking least connections
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
                            add_protocol(server), timeout=args.timeout
                        ) as response:
                            assert response.status == 200
                            print(f"{server} status: 200")

                            # if server become healhty add it to conn_pool
                            async with shared_state.queue_lock:
                                if shared_state.servers_health[server] == False:
                                    shared_state.least_conn_queue.add((0, server))

                            shared_state.servers_health[server] = True
                    except Exception:

                        # if server become unhealty remove it from connection list
                        async with shared_state.queue_lock:
                            if shared_state.servers_health[server] == True:
                                shared_state.least_conn_queue.remove(
                                    (shared_state.servers_conn[server], server)
                                )

                        shared_state.servers_health[server] = False
                        print(f"{server} is unreachable")
        async with shared_state.queue_lock:
            print(f"list during request")
            for i in shared_state.least_conn_queue:
                print(i, end=" ")
            print("\n")
        await asyncio.sleep(interval)
