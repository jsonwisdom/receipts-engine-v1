import fs from 'node:fs';
import { keccak256 } from 'viem';

const leafPath = process.argv[2] || '_truth/apple/april26_leaf.json';
const outPath = process.argv[3] || 'golden-v1-final/receipt.json';

function stableStringify(value) {
  if (value === null) return 'null';
  if (typeof value === 'number') return JSON.stringify(value);
  if (typeof value === 'boolean') return value ? 'true' : 'false';
  if (typeof value === 'string') return JSON.stringify(value);
  if (Array.isArray(value)) return '[' + value.map(stableStringify).join(',') + ']';
  const keys = Object.keys(value).sort();
  return '{' + keys.map(k => JSON.stringify(k) + ':' + stableStringify(value[k])).join(',') + '}';
}

function hexToBytes(hex) {
  const clean = hex.startsWith('0x') ? hex.slice(2) : hex;
  return Uint8Array.from(clean.match(/.{1,2}/g).map(h => parseInt(h, 16)));
}

function bytesToHex(bytes) {
  return '0x' + Array.from(bytes, b => b.toString(16).padStart(2, '0')).join('');
}

function concatBytes(...parts) {
  const total = parts.reduce((n, p) => n + p.length, 0);
  const out = new Uint8Array(total);
  let off = 0;
  for (const p of parts) {
    out.set(p, off);
    off += p.length;
  }
  return out;
}

function uint256Be32(n) {
  const out = new Uint8Array(32);
  let x = BigInt(n);
  for (let i = 31; i >= 0; i--) {
    out[i] = Number(x & 0xffn);
    x >>= 8n;
  }
  return out;
}

const leaf = JSON.parse(fs.readFileSync(leafPath, 'utf8'));
const leafCanon = stableStringify(leaf);
const leafHash = keccak256(new TextEncoder().encode(leafCanon)).toLowerCase();
const leaves = [leafHash];
const merkleRoot = leafHash;
const batchId = keccak256(concatBytes(hexToBytes(leafHash), hexToBytes(merkleRoot), uint256Be32(1))).toLowerCase();

const receipt = {
  version: '1.0.0',
  batch_id: batchId,
  merkle_root: merkleRoot,
  receipt_hash: null,
  leaf_count: 1,
  leaves,
  provenance: {
    gcs_bucket: 'observer-network',
    gcs_prefix: 'apple/april26',
    timestamp_utc: leaf.captured_at_utc,
    manifest_cid: null
  },
  hard_rules: {
    sorting: 'lexicographical',
    normalization: 'lowercase_hex',
    merkle_domain_separation: '0x00_leaf_0x01_node',
    receipt_hash_derivation: 'keccak256(receipt_json_with_null_hash)',
    canonicalization: 'stable_stringify_sorted_keys'
  }
};

const preimage = stableStringify(receipt);
receipt.receipt_hash = keccak256(new TextEncoder().encode(preimage)).toLowerCase();

fs.mkdirSync(require('node:path').dirname(outPath), { recursive: true });
fs.writeFileSync(outPath, JSON.stringify(receipt, null, 2) + '\n');
console.log(JSON.stringify({ status: 'built', leafPath, outPath, batch_id: receipt.batch_id, merkle_root: receipt.merkle_root, receipt_hash: receipt.receipt_hash }, null, 2));
