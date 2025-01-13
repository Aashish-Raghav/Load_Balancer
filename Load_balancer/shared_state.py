import asyncio


class SharedState(object):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.servers = []
            cls._instance.args = None
            # specific to weighted round robin
            cls._instance.servers_with_weights = {}
            # dict to keep track of health of server
            cls._instance.servers_health = {}
            cls._instance.servers_lock = asyncio.Lock()

        return cls._instance

    def set_args(cls, args):
        cls._instance.args = args

    def get_args(cls):
        return cls._instance.args

    def add_server(cls, server, weight):
        cls._instance.servers.append(server)
        cls._instance.servers_with_weights[server] = weight

    def get_server_weight(cls, server):
        return cls._instance.servers_with_weights[server]

    # for server health
    def update_health(cls, server, health_status):
        cls._instance.servers_health[server] = health_status


shared_state = SharedState()
