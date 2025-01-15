import asyncio
import hashlib
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

            # specific to consistent hashing algorithm
            cls._instance.sortedKeys = SortedList()
            cls._instance.ring = {}
            cls._instance.ring_lock = asyncio.Lock()
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

    # for consistent hashing
    def get_hash(cls, key):
        _key = str(key)
        return int(hashlib.sha1(_key.encode("utf-8")).hexdigest(), 16)

    async def add_server_consistent_hashing(cls, server, replicas=3):
        exist = 1
        for i in range(replicas):
            replica_key = cls._instance.get_hash(server + "_" + str(i))
            async with shared_state.ring_lock:
                if replica_key not in shared_state.ring:
                    exist = 0
                    shared_state.ring[replica_key] = server
                    shared_state.sortedKeys.add(replica_key)
        if exist:
            return {"error": f"Server {server} already exists"}
        else:
            return {"message": f"Server {server} added successfully"}

    async def remove_server_consistent_hashing(cls, server, replicas=3):
        exist = 0
        for i in range(replicas):
            replica_key = cls._instance.get_hash(server + "_" + str(i))
            async with shared_state.ring_lock:
                if replica_key in shared_state.ring:
                    exist = 1
                    shared_state.ring.pop(replica_key)
                    shared_state.sortedKeys.remove(replica_key)
        if exist:
            return {"message": f"Server {server} removed successfully"}
        else:
            return {"error": f"Server {server} does not exist"}


shared_state = SharedState()
