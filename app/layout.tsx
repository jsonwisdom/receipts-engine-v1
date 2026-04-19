export const metadata = {
  title: 'Receipts Engine V1',
  description: 'Looking Glass Verification Surface'
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, background: '#ffffff', color: '#000000', fontFamily: 'monospace' }}>
        {children}
      </body>
    </html>
  );
}
