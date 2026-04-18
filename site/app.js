async function loadConfig() {
  const res = await fetch('./config.json');
  return res.json();
}

function el(id) { return document.getElementById(id); }

function setText(id, val) {
  const e = el(id);
  if (e) e.textContent = val ?? '';
}

async function main() {
  try {
    const cfg = await loadConfig();
    const cid = cfg.receipt_cid;
    const gateway = cfg.gateway || 'https://ipfs.io/ipfs/';
    const url = gateway + cid;

    setText('receiptCid', cid);
    setText('gatewayUrl', url);

    const res = await fetch(url);
    if (!res.ok) throw new Error('fetch failed');
    const data = await res.json();

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
  } catch (err) {
    el('status').textContent = 'Error loading receipt';
    el('status').className = 'value bad';
    el('verification').textContent = err.message;
  }
}

main();
