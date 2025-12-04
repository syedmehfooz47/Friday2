// jarvis-ui/app/api/files/route.ts
// Next.js API Route - Proxy to FastAPI backend for generated files
// This is MORE RELIABLE than direct client->FastAPI calls

import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET() {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s timeout

    const response = await fetch(`${BACKEND_URL}/api/generated-files`, {
      signal: controller.signal,
      headers: {
        'Accept': 'application/json',
      },
      // Next.js 14+ cache control
      cache: 'no-store',
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`[API /api/files] Backend error: ${response.status} - ${errorText}`);
      return NextResponse.json(
        { error: `Backend error: ${response.status}`, files: [] },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error: any) {
    if (error.name === 'AbortError') {
      console.error('[API /api/files] Request timeout');
      return NextResponse.json(
        { error: 'Backend request timeout', files: [] },
        { status: 504 }
      );
    }

    console.error('[API /api/files] Failed to fetch from backend:', error.message);
    return NextResponse.json(
      { error: 'Failed to connect to backend', files: [] },
      { status: 503 }
    );
  }
}
