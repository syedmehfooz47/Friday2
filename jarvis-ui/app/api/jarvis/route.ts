// jarvis-ui/app/api/jarvis/route.ts

import { NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

// This function assumes Frontend and Backend folders are in the PARENT directory of the Next.js project.
const getFilePath = (fileName: string): string => {
  // process.cwd() is the root of the Next.js project (e.g., /path/to/Jarvis/jarvis-ui)
  // We need to go one level up to find the Backend/Frontend folders.
  const projectParentDir = path.join(process.cwd(), '..');

  let filePath: string;

  if (fileName === 'ChatLog.json') {
    filePath = path.join(projectParentDir, 'Backend', 'Database', fileName);
  } else if (fileName.endsWith('.data')) {
    filePath = path.join(projectParentDir, 'Frontend', 'Files', fileName);
  } else {
    // For security, explicitly block requests for other files.
    console.warn(`[API SECURITY] Blocked attempt to access invalid file: ${fileName}`);
    throw new Error(`Invalid or unsupported file: ${fileName}`);
  }

  // Return a normalized, absolute path
  return path.normalize(filePath);
};

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const fileName = searchParams.get('file');

  if (!fileName) {
    return NextResponse.json({ error: 'File name is required' }, { status: 400 });
  }

  let filePath: string | undefined; // Initialize here
  try {
    filePath = getFilePath(fileName);
    // Log the path we are trying to read for easier debugging
    console.log(`[API GET] Attempting to read: ${filePath}`);

    const content = await fs.readFile(filePath, 'utf-8');
    return NextResponse.json({ content });
  } catch (error: any) {
    if (error.code === 'ENOENT') {
      // This is not an error, just means the backend hasn't created the file yet.
      return NextResponse.json({ content: '' });
    }
    console.error(`[API GET CRITICAL ERROR] Failed to read ${fileName} from path ${filePath}:`, error);
    return NextResponse.json({ error: `Server error reading file.` }, { status: 500 });
  }
}

export async function POST(req: Request) {
  let filePath: string | undefined; // Initialize here
  try {
    const body = await req.json();
    const { file, content } = body;

    if (!file || content === undefined) {
      return NextResponse.json({ error: 'File and content are required' }, { status: 400 });
    }

    filePath = getFilePath(file);
    // Log the path we are trying to write to for easier debugging
    console.log(`[API POST] Attempting to write to: ${filePath}`);
    
    const dir = path.dirname(filePath);
    await fs.mkdir(dir, { recursive: true });

    await fs.writeFile(filePath, content, 'utf-8');
    return NextResponse.json({ success: true, message: `Wrote to ${file}` });
  } catch (error: any) {
    console.error(`[API POST CRITICAL ERROR] Failed to write to ${filePath}:`, error);
    return NextResponse.json({ error: `Server error writing file.` }, { status: 500 });
  }
}