import { createPublicClient, http } from 'viem';
import { base } from 'viem/chains';

export type BaseTxStatus = {
  exists: boolean;
  confirmations: number | null;
  isFinal: boolean;
  blockTime: string | null;
};

function getBaseRpcUrl(): string {
  return process.env.RPC_URL_BASE || 'https://mainnet.base.org';
}

function getClient() {
  return createPublicClient({
    chain: base,
    transport: http(getBaseRpcUrl(), { timeout: 10_000 })
  });
}

export async function checkBaseTransaction(txHash: string | null): Promise<BaseTxStatus> {
  if (!txHash) {
    return { exists: false, confirmations: null, isFinal: false, blockTime: null };
  }

  const client = getClient();

  try {
    const tx = await client.getTransaction({ hash: txHash as `0x${string}` });
    if (!tx || !tx.blockNumber) {
      return { exists: false, confirmations: null, isFinal: false, blockTime: null };
    }

    const currentBlock = await client.getBlockNumber();
    const block = await client.getBlock({ blockNumber: tx.blockNumber });
    const confirmations = Number(currentBlock - tx.blockNumber);

    return {
      exists: true,
      confirmations,
      isFinal: confirmations >= 12,
      blockTime: new Date(Number(block.timestamp) * 1000).toISOString()
    };
  } catch {
    return { exists: false, confirmations: null, isFinal: false, blockTime: null };
  }
}

export async function getBaseTxBlockTime(txHash: string | null): Promise<string | null> {
  const status = await checkBaseTransaction(txHash);
  return status.blockTime;
}
