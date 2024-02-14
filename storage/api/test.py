import bittensor as bt
from storage import StoreUserAPI, RetrieveUserAPI, APIRegistry
bt.trace()

async def test_vanilla():
    # Example usage
    wallet = bt.wallet()

    store_handler = StoreUserAPI(wallet)

    metagraph = bt.subtensor("test").metagraph(netuid=22)

    cid = await store_handler(
        metagraph=metagraph,
        # any arguments for the proper synapse
        data=b"some data to store",
        encrypt=True,
        ttl=60 * 60 * 24 * 30,
        encoding="utf-8",
        uid=None,
        timeout=60,
    )
    print(cid)

    retrieve_handler = RetrieveUserAPI(wallet)
    retrieve_response = await retrieve_handler(metagraph=metagraph, cid=cid, timeout=60)
    print(retrieve_response)

async def test_registry():
    wallet = bt.wallet()
    metagraph = bt.subtensor("test").metagraph(netuid=22)

    # Dynamically get a StoreUserAPI handler by name & args
    store_handler = APIRegistry.get_api_handler("store_user", wallet)

    # OR equivalently call the registry directly to get the handler you want by name & args
    registry = APIRegistry()
    store_handler = registry("store_user", wallet)

    bt.logging.info(f"Initiating store_handler: {store_handler}")
    cid = await store_handler(
        metagraph=metagraph,
        data=b"some data",
        encrypt=False,
        ttl=60 * 60 * 24 * 30,
        encoding="utf-8",
        uid=None,
    )

    # Dynamically get a RetrieveUserAPI handler
    retrieve_handler = APIRegistry.get_api_handler("retrieve_user", wallet)
    bt.logging.info(f"Initiating retrieve_handler: {retrieve_handler}")
    retrieve_response = await retrieve_handler(metagraph=metagraph, cid=cid)


async def test_dummy():
    from storage import APIRegistry
    print("Importing base registry from bittensor...")
    print(APIRegistry)
    from template import DummyAPI
    print("Importing dummy API from template...")
    print(APIRegistry)
    from storage import StoreUserAPI, RetrieveUserAPI
    print("Importing storage API from storage...")
    print(APIRegistry)