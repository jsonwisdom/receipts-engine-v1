import { NextResponse } from 'next/server';
import { triangulate } from '@/lib/triangulate';

export const dynamic = 'force-dynamic';

export async function GET() {
  const ensName = process.env.NEXT_PUBLIC_ROOT_ENS || 'jaywisdom.base.eth';
  const expectedSha = process.env.BRIEF_SHA256 || null;

  const result = await triangulate(ensName, expectedSha);

  return new NextResponse(JSON.stringify({
    status: result.verdict,
    exposureWindow: { delta_seconds: result.exposureWindowSeconds },
    ens: result.ens,
    base: result.base,
    ipfs: result.ipfs
  }), {
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'no-store'
    }
  });
}
