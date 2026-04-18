// existing code above unchanged

async function loadDiff() {
  try {
    const res = await fetch('_truth/apple/april26_diff.json');
    const diff = await res.json();
    setText('diffChanged', diff.changed ? 'YES' : 'NO');
    setText('diffKeys', (diff.changed_signal_keys || []).join(', '));
    el('diffRaw').textContent = JSON.stringify(diff, null, 2);
  } catch {
    setText('diffChanged', 'unavailable');
  }
}

// modify main()
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

    await loadDiff();

    el('status').textContent = 'Loaded';
    el('status').className = 'value ok';
  } catch (err) {
    el('status').textContent = 'Error';
    el('status').className = 'value bad';
    el('verification').textContent = err.message;
  }
}

main();
