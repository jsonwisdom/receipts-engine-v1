type Props = {
  data: unknown;
};

export function JsonViewer({ data }: Props) {
  return (
    <pre
      style={{
        marginTop: 20,
        padding: 10,
        border: '2px solid #000',
        overflowX: 'auto',
        fontSize: 12
      }}
    >
      {JSON.stringify(data, null, 2)}
    </pre>
  );
}
