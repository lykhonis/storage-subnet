import unittest
import subprocess
import time
import pytest
import asyncio
import re
from redis import asyncio as aioredis


REDIS_CONF = "/etc/redis/redis.conf"

def get_redis_password(redis_conf_path):
    try:
        cmd = f"sudo grep -Po '^requirepass \K.*' {redis_conf_path}"
        result = subprocess.run(cmd, shell=True, text=True, capture_output=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return None


def get_redis_config(file_path, setting):
    """Retrieve specific settings from the Redis configuration file."""
    try:
        result = subprocess.check_output(['sudo', 'grep', f'^{setting}', file_path], text=True)
        return result.strip().split('\n')
    except subprocess.CalledProcessError:
        return None


def check_redis_config(file_path, setting, expected_values):
    """Check if Redis configuration contains all expected values for a given setting."""
    actual_values = get_redis_config(file_path, setting)
    return sorted(actual_values) == sorted(expected_values)


@pytest.mark.parametrize("setting, expected_values", [
    ("appendonly", ["appendonly yes"]),
    ("save", ["save 900 1", "save 300 10", "save 60 10000"])
])
def test_redis_configuration(setting, expected_values):
    redis_conf = "/etc/redis/redis.conf"
    assert check_redis_config(redis_conf, setting, expected_values), f"Configuration for '{setting}' does not match expected values."


@pytest.mark.asyncio
async def test_data_persistence():
    redis_password = get_redis_password(REDIS_CONF)
    port = 6379

    assert port is not None, "Redis server port not found"
    client = aioredis.StrictRedis(port=port, db=0, password=redis_password)

    # Insert data into Redis
    await client.set('testkey', 'Hello, Redis!')

    # Restart Redis server
    subprocess.run(['sudo', 'systemctl', 'restart', 'redis-server.service'], check=True)

    # Wait a bit to ensure Redis has restarted
    await asyncio.sleep(5)

    # Reconnect to Redis
    assert port is not None, "Redis server port not found after restart"
    new_redis = aioredis.StrictRedis(port=port, db=0, password=redis_password)

    # Retrieve data from Redis
    value = await new_redis.get('testkey')

    await new_redis.aclose()
    del new_redis

    # Check if the value is what we expect
    assert value.decode('utf-8') == 'Hello, Redis!', 'Data did not persist across restart.'
