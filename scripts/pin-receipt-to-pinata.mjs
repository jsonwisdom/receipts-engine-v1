import fs from 'node:fs';

const jwt = process.env.PINATA_JWT;
if (!jwt) {
  console.error('Missing PINATA_JWT');
  process.exit(2);
}

const filePath = process.argv[2];
if (!filePath) {
  console.error('usage: node scripts/pin-receipt-to-pinata.mjs path/to/receipt.json');
  process.exit(2);
}

const form = new FormData();
form.append('file', new Blob([fs.readFileSync(filePath)]), 'receipt.json');
form.append('pinataMetadata', JSON.stringify({ name: 'batch-receipt-0001' }));

const res = await fetch('https://api.pinata.cloud/pinning/pinFileToIPFS', {
  method: 'POST',
  headers: { Authorization: `Bearer ${jwt}` },
  body: form
});

if (!res.ok) {
  console.error(await res.text());
  process.exit(1);
}

const out = await res.json();
console.log(JSON.stringify({ cid: out.IpfsHash, size: out.PinSize, timestamp: out.Timestamp }, null, 2));
