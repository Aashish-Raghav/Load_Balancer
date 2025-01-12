import asyncio


class SharedState(object):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.healthy_servers = []
            cls._instance.servers_lock = asyncio.Lock()
            cls._instance.args = None
            # specific to weighted round robin
            cls._instance.servers_with_weights = {}

        return cls._instance

    def set_args(cls, args):
        cls._instance.args = args

    def get_args(cls):
        return cls._instance.args

    # specific to weighted round robin
    def add_server(cls, server, weight):
        cls._instance.servers_with_weights[server] = weight

    def get_server_weight(cls, server):
        return cls._instance.servers_with_weights[server]

    def get_servers_list(cls):
        return list(cls._instance.servers_with_weights.keys())


shared_state = SharedState()
