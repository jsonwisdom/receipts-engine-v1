import fs from 'node:fs';

const prevPath = process.argv[2] || '_truth/apple/april26_prev_leaf.json';
const currPath = process.argv[3] || '_truth/apple/april26_leaf.json';
const outPath = process.argv[4] || '_truth/apple/april26_diff.json';

function readJson(path) {
  if (!fs.existsSync(path)) return null;
  return JSON.parse(fs.readFileSync(path, 'utf8'));
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

const prev = readJson(prevPath);
const curr = readJson(currPath);
if (!curr) {
  console.error('missing current leaf');
  process.exit(2);
}

const prevSignals = prev?.signals || {};
const currSignals = curr.signals || {};
const allSignalKeys = Array.from(new Set([...Object.keys(prevSignals), ...Object.keys(currSignals)])).sort();
const signalChanges = allSignalKeys.map((k) => ({
  key: k,
  previous: prevSignals[k] ?? null,
  current: currSignals[k] ?? null,
  changed: (prevSignals[k] ?? null) !== (currSignals[k] ?? null)
}));

const diff = {
  source: 'apple_newsroom_april26_diff',
  compared_at_utc: curr.captured_at_utc,
  has_previous: !!prev,
  changed: !prev || stableStringify(prev) !== stableStringify(curr),
  previous_text_sha256: prev?.text_sha256 ?? null,
  current_text_sha256: curr.text_sha256,
  previous_text_bytes: prev?.text_bytes ?? null,
  current_text_bytes: curr.text_bytes,
  text_sha256_changed: (prev?.text_sha256 ?? null) !== curr.text_sha256,
  text_bytes_changed: (prev?.text_bytes ?? null) !== curr.text_bytes,
  signal_changes: signalChanges,
  changed_signal_keys: signalChanges.filter(x => x.changed).map(x => x.key)
};

fs.mkdirSync(require('node:path').dirname(outPath), { recursive: true });
fs.writeFileSync(outPath, JSON.stringify(diff, null, 2) + '\n');
console.log(JSON.stringify({ status: 'ok', outPath, changed: diff.changed, changed_signal_keys: diff.changed_signal_keys }, null, 2));
