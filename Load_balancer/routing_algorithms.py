from shared_state import shared_state

curr_index = 0
curr_weight = 0
curr_server = ""


def round_robin():
    global curr_index
    server = shared_state.healthy_servers[
        curr_index % len(shared_state.healthy_servers)
    ]
    curr_index = (curr_index + 1) % len(shared_state.healthy_servers)
    return server


def weighted_round_robin():
    global curr_index, curr_weight, curr_server
    curr_index == curr_index % len(shared_state.healthy_servers)

    # checking last server
    if curr_server == shared_state.healthy_servers[curr_index]:
        server_weight = shared_state.get_server_weight(
            shared_state.healthy_servers[curr_index]
        )
        if curr_weight >= server_weight:
            curr_index = (curr_index + 1) % len(shared_state.healthy_servers)
            curr_weight = 0
    # routing to new server
    else:
        curr_weight = 0

    curr_server = shared_state.healthy_servers[curr_index]
    curr_weight = curr_weight + 1
    return curr_server
