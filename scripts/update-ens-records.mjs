import { createWalletClient, encodeFunctionData, http, namehash, parseAbi } from 'viem';
import { mainnet } from 'viem/chains';
import { privateKeyToAccount } from 'viem/accounts';

const required = [
  'ETH_RPC_URL',
  'PRIVATE_KEY',
  'PUBLIC_RESOLVER_ADDRESS',
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

const resolverAbi = parseAbi([
  'function multicall(bytes[] data) external returns (bytes[] results)',
  'function setText(bytes32 node, string key, string value) external',
  'function setContenthash(bytes32 node, bytes hash) external'
]);

const BASE32_ALPHABET = 'abcdefghijklmnopqrstuvwxyz234567';
function decodeBase32(s) {
  const clean = s.toLowerCase().replace(/=+$/g, '');
  let bits = '';
  for (const c of clean) {
    const val = BASE32_ALPHABET.indexOf(c);
    if (val === -1) throw new Error(`invalid base32 char: ${c}`);
    bits += val.toString(2).padStart(5, '0');
  }
  const bytes = [];
  for (let i = 0; i + 8 <= bits.length; i += 8) {
    bytes.push(parseInt(bits.slice(i, i + 8), 2));
  }
  return Uint8Array.from(bytes);
}

function bytesToHex(bytes) {
  return '0x' + Array.from(bytes, b => b.toString(16).padStart(2, '0')).join('');
}

function cidV1ToContenthashHex(cid) {
  if (!cid.startsWith('b')) throw new Error('expected base32 CIDv1');
  const cidBytes = decodeBase32(cid.slice(1));
  const proto = Uint8Array.from([0xe3, 0x01]); // ipfs-ns per EIP-1577/multicodec varint
  const out = new Uint8Array(proto.length + cidBytes.length);
  out.set(proto, 0);
  out.set(cidBytes, proto.length);
  return bytesToHex(out);
}

const names = {
  data: 'data.jaywisdom.eth',
  batch: '0001.batches.jaywisdom.eth',
  batches: 'batches.jaywisdom.eth'
};

const nodes = {
  data: namehash(names.data),
  batch: namehash(names.batch),
  batches: namehash(names.batches)
};

const account = privateKeyToAccount(process.env.PRIVATE_KEY);
const client = createWalletClient({
  account,
  chain: mainnet,
  transport: http(process.env.ETH_RPC_URL)
});

const contenthashHex = cidV1ToContenthashHex(process.env.RECEIPT_CID);

const calls = [
  encodeFunctionData({ abi: resolverAbi, functionName: 'setContenthash', args: [nodes.data, contenthashHex] }),
  encodeFunctionData({ abi: resolverAbi, functionName: 'setText', args: [nodes.data, 'com.jaywisdom.version', 'Golden-v1-final'] }),
  encodeFunctionData({ abi: resolverAbi, functionName: 'setText', args: [nodes.data, 'com.jaywisdom.batch', '0001'] }),
  encodeFunctionData({ abi: resolverAbi, functionName: 'setText', args: [nodes.data, 'com.jaywisdom.batchId', process.env.BATCH_ID] }),
  encodeFunctionData({ abi: resolverAbi, functionName: 'setText', args: [nodes.data, 'com.jaywisdom.merkleRoot', process.env.MERKLE_ROOT] }),
  encodeFunctionData({ abi: resolverAbi, functionName: 'setText', args: [nodes.data, 'com.jaywisdom.receiptHash', process.env.RECEIPT_HASH] }),

  encodeFunctionData({ abi: resolverAbi, functionName: 'setContenthash', args: [nodes.batch, contenthashHex] }),
  encodeFunctionData({ abi: resolverAbi, functionName: 'setText', args: [nodes.batch, 'description', 'Golden-v1-final receipt, Merkle-verified, Batch 0001'] }),
  encodeFunctionData({ abi: resolverAbi, functionName: 'setText', args: [nodes.batch, 'com.jaywisdom.batch', '0001'] }),
  encodeFunctionData({ abi: resolverAbi, functionName: 'setText', args: [nodes.batch, 'com.jaywisdom.batchId', process.env.BATCH_ID] }),
  encodeFunctionData({ abi: resolverAbi, functionName: 'setText', args: [nodes.batch, 'com.jaywisdom.merkleRoot', process.env.MERKLE_ROOT] }),
  encodeFunctionData({ abi: resolverAbi, functionName: 'setText', args: [nodes.batch, 'com.jaywisdom.receiptHash', process.env.RECEIPT_HASH] }),

  encodeFunctionData({ abi: resolverAbi, functionName: 'setText', args: [nodes.batches, 'batches.latest', names.batch] }),
  encodeFunctionData({ abi: resolverAbi, functionName: 'setText', args: [nodes.batches, 'batches.batchId', process.env.BATCH_ID] }),
  encodeFunctionData({ abi: resolverAbi, functionName: 'setText', args: [nodes.batches, 'batches.root', process.env.MERKLE_ROOT] }),
  encodeFunctionData({ abi: resolverAbi, functionName: 'setText', args: [nodes.batches, 'batches.receipt', process.env.RECEIPT_CID] })
];

const hash = await client.writeContract({
  address: process.env.PUBLIC_RESOLVER_ADDRESS,
  abi: resolverAbi,
  functionName: 'multicall',
  args: [calls]
});

console.log(JSON.stringify({
  status: 'submitted',
  txHash: hash,
  names,
  nodes,
  receiptCid: process.env.RECEIPT_CID,
  contenthashHex
}, null, 2));
