#!/bin/bash

RPC=https://mainnet.base.org
ADDR=0x082836b2A8E2a77Cca7DDd9F9fC8eE99F884F58D

if [ ! -f batch.json ]; then
  echo "ERROR: batch.json not found"
  exit 1
fi

BASE_NONCE=$(cast nonce 0xC345B26094c63C69222Ee775189a3d3eaead5a84 --rpc-url $RPC)
i=0

jq -c '.[]' batch.json | while read -r row; do
  AGENT=$(echo "$row" | jq -r '.agentId')
  TRADE=$(echo "$row" | jq -r '.tradeId')
  CANON=$(echo "$row" | jq -r '.canonical')
  URI=$(echo "$row" | jq -r '.uri')
  HASH=$(cast keccak "$CANON")
  NONCE=$((BASE_NONCE + i))

  echo "EMITTING: $AGENT | $TRADE"
  echo "NONCE: $NONCE"
  echo "HASH: $HASH"

  cast send $ADDR \
    'emitProof(string,string,bytes32,string)' \
    "$AGENT" \
    "$TRADE" \
    "$HASH" \
    "$URI" \
    --rpc-url $RPC \
    --private-key $PRIVATE_KEY \
    --nonce $NONCE \
    --gas-price 6000000

  i=$((i + 1))
  sleep 3
  echo "----------------------------------------"
done
