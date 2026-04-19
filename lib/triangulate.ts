import { resolveEnsRecords } from './ens';
import { checkBaseTransaction } from './base';
import { fetchIpfsIntegrity } from './ipfs';

export type Verdict = 'PASS' | 'FAIL' | 'PENDING';

export type TriangulationResult = {
  verdict: Verdict;
  ens: Awaited<ReturnType<typeof resolveEnsRecords>>;
  base: Awaited<ReturnType<typeof checkBaseTransaction>>;
  ipfs: Awaited<ReturnType<typeof fetchIpfsIntegrity>>;
  exposureWindowSeconds: number | null;
};

function allPresent(ens: any): boolean {
  return Boolean(ens.records.sha256 && ens.records.cid && ens.records.txHash);
}

function computeExposure(blockTime: string | null): number | null {
  if (!blockTime) return null;
  const anchor = new Date(blockTime).getTime();
  const now = Date.now();
  if (!Number.isFinite(anchor)) return null;
  return Math.max(0, Math.floor((now - anchor) / 1000));
}

export async function triangulate(ensName: string, expectedSha: string | null): Promise<TriangulationResult> {
  const ens = await resolveEnsRecords(ensName);

  if (!allPresent(ens)) {
    return {
      verdict: 'PENDING',
      ens,
      base: { exists: false, confirmations: null, isFinal: false, blockTime: null },
      ipfs: { cid: ens.records.cid, gatewayHits: [], byteMatch: false, sha256: null },
      exposureWindowSeconds: null
    };
  }

  const [base, ipfs] = await Promise.all([
    checkBaseTransaction(ens.records.txHash),
    fetchIpfsIntegrity(ens.records.cid)
  ]);

  if (!base.exists || !base.isFinal) {
    return {
      verdict: 'PENDING',
      ens,
      base,
      ipfs,
      exposureWindowSeconds: computeExposure(base.blockTime)
    };
  }

  if (!ipfs.byteMatch || !ipfs.sha256) {
    return {
      verdict: 'PENDING',
      ens,
      base,
      ipfs,
      exposureWindowSeconds: computeExposure(base.blockTime)
    };
  }

  const ensSha = ens.records.sha256;
  const contentSha = ipfs.sha256;
  const expected = expectedSha;

  const allEqual = Boolean(
    ensSha && contentSha && expected &&
    ensSha === contentSha &&
    ensSha === expected
  );

  if (!allEqual) {
    return {
      verdict: 'FAIL',
      ens,
      base,
      ipfs,
      exposureWindowSeconds: computeExposure(base.blockTime)
    };
  }

  return {
    verdict: 'PASS',
    ens,
    base,
    ipfs,
    exposureWindowSeconds: computeExposure(base.blockTime)
  };
}
