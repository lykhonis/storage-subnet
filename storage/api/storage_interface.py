import torch
import base64
import bittensor
import bittensor as bt

from storage.validator.cid import generate_cid_string
from storage.validator.encryption import encrypt_data, decrypt_data_with_private_key
from storage.protocol import StoreUser, RetrieveUser


async def ping_uids(dendrite, metagraph, uids, timeout=3):
    """
    Ping a list of UIDs to check their availability.
    Returns a tuple with a list of successful UIDs and a list of failed UIDs.
    """
    axons = [metagraph.axons[uid] for uid in uids]
    try:
        responses = await dendrite(
            axons,
            bt.Synapse(),  # TODO: potentially get the synapses available back?
            deserialize=False,
            timeout=timeout,
        )
        successful_uids = [
            uid
            for uid, response in zip(uids, responses)
            if response.dendrite.status_code == 200
        ]
        failed_uids = [
            uid
            for uid, response in zip(uids, responses)
            if response.dendrite.status_code != 200
        ]
    except Exception as e:
        bt.logging.error(f"Dendrite ping failed: {e}")
        successful_uids = []
        failed_uids = uids
    bt.logging.debug("ping() successful uids:", successful_uids)
    bt.logging.debug("ping() failed uids    :", failed_uids)
    return successful_uids, failed_uids


async def get_query_api_nodes(dendrite, metagraph, n=0.1, timeout=3):
    """Fetch the available API nodes to query for the particular subnet."""
    bt.logging.debug(f"Fetching available API nodes for subnet {metagraph.netuid}")
    vtrust_uids = [
        uid.item() for uid in metagraph.uids if metagraph.validator_trust[uid] > 0
    ]
    top_uids = torch.where(metagraph.S > torch.quantile(metagraph.S, 1 - n))
    top_uids = top_uids[0].tolist()
    init_query_uids = set(top_uids).intersection(set(vtrust_uids))
    query_uids, _ = await ping_uids(
        dendrite, metagraph, init_query_uids, timeout=timeout
    )
    bt.logging.debug(
        f"Available API node UIDs for subnet {metagraph.netuid}: {init_query_uids}"
    )
    return query_uids


async def get_query_api_axons(dendrite, metagraph, n=0.1, timeout=3):
    query_uids = await get_query_api_nodes(dendrite, metagraph, n=n, timeout=timeout)
    return [metagraph.axons[uid] for uid in query_uids]


async def store_data(
    data: bytes,
    wallet: "bt.wallet",
    metagraph: "bt.metagraph" = None,
    deserialize: bool = False,
    encrypt=False,
    ttl=60 * 60 * 24 * 30, # 30 days default
    timeout=180,
    n=0.1,
    ping_timeout=3,
    encoding="utf-8",
) -> str:

    data = bytes(data, encoding) if isinstance(data, str) else data
    encrypted_data, encryption_payload = encrypt_data(data, wallet) if encrypt else (data, "{}")
    expected_cid = generate_cid_string(encrypted_data)
    encoded_data = base64.b64encode(encrypted_data)

    synapse = StoreUser(
        encrypted_data=encoded_data,
        encryption_payload=encryption_payload,
        ttl=ttl,
    )

    dendrite = bt.dendrite(wallet=wallet)
    if metagraph is None:
        metagraph = bt.metagraph(21)

    axons = await get_query_api_axons(
        dendrite=dendrite,
        metagraph=metagraph,
        n=n,
        timeout=ping_timeout,
    )

    with bt.__console__.status(":satellite: Retreiving data..."):
        responses = await dendrite(
            axons, 
            synapse, 
            timeout=timeout, 
            deserialize=False
        )

        bt.logging.debug(
            "axon responses:", [resp.dendrite.dict() for resp in responses]
        )

    success = False
    failure_modes = {"code": [], "message": []}
    for response in responses:
        if response.dendrite.status_code != 200:
            failure_modes["code"].append(response.dendrite.status_code)
            failure_modes["message"].append(response.dendrite.status_message)
            continue

        stored_cid = (
            response.data_hash.decode("utf-8")
            if isinstance(response.data_hash, bytes)
            else response.data_hash
        )
        bt.logging.debug("received data hash: {}".format(stored_cid))

        if stored_cid != expected_cid:
            bt.logging.warning(
                f"Received CID {stored_cid} does not match expected CID {expected_cid}."
            )
        success = True
        break

    if success:
        bt.logging.info(
            f"Stored data on the Bittensor network with hash {stored_cid}"
        )
    else:
        bt.logging.error(
            f"Failed to store data. Response failure codes & messages {failure_modes}"
        )
        stored_cid = ""

    return stored_cid


async def retrieve_data(cid: str, wallet: "bt.wallet", metagraph: "bt.metagraph = None", n=0.1, timeout: int = 180, ping_timeout: int = 3) -> bytes:

    synapse = RetrieveUser(data_hash=cid)
    dendrite = bt.dendrite(wallet=wallet)

    axons = await get_query_api_axons(
        dendrite=dendrite,
        metagraph=metagraph or bt.metagraph(21),
        n=n,
        timeout=ping_timeout,
    )

    with bt.__console__.status(":satellite: Retreiving data..."):
        responses = await dendrite(
            axons, 
            synapse, 
            timeout=timeout, 
            deserialize=False
        )

    success = False
    for response in responses:
        bt.logging.trace(f"response: {response.dendrite.dict()}")
        if (
            response.dendrite.status_code != 200
            or response.encrypted_data is None
        ):
            continue

        # Decrypt the response
        bt.logging.trace(
            f"encrypted_data: {response.encrypted_data[:100]}"
        )
        encrypted_data = base64.b64decode(response.encrypted_data)
        bt.logging.debug(
            f"encryption_payload: {response.encryption_payload}"
        )
        if (
            response.encryption_payload is None
            or response.encryption_payload == ""
            or response.encryption_payload == "{}"
        ):
            bt.logging.warning(
                "No encryption payload found. Unencrypted data."
            )
            decrypted_data = encrypted_data
        else:
            decrypted_data = decrypt_data_with_private_key(
                encrypted_data,
                response.encryption_payload,
                bytes(wallet.coldkey.private_key.hex(), "utf-8"),
            )
        bt.logging.trace(f"decrypted_data: {decrypted_data[:100]}")
        success = True
        break

    if success:
        return decrypted_data
        bt.logging.info("Saved retrieved data to: {}".format(outpath))
    else:
        bt.logging.error("Failed to retrieve data.")

    return b""