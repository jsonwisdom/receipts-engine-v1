async function loadJSON(path) {
  const res = await fetch(path);
  return res.json();
}

function el(id) { return document.getElementById(id); }
function setText(id, val) { if (el(id)) el(id).textContent = val ?? ''; }
function setStatus(id, pass) {
  const e = el(id);
  if (!e) return;
  e.textContent = pass ? 'PASS' : 'FAIL';
  e.className = pass ? 'value ok' : 'value bad';
}

async function loadReceipt(cid, gateway) {
  const url = gateway + cid;
  const res = await fetch(url);
  const data = await res.json();
  return { data, url };
}

async function loadDiff(path) {
  try {
    const res = await fetch(path);
    const diff = await res.json();
    setText('diffChanged', diff.changed ? 'YES' : 'NO');
    setText('diffKeys', (diff.changed_signal_keys || []).join(', '));
    el('diffRaw').textContent = JSON.stringify(diff, null, 2);
  } catch {
    setText('diffChanged', 'unavailable');
  }
}

function renderReceipt(data, cid, url) {
  setText('receiptCid', cid);
  setText('gatewayUrl', url);
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
      if (b.diff_path) await loadDiff(b.diff_path);
    };
    list.appendChild(btn);
  });
}

async function main() {
  try {
    const cfg = await loadJSON('./config.json');
    const gateway = cfg.gateway;
    const index = await loadJSON('./batches.json');

    renderBatchList(index, gateway);

    const latest = index.batches.find(b => b.id === index.latest) || index.batches[0];
    const { data, url } = await loadReceipt(latest.receipt_cid, gateway);
    renderReceipt(data, latest.receipt_cid, url);

    if (latest.diff_path) await loadDiff(latest.diff_path);

    setText('sourceType', 'local-index');
    el('status').textContent = 'Loaded';
  } catch (err) {
    el('status').textContent = 'Error';
  }
}

main();
