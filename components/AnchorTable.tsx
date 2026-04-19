type Props = {
  ensSha: string | null;
  cid: string | null;
  tx: string | null;
  contentSha: string | null;
  confirmations: number | null;
};

export function AnchorTable({ ensSha, cid, tx, contentSha, confirmations }: Props) {
  const cell = (v: any) => (v ? v : '—');

  return (
    <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 20 }}>
      <tbody>
        {[
          ['ENS SHA256', cell(ensSha)],
          ['IPFS CID', cell(cid)],
          ['BASE TX', cell(tx)],
          ['CONTENT SHA256', cell(contentSha)],
          ['CONFIRMATIONS', cell(confirmations)]
        ].map(([k, v]) => (
          <tr key={k}>
            <td style={{ border: '2px solid #000', padding: 8 }}>{k}</td>
            <td style={{ border: '2px solid #000', padding: 8 }}>{v}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
