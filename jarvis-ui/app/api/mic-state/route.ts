// jarvis-ui/app/api/mic-state/route.ts
// Next.js API Route - Proxy for mic state control

import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/mic-state`, {
      cache: 'no-store',
    });
    
    if (!response.ok) {
      return NextResponse.json({ error: 'Backend error' }, { status: response.status });
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error('[API /api/mic-state GET] Error:', error.message);
    return NextResponse.json({ error: 'Failed to connect to backend' }, { status: 503 });
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    
    const response = await fetch(`${BACKEND_URL}/api/mic-state`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return NextResponse.json(errorData, { status: response.status });
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error('[API /api/mic-state POST] Error:', error.message);
    return NextResponse.json({ error: 'Failed to connect to backend' }, { status: 503 });
  }
}
