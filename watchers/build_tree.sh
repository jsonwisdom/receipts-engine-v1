#!/usr/bin/env bash
set -euo pipefail
LEAF_DIR="${1:-_artifacts/leaves}"
OUT_DIR="_artifacts/current"
STATE="_truth/state.json"
mkdir -p "$OUT_DIR"
[ -d "$LEAF_DIR" ] || { echo "missing leaf dir"; exit 1; }

mapfile -t LEAVES < <(find "$LEAF_DIR" -type f -name '*.json' | sort)
[ ${#LEAVES[@]} -gt 0 ] || { echo "no leaves found"; exit 1; }

ROOT=$(LEAF_DIR="$LEAF_DIR" python3 - <<'PY'
import json,hashlib,glob,os,sys
paths=sorted(glob.glob(os.path.join(os.environ['LEAF_DIR'],'*.json')))
vals=[]
for p in paths:
    with open(p) as f:
        obj=json.load(f)
    vals.append(obj['leaf_hash'])
if not vals:
    print('no leaves', file=sys.stderr)
    sys.exit(1)

def parent(a,b):
    return hashlib.sha256(("\x01"+a+b).encode()).hexdigest()
layer=vals[:]
while len(layer)>1:
    nxt=[]
    for i in range(0,len(layer),2):
        left=layer[i]
        right=layer[i+1] if i+1 < len(layer) else layer[i]
        nxt.append(parent(left,right))
    layer=nxt
print(layer[0])
PY
)

TREE_JSON=$(LEAF_DIR="$LEAF_DIR" ROOT="$ROOT" python3 - <<'PY'
import json,glob,os
paths=sorted(glob.glob(os.path.join(os.environ['LEAF_DIR'],'*.json')))
leaves=[]
for p in paths:
    with open(p) as f:
        leaves.append(json.load(f))
print(json.dumps({"leaf_count":len(leaves),"merkle_root":os.environ['ROOT'],"leaves":leaves},sort_keys=True,separators=(',',':')))
PY
)
printf '%s\n' "$TREE_JSON" > "$OUT_DIR/tree.json"

TMP=$(mktemp)
ROOT="$ROOT" python3 - <<'PY' > "$TMP"
import json,os
s=json.load(open('_truth/state.json'))
s['last_merkle_root']=os.environ['ROOT']
s['status']='tree_built'
print(json.dumps(s,sort_keys=True,separators=(',',':')))
PY
mv "$TMP" "$STATE"

echo "tree:ok"
echo "root:$ROOT"
