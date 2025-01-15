import asyncio
import logging
from aiohttp import web
from shared_state import shared_state
from routing_algorithms import consistent_hashing


async def home_handler(request):
    return web.Response(
        text="Load Balancer API is running. Available endpoints:\n"
        "1. POST /add_server - Add a server\n"
        "2. POST /remove_server - Remove a server\n"
        "3. GET /get_server?key=<key> - Get the server responsible for a key\n",
        content_type="text/plain",
    )


async def add_server_handler(request):
    data = await request.json()
    server = data.get("server")
    if not server:
        return web.json_response({"error": "Server address is required"}, status=400)
    logging.info(f"Adding server {server} to the load balancer")

    response = await shared_state.add_server_consistent_hashing(server, 3)
    return web.json_response(response)


async def remove_server_handler(request):
    data = await request.json()
    server = data.get("server")
    if not server:
        return web.json_response({"error": "Server address is required"}, status=400)
    logging.info(f"Removing server {server} from the load balancer")

    response = await shared_state.remove_server_consistent_hashing(server, 3)
    return web.json_response(response)


async def get_server_handler(request):
    key = request.query.get("key")
    if not key:
        return web.json_response({"error": "Client address is required"}, status=400)
    logging.info(f"Getting server for {key} from the load balancer")

    server = await consistent_hashing(key)
    return web.json_response({"server": server})


async def start_api_server():
    app = web.Application()
    app.router.add_get("/", home_handler)
    app.router.add_post("/add_server", add_server_handler)
    app.router.add_post("/remove_server", remove_server_handler)
    app.router.add_get("/get_server", get_server_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 65432)
    logging.info("API server started on port 65432...")
    await site.start()
