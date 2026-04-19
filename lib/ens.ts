import { createPublicClient, http, namehash, type Hex } from 'viem';
import { mainnet } from 'viem/chains';

const ENS_REGISTRY_ADDRESS = '0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e' as const;
const ENS_REGISTRY_ABI = [
  {
    type: 'function',
    stateMutability: 'view',
    name: 'resolver',
    inputs: [{ name: 'node', type: 'bytes32' }],
    outputs: [{ name: '', type: 'address' }]
  }
] as const;
const ENS_RESOLVER_ABI = [
  {
    type: 'function',
    stateMutability: 'view',
    name: 'text',
    inputs: [
      { name: 'node', type: 'bytes32' },
      { name: 'key', type: 'string' }
    ],
    outputs: [{ name: '', type: 'string' }]
  }
] as const;

export type EnsSnapshot = {
  ensName: string;
  resolverAddress: string | null;
  records: {
    sha256: string | null;
    cid: string | null;
    txHash: string | null;
  };
  missingKeys: string[];
};

function getMainnetRpcUrl(): string {
  return process.env.RPC_URL_MAINNET || 'https://ethereum-rpc.publicnode.com';
}

export async function resolveEnsRecords(ensName: string): Promise<EnsSnapshot> {
  const client = createPublicClient({
    chain: mainnet,
    transport: http(getMainnetRpcUrl(), { timeout: 10_000 })
  });

  const node = namehash(ensName);
  const resolverAddress = await client.readContract({
    address: ENS_REGISTRY_ADDRESS,
    abi: ENS_REGISTRY_ABI,
    functionName: 'resolver',
    args: [node]
  }) as string;

  if (!resolverAddress || resolverAddress === '0x0000000000000000000000000000000000000000') {
    return {
      ensName,
      resolverAddress: null,
      records: { sha256: null, cid: null, txHash: null },
      missingKeys: ['lookingglass.brief.sha256', 'lookingglass.brief.cid', 'lookingglass.brief.tx']
    };
  }

  const readText = async (key: string): Promise<string | null> => {
    try {
      const value = await client.readContract({
        address: resolverAddress as Hex,
        abi: ENS_RESOLVER_ABI,
        functionName: 'text',
        args: [node, key]
      }) as string;
      const trimmed = value.trim();
      return trimmed.length > 0 ? trimmed : null;
    } catch {
      return null;
    }
  };

  const sha256 = await readText('lookingglass.brief.sha256');
  const cid = await readText('lookingglass.brief.cid');
  const txHash = await readText('lookingglass.brief.tx');

  const missingKeys: string[] = [];
  if (!sha256) missingKeys.push('lookingglass.brief.sha256');
  if (!cid) missingKeys.push('lookingglass.brief.cid');
  if (!txHash) missingKeys.push('lookingglass.brief.tx');

  return {
    ensName,
    resolverAddress,
    records: { sha256, cid, txHash },
    missingKeys
  };
}
