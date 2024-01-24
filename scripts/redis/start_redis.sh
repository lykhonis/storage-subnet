#!/bin/bash

generate_password() {
    openssl rand -base64 20
}

REDIS_DIR="$HOME/.redis"
if [ ! -d $REDIS_DIR ]; then
    mkdir -p $REDIS_DIR
fi

REDIS_PASSWD_FILE="$REDIS_DIR/passwd"
if [ -f $REDIS_PASSWD_FILE ]; then
   REDIS_PASSWORD=`cat $REDIS_PASSWD_FILE`
else
   REDIS_PASSWORD=$(generate_password)
fi

redis-cli shutdown

sleep 5

if (sudo lsof -i :6379 | wc -l) > 1; then
    echo "Redis is still running. Attempting to force stop..."
    sudo kill $(sudo lsof -t -i :6379)
    sleep 5
fi

redis-server --requirepass "$REDIS_PASSWORD"

export REDIS_PASSWORD
echo -n $REDIS_PASSWORD > $REDIS_PASSWD_FILE
