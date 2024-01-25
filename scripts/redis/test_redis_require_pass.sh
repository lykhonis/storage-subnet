#!/bin/bash

REDIS_CONF="/etc/redis/redis.conf"

check_redis_access() {
    if redis-cli -a $1 PING &> /dev/null; then
        echo "Access with password: Success"
    else
        echo "Access with password: Failure"
    fi

    if redis-cli PING &> /dev/null; then
        echo "Access without password: Success"
    else
        echo "Access without password: Failure"
    fi
}

REDIS_PASSWORD=$(sudo grep -Po '^requirepass \K.*' $REDIS_CONF)

echo "Testing Redis access..."
check_redis_access $REDIS_PASSWORD
