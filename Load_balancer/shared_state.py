import asyncio


class SharedState(object):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.healthy_servers = []
            cls._instance.servers_lock = asyncio.Lock()
            cls._instance.args = None

        return cls._instance

    @classmethod
    def set_args(cls, args):
        cls._instance.args = args

    @classmethod
    def get_args(cls):
        return cls._instance.args


shared_state = SharedState()
