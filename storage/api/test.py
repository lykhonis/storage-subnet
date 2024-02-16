import bittensor as bt
from storage import StoreUserAPI, RetrieveUserAPI, get_query_api_axons
bt.trace()

# Example usage
async def test_storage():

    wallet = bt.wallet()

    store_handler = StoreUserAPI(wallet)

    metagraph = bt.subtensor("test").metagraph(netuid=22)
    get_query_api_axons(wallet=wallet, metagraph=metagraph)

    raw_data = b"Hello FileTao!"

    bt.logging.info(f"Storing data {raw_data} on the Bittensor testnet.")
    cid = await store_handler(
        metagraph=metagraph,
        # any arguments for the proper synapse
        data=raw_data,
        encrypt=True,
        ttl=60 * 60 * 24 * 30,
        encoding="utf-8",
        uid=None,
        timeout=60,
    )
    print(cid)

    bt.logging.info(f"Now retrieving data with CID: {cid}")
    retrieve_handler = RetrieveUserAPI(wallet)
    retrieve_response = await retrieve_handler(metagraph=metagraph, cid=cid, timeout=60)
    print(retrieve_response)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_storage())