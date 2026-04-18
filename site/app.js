async function loadJSON(path) {
  const res = await fetch(path);
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

function renderReceipt(data, cid, url) {
  setText('receiptCid', cid);
  setText('gatewayUrl', url);
  setText('version', data.version);
  setText('leafCount', data.leaf_count);
  setText('batchId', data.batch_id);
  setText('merkleRoot', data.merkle_root);
  setText('receiptHash', data.receipt_hash);
  el('raw').textContent = JSON.stringify(data, null, 2);
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
  }
}

main();
