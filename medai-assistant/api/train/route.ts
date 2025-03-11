import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';
import { writeFile } from 'fs/promises';

export async function GET(req: NextRequest) {
    try {
        // Get training status
        const pythonProcess = spawn('python', [
            path.join(process.cwd(), 'fl-backend/server/cli.py'),
            '--mode', 'status'
        ]);

        let result = '';
        
        pythonProcess.stdout.on('data', (data) => {
            result += data.toString();
        });

        await new Promise((resolve, reject) => {
            pythonProcess.on('close', (code) => {
                if (code === 0) resolve(null);
                else reject(new Error(`Process exited with code ${code}`));
            });
        });

        return new NextResponse(
            JSON.stringify({
                success: true, 
                status: JSON.parse(result)
            }), 
            { status: 200 }
        );

    } catch (error) {
        console.error('Error getting training status:', error);
        return new NextResponse(
            JSON.stringify({
                success: false,
                error: 'Failed to get training status'
            }), 
            { status: 500 }
        );
    }
}

export async function POST(req: NextRequest) {
    try {
        const formData = await req.formData();
        const action = formData.get('action') as string;
        const clientId = formData.get('clientId') as string;
        const modelUpdate = formData.get('modelUpdate') as File;

        // Create temp directory if it doesn't exist
        const tempDir = path.join(process.cwd(), 'temp');
        await createTempDir(tempDir);

        let args = [
            path.join(process.cwd(), 'fl-backend/server/cli.py'),
            '--mode', action,
            '--client_id', clientId
        ];

        // If there's a model update, save it and pass the path
        if (modelUpdate) {
            const updatePath = path.join(tempDir, `update_${clientId}_${Date.now()}.pt`);
            const buffer = Buffer.from(await modelUpdate.arrayBuffer());
            await writeFile(updatePath, buffer);
            args.push('--update_path', updatePath);
        }

        // Run the Python process
        const pythonProcess = spawn('python', args);

        let result = '';
        let error = '';

        pythonProcess.stdout.on('data', (data) => {
            result += data.toString();
        });

        pythonProcess.stderr.on('data', (data) => {
            error += data.toString();
        });

        await new Promise((resolve, reject) => {
            pythonProcess.on('close', (code) => {
                if (code === 0) resolve(null);
                else reject(new Error(`Process exited with code ${code}`));
            });
        });

        if (error) {
            throw new Error(error);
        }

        return new NextResponse(
            JSON.stringify({
                success: true,
                result: JSON.parse(result)
            }), 
            { status: 200 }
        );

    } catch (error) {
        console.error('Training error:', error);
        return new NextResponse(
            JSON.stringify({
                success: false,
                error: 'Training operation failed'
            }), 
            { status: 500 }
        );
    }
}

async function createTempDir(dirPath: string) {
    const { mkdir } = require('fs/promises');
    try {
        await mkdir(dirPath, { recursive: true });
    } catch (error) {
        if ((error as any).code !== 'EEXIST') {
            throw error;
        }
    }
}

// API endpoint supports the following actions:
// GET /api/train - Get current training status
// POST /api/train 
//   - action: 'start_round' - Start new training round
//   - action: 'submit_update' - Submit model update from client
//   - action: 'get_model' - Get current global model