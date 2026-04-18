async function loadJSON(path) {
  const res = await fetch(path);
  return res.json();
}

function el(id) { return document.getElementById(id); }
function setText(id, val) {
  const e = el(id);
  if (e) e.textContent = val ?? '';
}
function setStatus(id, pass) {
  const e = el(id);
  if (!e) return;
  e.textContent = pass ? 'PASS' : 'FAIL';
  e.className = pass ? 'value ok' : 'value bad';
}

function bytesToHex(bytes) {
  return '0x' + Array.from(bytes, b => b.toString(16).padStart(2, '0')).join('');
}

function hexToBytes(hex) {
  const clean = hex.startsWith('0x') ? hex.slice(2) : hex;
  if (clean.length % 2 !== 0) throw new Error('invalid hex');
  return Uint8Array.from(clean.match(/.{1,2}/g).map(h => parseInt(h, 16)));
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
  const bytes = Uint8Array.from(hex.slice(2).match(/.{1,2}/g).map(h => parseInt(h, 16)));
  const cidBytes = bytes.slice(2);
  return 'b' + encodeBase32(cidBytes);
}

async function resolveCidByEnsName(name, cfg) {
  const { createPublicClient, http, parseAbi, namehash } = window.viem;
  const abi = parseAbi(['function contenthash(bytes32 node) view returns (bytes)']);
  const client = createPublicClient({ transport: http(cfg.ens_rpc) });
  const node = namehash(name);
  const contenthash = await client.readContract({
    address: cfg.public_resolver,
    abi,
    functionName: 'contenthash',
    args: [node]
  });
  const hex = bytesToHex(contenthash);
  return contenthashHexToCid(hex);
}

async function loadReceipt(cid, gateway) {
  const url = gateway + cid;
  const res = await fetch(url);
  const data = await res.json();
  return { data, url };
}

function stableStringify(value) {
  if (value === null) return 'null';
  if (typeof value === 'number') return JSON.stringify(value);
  if (typeof value === 'boolean') return value ? 'true' : 'false';
  if (typeof value === 'string') return JSON.stringify(value);
  if (Array.isArray(value)) return '[' + value.map(stableStringify).join(',') + ']';
  const keys = Object.keys(value).sort();
  return '{' + keys.map(k => JSON.stringify(k) + ':' + stableStringify(value[k])).join(',') + '}';
}

function concatBytes(...parts) {
  const total = parts.reduce((n, p) => n + p.length, 0);
  const out = new Uint8Array(total);
  let offset = 0;
  for (const p of parts) {
    out.set(p, offset);
    offset += p.length;
  }
  return out;
}

function compareBytes(a, b) {
  for (let i = 0; i < Math.min(a.length, b.length); i++) {
    if (a[i] !== b[i]) return a[i] - b[i];
  }
  return a.length - b.length;
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

function keccakHex(bytes) {
  return window.viem.keccak256(bytes);
}

function computeReceiptHash(receipt) {
  const pre = JSON.parse(JSON.stringify(receipt));
  pre.receipt_hash = null;
  const canon = stableStringify(pre);
  return keccakHex(new TextEncoder().encode(canon));
}

function computeNode(aHex, bHex) {
  const a = hexToBytes(aHex.toLowerCase());
  const b = hexToBytes(bHex.toLowerCase());
  const [left, right] = compareBytes(a, b) <= 0 ? [a, b] : [b, a];
  return keccakHex(concatBytes(Uint8Array.from([0x01]), left, right));
}

function computeMerkleRoot(leaves) {
  let level = [...leaves].map(x => x.toLowerCase()).sort();
  if (level.length === 0) throw new Error('no leaves');
  while (level.length > 1) {
    if (level.length % 2 === 1) level.push(level[level.length - 1]);
    const next = [];
    for (let i = 0; i < level.length; i += 2) {
      next.push(computeNode(level[i], level[i + 1]));
    }
    level = next;
  }
  return level[0];
}

function computeBatchId(leaves, root) {
  const sorted = [...leaves].map(x => x.toLowerCase()).sort();
  const leafBytes = sorted.map(hexToBytes);
  const rootBytes = hexToBytes(root);
  const countBytes = uint256Be32(sorted.length);
  const preimage = concatBytes(...leafBytes, rootBytes, countBytes);
  return keccakHex(preimage);
}

function verifyReceipt(data) {
  const rh = computeReceiptHash(data).toLowerCase();
  const mr = computeMerkleRoot(data.leaves).toLowerCase();
  const bid = computeBatchId(data.leaves, mr).toLowerCase();

  const rhPass = rh === String(data.receipt_hash).toLowerCase();
  const mrPass = mr === String(data.merkle_root).toLowerCase();
  const bidPass = bid === String(data.batch_id).toLowerCase();

  setStatus('verifyReceiptHash', rhPass);
  setStatus('verifyMerkleRoot', mrPass);
  setStatus('verifyBatchId', bidPass);
  el('verification').textContent = rhPass && mrPass && bidPass
    ? 'Client-side verification passed.'
    : 'Client-side verification failed.';
}

function renderReceipt(data, cid, url) {
  setText('receiptCid', cid);
  setText('gatewayUrl', url);
  setText('version', data.version);
  setText('leafCount', data.leaf_count);
  setText('batchId', data.batch_id);
  setText('merkleRoot', data.merkle_root);
  setText('receiptHash', data.receipt_hash);
  el('raw').textContent = JSON.stringify(data, null, 2);
  verifyReceipt(data);
}

function renderBatchList(index, gateway) {
  const list = el('batchList');
  list.innerHTML = '';
  index.batches.forEach(b => {
    const btn = document.createElement('button');
    btn.textContent = `${b.id} — ${b.label}`;
    btn.onclick = async () => {
      const { data, url } = await loadReceipt(b.receipt_cid, gateway);
      renderReceipt(data, b.receipt_cid, url);
    };
    list.appendChild(btn);
  });
}

async function main() {
  try {
    const cfg = await loadJSON('./config.json');
    const gateway = cfg.gateway;

    let index;
    try {
      const indexCid = await resolveCidByEnsName(cfg.index_ens_name, cfg);
      index = await loadJSON(gateway + indexCid);
      setText('sourceType', 'ens-index');
    } catch {
      index = await loadJSON('./batches.json');
      setText('sourceType', 'fallback-local');
    }

    renderBatchList(index, gateway);

    let latestCid;
    try {
      latestCid = await resolveCidByEnsName(cfg.ens_name, cfg);
    } catch {
      latestCid = cfg.receipt_cid;
    }

    const { data, url } = await loadReceipt(latestCid, gateway);
    renderReceipt(data, latestCid, url);

    el('status').textContent = 'Loaded';
    el('status').className = 'value ok';
  } catch (err) {
    el('status').textContent = 'Error';
    el('status').className = 'value bad';
    el('verification').textContent = err.message;
  }
}

main();
