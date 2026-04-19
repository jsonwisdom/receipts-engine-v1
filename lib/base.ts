import { createPublicClient, http } from 'viem';
import { base } from 'viem/chains';

export type BaseTxStatus = {
  exists: boolean;
  confirmations: number | null;
  isFinal: boolean;
};

function getBaseRpcUrl(): string {
  return process.env.RPC_URL_BASE || 'https://mainnet.base.org';
}

export async function checkBaseTransaction(txHash: string | null): Promise<BaseTxStatus> {
  if (!txHash) {
    return { exists: false, confirmations: null, isFinal: false };
  }

  const client = createPublicClient({
    chain: base,
    transport: http(getBaseRpcUrl(), { timeout: 10_000 })
  });

  try {
    const tx = await client.getTransaction({ hash: txHash as `0x${string}` });
    if (!tx || !tx.blockNumber) {
      return { exists: false, confirmations: null, isFinal: false };
    }

    const currentBlock = await client.getBlockNumber();
    const confirmations = Number(currentBlock - tx.blockNumber);

    return {
      exists: true,
      confirmations,
      isFinal: confirmations >= 12
    };
  } catch {
    return { exists: false, confirmations: null, isFinal: false };
  }
}
