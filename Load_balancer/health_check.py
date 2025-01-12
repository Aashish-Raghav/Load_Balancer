import asyncio
import aiohttp
from shared_state import shared_state


def add_protocol(server):
    if not (server.startswith("http://") or server.startswith("https://")):
        server = "http://" + server
    return server


async def server_health_check():
    args = shared_state.get_args()
    servers = args.servers
    interval = args.interval

    while True:
        temporary_healthy_servers = []
        async with aiohttp.ClientSession() as session:
            for server in servers:
                try:
                    async with session.get(add_protocol(server), timeout=2) as response:
                        assert response.status == 200
                        print(f"{server} status: 200")
                        temporary_healthy_servers.append(server)
                except Exception:
                    print(f"{server} is unreachable")

        async with shared_state.servers_lock:
            shared_state.healthy_servers[:] = temporary_healthy_servers
        await asyncio.sleep(interval)
