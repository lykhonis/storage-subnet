#!/usr/bin/env python

import asyncio
import argparse
import bittensor as bt
from redis import asyncio as aioredis

from storage.miner.database import purge_expired_ttl_keys


async def main(args):
    try:
        database = aioredis.StrictRedis(db=args.database_index)

        bt.logging.info(
            f"Purging expired TTL keys from database {args.database_index}..."
        )

        await purge_expired_ttl_keys(database)

    finally:
        if "subtensor" in locals():
            subtensor.close()
            bt.logging.debug("closing subtensor connection")


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--netuid", type=int, default=21)
        parser.add_argument("--database_index", type=int, default=0)
        args = parser.parse_args()

        asyncio.run(main(args))
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    except ValueError as e:
        print(f"ValueError: {e}")
