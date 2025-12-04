// jarvis-ui/app/api/chatlogs/route.ts
// Next.js API Route - Proxy for chat history

import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const limit = searchParams.get('limit') || '100';
    
    const response = await fetch(`${BACKEND_URL}/api/chatlogs?limit=${limit}`, {
      cache: 'no-store',
    });
    
    if (!response.ok) {
      return NextResponse.json({ chatlogs: [], error: 'Backend error' }, { status: response.status });
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error('[API /api/chatlogs] Error:', error.message);
    return NextResponse.json({ chatlogs: [], error: 'Failed to connect to backend' }, { status: 503 });
  }
}
