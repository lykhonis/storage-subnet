#!/usr/bin/env python

import os
import asyncio
import aioredis
import argparse
import bittensor as bt

from storage.validator.rebalance import rebalance_data


async def main(args):
    try:
        subtensor = bt.subtensor(network=args.network)
        metagraph = bt.metagraph(netuid=args.netuid, network=args.network)
        metagraph.sync(subtensor=subtensor)
        database = aioredis.StrictRedis(db=args.database_index)

        hotkeys = args.hotkeys.split(",")
        bt.logging.info(
            f"Deregistered hotkeys {hotkeys} will be rebalanced in the index."
        )

        self = argparse.Namespace()
        self.metagraph = metagraph
        self.database = database

        await rebalance_data(self, k=2, dropped_hotkeys=hotkeys, hotkey_replaced=True)

    finally:
        if "subtensor" in locals():
            subtensor.close()
            bt.logging.debug("closing subtensor connection")


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--hotkeys",
            type=str,
            required=True,
            help="comma separated list of hotkeys to deregister",
        )
        parser.add_argument("--network", type=str, default="local")
        parser.add_argument("--netuid", type=int, default=21)
        parser.add_argument("--database_index", type=int, default=1)
        args = parser.parse_args()

        asyncio.run(main(args))
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    except ValueError as e:
        print(f"ValueError: {e}")
