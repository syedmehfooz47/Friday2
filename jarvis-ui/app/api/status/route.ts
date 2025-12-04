// jarvis-ui/app/api/status/route.ts
// Next.js API Route - Backend health check endpoint
// Use this to check if backend is alive before establishing WebSocket

import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET() {
  const startTime = Date.now();
  
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000); // 3s timeout

    const response = await fetch(`${BACKEND_URL}/api/status`, {
      signal: controller.signal,
      cache: 'no-store',
    });

    clearTimeout(timeoutId);
    const latency = Date.now() - startTime;

    if (!response.ok) {
      return NextResponse.json({
        status: 'degraded',
        backend: false,
        latency,
        message: `Backend returned ${response.status}`,
      });
    }

    const data = await response.json();
    
    return NextResponse.json({
      status: 'healthy',
      backend: true,
      latency,
      backendStatus: data,
    });

  } catch (error: any) {
    const latency = Date.now() - startTime;
    
    if (error.name === 'AbortError') {
      return NextResponse.json({
        status: 'timeout',
        backend: false,
        latency,
        message: 'Backend request timeout (>3s)',
      });
    }

    return NextResponse.json({
      status: 'offline',
      backend: false,
      latency,
      message: error.message || 'Cannot connect to backend',
    });
  }
}
