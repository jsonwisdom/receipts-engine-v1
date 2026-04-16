import json, sys

def chunk64(s, i): return s[i:i+64]

def read_dyn(data, head_offset_words):
    off = int(data[head_offset_words*64:(head_offset_words+1)*64], 16) * 2
    ln = int(data[off:off+64], 16) * 2
    raw = data[off+64:off+64+ln]
    return bytes.fromhex(raw).decode("utf-8")

with open("raw_logs.txt") as f:
    blocks = f.read().strip().split("- address: ")

out = open("court.jsonl", "w")
for b in blocks:
    b = b.strip()
    if not b: continue
    lines = b.splitlines()
    row = {}
    for line in lines:
        if ":" in line and not line.strip().startswith("topics"):
            k,v = line.split(":",1)
            row[k.strip()] = v.strip()
    data = row.get("data","")
    if data.startswith("0x"): data = data[2:]
    if len(data) < 256: continue
    rec = {
        "contract": row.get("address"),
        "blockNumber": int(row.get("blockNumber","0")),
        "transactionHash": row.get("transactionHash"),
        "logIndex": int(row.get("logIndex","0")),
        "commitmentHash": "0x" + data[128:192],
        "agentId": read_dyn(data, 0),
        "tradeId": read_dyn(data, 1),
        "uri": read_dyn(data, 3)
    }
    out.write(json.dumps(rec) + "\n")
out.close()
print("wrote court.jsonl")
