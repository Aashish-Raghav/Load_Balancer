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
        "-t",
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

    args = parser.parse_args()
    shared_state.set_args(args)
    asyncio.run(main())
