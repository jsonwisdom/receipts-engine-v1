import fs from 'node:fs';

const required = [
  'ETH_RPC_URL',
  'PRIVATE_KEY',
  'ENS_REGISTRY_ADDRESS',
  'PUBLIC_RESOLVER_ADDRESS',
  'DATA_NODE',
  'BATCH_NODE',
  'BATCHES_NODE',
  'RECEIPT_CID',
  'BATCH_ID',
  'MERKLE_ROOT',
  'RECEIPT_HASH'
];
for (const k of required) {
  if (!process.env[k]) {
    console.error(`Missing ${k}`);
    process.exit(2);
  }
}

console.log(JSON.stringify({
  status: 'prepared',
  names: {
    data: 'data.jaywisdom.eth',
    batch: '0001.batches.jaywisdom.eth',
    batches: 'batches.jaywisdom.eth'
  },
  records: {
    receipt_cid: process.env.RECEIPT_CID,
    batch_id: process.env.BATCH_ID,
    merkle_root: process.env.MERKLE_ROOT,
    receipt_hash: process.env.RECEIPT_HASH
  },
  note: 'Replace this scaffold with viem resolver writes using your preferred ENS contracts.'
}, null, 2));
