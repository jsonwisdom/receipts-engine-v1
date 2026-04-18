async function loadConfig() {
  const res = await fetch('./config.json');
  return res.json();
}

function el(id) { return document.getElementById(id); }
function setText(id, val) {
  const e = el(id);
  if (e) e.textContent = val ?? '';
}

function bytesToHex(bytes) {
  return '0x' + Array.from(bytes, b => b.toString(16).padStart(2, '0')).join('');
}

const BASE32_ALPHABET = 'abcdefghijklmnopqrstuvwxyz234567';
function encodeBase32(bytes) {
  let bits = '';
  for (const b of bytes) bits += b.toString(2).padStart(8, '0');
  let out = '';
  for (let i = 0; i < bits.length; i += 5) {
    const chunk = bits.slice(i, i + 5).padEnd(5, '0');
    out += BASE32_ALPHABET[parseInt(chunk, 2)];
  }
  return out;
}

function contenthashHexToCid(hex) {
  if (!hex || !hex.startsWith('0x')) throw new Error('invalid contenthash');
  const bytes = Uint8Array.from(hex.slice(2).match(/.{1,2}/g).map(h => parseInt(h, 16)));
  if (bytes.length < 3 || bytes[0] !== 0xe3 || bytes[1] !== 0x01) throw new Error('unsupported contenthash codec');
  const cidBytes = bytes.slice(2);
  return 'b' + encodeBase32(cidBytes);
}

async function resolveCidFromEns(cfg) {
  if (!cfg.ens_name) throw new Error('no ens_name in config');
  if (!window.viem) throw new Error('viem not loaded');
  const { createPublicClient, http, parseAbi, namehash } = window.viem;
  const rpc = cfg.ens_rpc || 'https://ethereum.publicnode.com';
  const resolver = cfg.public_resolver;
  if (!resolver) throw new Error('missing public_resolver in config');

  const abi = parseAbi([
    'function contenthash(bytes32 node) view returns (bytes)',
    'function text(bytes32 node, string key) view returns (string)'
  ]);

  const client = createPublicClient({ transport: http(rpc) });
  const node = namehash(cfg.ens_name);
  const contenthash = await client.readContract({ address: resolver, abi, functionName: 'contenthash', args: [node] });
  const hex = bytesToHex(contenthash);
  const cid = contenthashHexToCid(hex);
  return { cid, node, resolver, rpc };
}

async function loadReceiptByCid(cid, gateway) {
  const url = (gateway || 'https://ipfs.io/ipfs/') + cid;
  const res = await fetch(url);
  if (!res.ok) throw new Error('fetch failed');
  const data = await res.json();
  return { url, data };
}

function render(data, cid, url, source) {
  setText('receiptCid', cid);
  setText('gatewayUrl', url);
  setText('sourceType', source);
  setText('version', data.version);
  setText('leafCount', data.leaf_count);
  setText('batchId', data.batch_id);
  setText('merkleRoot', data.merkle_root);
  setText('receiptHash', data.receipt_hash);

  const p = data.provenance || {};
  setText('gcsBucket', p.gcs_bucket);
  setText('gcsPrefix', p.gcs_prefix);
  setText('timestampUtc', p.timestamp_utc);
  setText('manifestCid', p.manifest_cid);

  el('raw').textContent = JSON.stringify(data, null, 2);
  el('status').textContent = 'Loaded';
  el('status').className = 'value ok';
  el('verification').textContent = 'Receipt loaded. For full verification, run verify_batch.py.';
}

async function main() {
  try {
    const cfg = await loadConfig();
    let cid, source = 'config';
    try {
      const ens = await resolveCidFromEns(cfg);
      cid = ens.cid;
      setText('ensName', cfg.ens_name);
      setText('ensRpc', ens.rpc);
      setText('resolverAddress', ens.resolver);
      source = 'ens';
    } catch (err) {
      cid = cfg.receipt_cid;
      setText('ensName', cfg.ens_name || '');
      setText('ensRpc', cfg.ens_rpc || '');
      setText('resolverAddress', cfg.public_resolver || '');
      setText('verification', `ENS resolution failed, fell back to config CID: ${err.message}`);
    }

    const gateway = cfg.gateway || 'https://ipfs.io/ipfs/';
    const { url, data } = await loadReceiptByCid(cid, gateway);
    render(data, cid, url, source);
  } catch (err) {
    el('status').textContent = 'Error loading receipt';
    el('status').className = 'value bad';
    el('verification').textContent = err.message;
  }
}

main();
