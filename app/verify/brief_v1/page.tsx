import { StatusBadge } from '@/components/StatusBadge';
import { AnchorTable } from '@/components/AnchorTable';
import { JsonViewer } from '@/components/JsonViewer';

export const dynamic = 'force-dynamic';

async function getData() {
  const res = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL || ''}/api/verify/brief_v1`, { cache: 'no-store' });
  return res.json();
}

export default async function Page() {
  const data = await getData();

  return (
    <div style={{ padding: 20 }}>
      <h1 style={{ fontSize: 18 }}>Looking Glass Artifact: Presidential Brief v1</h1>

      <div style={{ marginTop: 20 }}>
        <StatusBadge status={data.status} />
      </div>

      <div style={{ marginTop: 20, fontSize: 32 }}>
        Exposure Window: {data.exposureWindow?.delta_seconds ?? '—'}s
      </div>

      <AnchorTable
        ensSha={data.ens?.records?.sha256}
        cid={data.ens?.records?.cid}
        tx={data.ens?.records?.txHash}
        contentSha={data.ipfs?.sha256}
        confirmations={data.base?.confirmations}
      />

      <JsonViewer data={data} />
    </div>
  );
}
