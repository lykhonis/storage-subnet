#!/usr/bin/env python

import asyncio
import argparse
import bittensor as bt
from redis import asyncio as aioredis

from storage.shared.utils import get_redis_password
from storage.miner.database import purge_expired_ttl_keys


async def main(args):
    try:
        redis_password = get_redis_password(args.redis_password)
        database = aioredis.StrictRedis(
            host=args.database_host,
            port=args.database_port,
            db=args.database_index,
            socket_keepalive=True,
            socket_connect_timeout=300,
            password=redis_password,
        )

        bt.logging.info(
            f"Purging expired TTL keys from database {args.database_index}..."
        )

        await purge_expired_ttl_keys(database)

    except Exception as e:
        bt.logging.error(f"Error purging ttl keys: {e}")

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--netuid", type=int, default=21)
        parser.add_argument("--database_index", type=int, default=0)
        parser.add_argument("--database_host", type=str, default="localhost")
        parser.add_argument("--database_port", type=int, default=6379)
        parser.add_argument("--redis_password", type=str, default=None)
        args = parser.parse_args()

        asyncio.run(main(args))
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    except ValueError as e:
        print(f"ValueError: {e}")
