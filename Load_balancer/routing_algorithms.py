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


async def least_connection_request_sent():
    async with shared_state.queue_lock:
        if len(shared_state.least_conn_queue) == 0:
            return None
        # least connected server
        server = shared_state.least_conn_queue[0]
        shared_state.least_conn_queue.discard(server)
        # increase connection by 1
        shared_state.servers_conn[server[1]] = server[0] + 1
        shared_state.least_conn_queue.add((server[0] + 1, server[1]))

        print(f"list during request")
        for i in shared_state.least_conn_queue:
            print(i, end=" ")
        print("\n")

        return server[1]


async def least_connection_response_received(server):
    # decrement connection count by 1
    async with shared_state.queue_lock:
        if (shared_state.servers_conn[server], server) in shared_state.least_conn_queue:
            shared_state.least_conn_queue.discard(
                (shared_state.servers_conn[server], server)
            )
            shared_state.servers_conn[server] = shared_state.servers_conn[server] - 1
            shared_state.least_conn_queue.add(
                (shared_state.servers_conn[server], server)
            )
    async with shared_state.queue_lock:
        print(f"list after response {server}")
        for i in shared_state.least_conn_queue:
            print(i, end=" ")
        print("\n")
