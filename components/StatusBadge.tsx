type Props = {
  status: 'PASS' | 'FAIL' | 'PENDING';
};

export function StatusBadge({ status }: Props) {
  const styles: Record<Props['status'], React.CSSProperties> = {
    PASS: { background: '#ffffff', color: '#000000', border: '2px solid #000000' },
    FAIL: { background: '#ff0000', color: '#ffffff', border: '2px solid #000000' },
    PENDING: { background: '#d4d4d4', color: '#000000', border: '2px solid #000000' }
  };

  return (
    <div
      style={{
        ...styles[status],
        display: 'inline-block',
        padding: '10px 16px',
        fontSize: '28px',
        fontWeight: 700,
        letterSpacing: '0.08em'
      }}
    >
      {status}
    </div>
  );
}
