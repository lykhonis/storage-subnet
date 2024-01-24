#!/bin/bash

generate_password() {
    openssl rand -base64 20
}

REDIS_PASSWORD=$(generate_password)

redis-cli shutdown

sleep 5

if lsof -i :6379; then
    echo "Redis is still running. Attempting to force stop..."
    sudo kill $(sudo lsof -t -i :6379)
    sleep 5
fi

redis-server --requirepass "$REDIS_PASSWORD"

export REDIS_PASSWORD
