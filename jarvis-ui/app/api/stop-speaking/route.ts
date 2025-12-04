// jarvis-ui/app/api/stop-speaking/route.ts
// Next.js API Route - Proxy for stop speaking command

import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function POST() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/stop-speaking`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return NextResponse.json(errorData, { status: response.status });
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error('[API /api/stop-speaking] Error:', error.message);
    return NextResponse.json({ success: false, error: 'Failed to connect to backend' }, { status: 503 });
  }
}
