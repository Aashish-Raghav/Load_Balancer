import asyncio
from sortedcontainers import SortedList


class SharedState(object):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.args = None

            # Keep track of servers and health
            cls._instance.servers = []
            cls._instance.servers_health = {}
            cls._instance.servers_lock = asyncio.Lock()

            # specific to weighted round robin algorithm
            cls._instance.servers_with_weights = {}

            # specific to least connections algorithm
            cls._instance.queue_lock = asyncio.Lock()
            cls._instance.least_conn_queue = SortedList(key=lambda x: x[0])
            cls._instance.servers_conn = {}

        return cls._instance

    def set_args(cls, args):
        cls._instance.args = args

    def get_args(cls):
        return cls._instance.args

    def add_server(cls, server, weight):
        cls._instance.servers.append(server)
        cls._instance.servers_with_weights[server] = weight
        cls._instance.servers_health[server] = True
        cls._instance.least_conn_queue.add((0, server))
        cls._instance.servers_conn[server] = 0

    def get_server_weight(cls, server):
        return cls._instance.servers_with_weights[server]

    # for server health
    def update_health(cls, server, health_status):
        cls._instance.servers_health[server] = health_status


shared_state = SharedState()
