import asyncio
import logging
import sys

from walkingpadfitbit.auth.client import get_client
from walkingpadfitbit.auth.config import Settings
from walkingpadfitbit.domain.eventhandler import TreadmillEventHandler
from walkingpadfitbit.interfaceadapters.cli.argparser import CliArgs, parse_args
from walkingpadfitbit.interfaceadapters.cli.logincli import login_cli
from walkingpadfitbit.interfaceadapters.fitbit.remoterepository import (
    FitbitRemoteActivityRepository,
)
from walkingpadfitbit.interfaceadapters.walkingpad.monitor import monitor


async def main(
    env_file: str = ".env",
):
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stderr,
        format="[%(asctime)s][%(levelname)-7s][%(name)-10s] %(message)s",
    )

    # Get command-line arguments.
    args: CliArgs = parse_args()

    # Log into Fitbit
    settings = Settings(_env_file=env_file)
    oauth_settings = {
        "client_id": settings.fitbit_oauth_client_id,
        "client_secret": settings.fitbit_oauth_client_secret,
    }
    client = get_client(**oauth_settings)
    if not client:
        await login_cli(**oauth_settings)
        client = get_client(**oauth_settings)

    # Start monitoring
    remote_activity_repository = FitbitRemoteActivityRepository(client)
    treadmill_event_handler = TreadmillEventHandler(
        remote_activity_repository=remote_activity_repository,
    )
    await monitor(
        device_name=args.device_name,
        treadmill_event_handler=treadmill_event_handler,
        monitor_duration_s=args.monitor_duration_s,
        poll_interval_s=args.poll_interval_s,
    )


if __name__ == "__main__":
    asyncio.run(main())
