// jarvis-ui/app/api/settings/route.ts
// Next.js API Route - Proxy for settings

import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/settings`, {
      cache: 'no-store',
    });
    
    if (!response.ok) {
      return NextResponse.json({ error: 'Backend error' }, { status: response.status });
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error('[API /api/settings] Error:', error.message);
    return NextResponse.json({ error: 'Failed to connect to backend' }, { status: 503 });
  }
}
