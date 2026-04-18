// FULL RESTORE WITH PER-BATCH DIFF + ENS + VERIFICATION

async function loadJSON(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`failed to load ${path}`);
  return res.json();
}

function el(id) { return document.getElementById(id); }
function setText(id, val) { const e = el(id); if (e) e.textContent = val ?? ''; }
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
  return Uint8Array.from(clean.match(/.{1,2}/g).map(h => parseInt(h, 16)));
}
function concatBytes(...parts) {
  const total = parts.reduce((n, p) => n + p.length, 0);
  const out = new Uint8Array(total);
  let offset = 0;
  for (const p of parts) { out.set(p, offset); offset += p.length; }
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
  for (let i = 31; i >= 0; i--) { out[i] = Number(x & 0xffn); x >>= 8n; }
  return out;
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

function keccakHex(bytes) { return window.viem.keccak256(bytes); }

function computeReceiptHash(receipt) {
  const pre = JSON.parse(JSON.stringify(receipt));
  pre.receipt_hash = null;
  return keccakHex(new TextEncoder().encode(stableStringify(pre)));
}

function computeNode(aHex, bHex) {
  const a = hexToBytes(aHex);
  const b = hexToBytes(bHex);
  const [left, right] = compareBytes(a, b) <= 0 ? [a, b] : [b, a];
  return keccakHex(concatBytes(Uint8Array.from([0x01]), left, right));
}

function computeMerkleRoot(leaves) {
  let level = [...leaves].sort();
  while (level.length > 1) {
    if (level.length % 2 === 1) level.push(level[level.length - 1]);
    const next = [];
    for (let i = 0; i < level.length; i += 2) next.push(computeNode(level[i], level[i+1]));
    level = next;
  }
  return level[0];
}

function computeBatchId(leaves, root) {
  const sorted = [...leaves].sort();
  const preimage = concatBytes(...sorted.map(hexToBytes), hexToBytes(root), uint256Be32(sorted.length));
  return keccakHex(preimage);
}

function verifyReceipt(data) {
  const rh = computeReceiptHash(data);
  const mr = computeMerkleRoot(data.leaves);
  const bid = computeBatchId(data.leaves, mr);

  setStatus('verifyReceiptHash', rh === data.receipt_hash);
  setStatus('verifyMerkleRoot', mr === data.merkle_root);
  setStatus('verifyBatchId', bid === data.batch_id);
}

async function loadDiff(batch) {
  if (!batch.diff_path) return setText('diffChanged', 'unavailable');
  const diff = await loadJSON(batch.diff_path);
  setText('diffChanged', diff.changed ? 'YES' : 'NO');
  setText('diffKeys', (diff.changed_signal_keys || []).join(', '));
  el('diffRaw').textContent = JSON.stringify(diff, null, 2);
}

function renderReceipt(data, cid, url) {
  setText('receiptCid', cid);
  setText('gatewayUrl', url);
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
      await loadDiff(b);
    };
    list.appendChild(btn);
  });
}

async function main() {
  const cfg = await loadJSON('./config.json');
  const gateway = cfg.gateway;

  const index = await loadJSON('./batches.json');
  renderBatchList(index, gateway);

  const latest = index.batches[0];
  const { data, url } = await loadReceipt(latest.receipt_cid, gateway);
  renderReceipt(data, latest.receipt_cid, url);
  await loadDiff(latest);

  setText('status', 'Loaded');
}

main();
