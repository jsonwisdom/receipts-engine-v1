#!/bin/bash

ADDR=0x082836b2A8E2a77Cca7DDd9F9fC8eE99F884F58D
RPC=https://mainnet.base.org

if [ $# -ne 4 ]; then
  echo "Usage: ./emit.sh AGENT_ID TRADE_ID COMMITMENT_HASH URI"
  exit 1
fi

AGENT="$1"
TRADE="$2"
HASH="$3"
URI="$4"

cast send $ADDR \
  'emitProof(string,string,bytes32,string)' \
  "$AGENT" \
  "$TRADE" \
  "$HASH" \
  "$URI" \
  --rpc-url $RPC \
  --private-key $PRIVATE_KEY
