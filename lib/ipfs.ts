export type IpfsSnapshot = {
  cid: string | null;
  gatewayHits: string[];
  byteMatch: boolean;
  sha256: string | null;
};

const DEFAULT_GATEWAYS = [
  'https://ipfs.io/ipfs',
  'https://cloudflare-ipfs.com/ipfs'
] as const;

function getGateways(): string[] {
  const raw = process.env.IPFS_GATEWAYS?.trim();
  if (!raw) return [...DEFAULT_GATEWAYS];
  return raw.split(',').map((value) => value.trim()).filter(Boolean);
}

async function sha256Hex(bytes: Uint8Array): Promise<string> {
  const digest = await crypto.subtle.digest('SHA-256', bytes);
  const hashBytes = new Uint8Array(digest);
  return `0x${Array.from(hashBytes).map((b) => b.toString(16).padStart(2, '0')).join('')}`;
}

function arraysEqual(a: Uint8Array, b: Uint8Array): boolean {
  if (a.length !== b.length) return false;
  for (let i = 0; i < a.length; i += 1) {
    if (a[i] !== b[i]) return false;
  }
  return true;
}

export async function fetchIpfsIntegrity(cid: string | null): Promise<IpfsSnapshot> {
  if (!cid) {
    return { cid: null, gatewayHits: [], byteMatch: false, sha256: null };
  }

  const gateways = getGateways();
  const successful: Array<{ gateway: string; bytes: Uint8Array }> = [];

  await Promise.all(
    gateways.map(async (gateway) => {
      try {
        const response = await fetch(`${gateway}/${cid}`, {
          method: 'GET',
          cache: 'no-store'
        });
        if (!response.ok) return;
        const buffer = await response.arrayBuffer();
        successful.push({ gateway, bytes: new Uint8Array(buffer) });
      } catch {
        return;
      }
    })
  );

  if (successful.length < 2) {
    return {
      cid,
      gatewayHits: successful.map((item) => item.gateway),
      byteMatch: false,
      sha256: null
    };
  }

  const [first, ...rest] = successful;
  const byteMatch = rest.every((item) => arraysEqual(first.bytes, item.bytes));
  if (!byteMatch) {
    return {
      cid,
      gatewayHits: successful.map((item) => item.gateway),
      byteMatch: false,
      sha256: null
    };
  }

  const sha256 = await sha256Hex(first.bytes);
  return {
    cid,
    gatewayHits: successful.map((item) => item.gateway),
    byteMatch: true,
    sha256
  };
}
