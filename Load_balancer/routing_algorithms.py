from shared_state import shared_state

curr_index = 0


def round_robin():
    global curr_index
    server = shared_state.healthy_servers[
        curr_index % len(shared_state.healthy_servers)
    ]
    curr_index = (curr_index + 1) % len(shared_state.healthy_servers)
    return server
