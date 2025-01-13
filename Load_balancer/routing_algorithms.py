from shared_state import shared_state

curr_index = 0
curr_weight = 0
curr_server = None


def round_robin():
    global curr_index, curr_server
    start = curr_index
    while True:
        curr_server = shared_state.servers[curr_index]
        curr_index = (curr_index + 1) % len(shared_state.servers)

        # Healthy server
        if shared_state.servers_health[curr_server]:
            break

        # No healthy server
        if start == curr_index:
            curr_server = None
            break

    return curr_server


def weighted_round_robin():
    global curr_index, curr_weight, curr_server
    start = curr_index
    # checking last server

    while True:
        curr_server = shared_state.servers[curr_index]

        # Healthy server
        if shared_state.servers_health[curr_server] == True:
            server_weight = shared_state.get_server_weight(curr_server)
            if curr_weight >= server_weight:
                curr_index = (curr_index + 1) % len(shared_state.servers)
                curr_weight = 0
            else:
                curr_weight = curr_weight + 1
                break

        # Unhealthy Server
        else:
            curr_index = (curr_index + 1) % len(shared_state.servers)
            # No healthy server
            if curr_index == start:
                curr_server = None
                break

    return curr_server
