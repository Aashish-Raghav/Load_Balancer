import asyncio
import argparse
from health_check import server_health_check
from load_balancer import load_balancer
from shared_state import shared_state


async def main():
    # Start health check and load balancer tasks
    task1 = asyncio.create_task(server_health_check())
    task2 = asyncio.create_task(load_balancer())

    await task1
    await task2


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Load Balancer")
    parser.add_argument(
        "-s", "--servers", nargs="+", required=True, help="backend servers"
    )
    parser.add_argument(
        "-i",
        "--interval",
        default=5,
        type=int,
        help="interval in seconds after which check servers health",
    )
    parser.add_argument(
        "-r",
        "--retries",
        default=4,
        type=int,
        help="Number of request retries to server",
    )
    parser.add_argument(
        "-b",
        "--backoff",
        default=0.5,
        type=float,
        help="Initial backoff time after request failure",
    )
    parser.add_argument(
        "-e",
        "--exponential-factor",
        default=1.5,
        type=float,
        help="Exponential Factor to backoff time",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        default=2,
        type=int,
        help="Timeout to wait for response",
    )
    parser.add_argument(
        "-a",
        "--routing-algorithm",
        type=str,
        choices=[
            "round_robin",
            "weighted_round_robin",
            "least_connection",
            "consistent_hashing",
        ],
        default="round_robin",
        help="Specify the routing algorithm to use: round_robin, weighted_round_robin, least_connection or consistent_hashing (default: round_robin)",
    )

    args = parser.parse_args()
    print(args.routing_algorithm)
    shared_state.set_args(args)
    for entry in args.servers:
        try:
            parts = entry.split(":")

            if len(parts) == 3:  # Format: host:port:weight
                server = f"{parts[0]}:{parts[1]}"
                weight = int(parts[2])  # Ensure weight is an integer
            elif len(parts) == 2:  # Format: host:port (no weight provided)
                server = f"{parts[0]}:{parts[1]}"
                weight = 1  # Default weight
            else:
                raise ValueError(
                    f"Invalid server format: {entry}. Use host:port or host:port:weight."
                )
            shared_state.add_server(server, weight)

        except ValueError as ve:
            print(f"Error parsing server entry '{entry}': {ve}. Skipping this server.")
        except Exception as e:
            print(
                f"Unexpected error while parsing '{entry}': {e}. Skipping this server."
            )

    asyncio.run(main())
