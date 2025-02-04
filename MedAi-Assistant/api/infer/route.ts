import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';
import { writeFile } from 'fs/promises';
import { mkdir } from 'fs/promises';

export async function POST(req: NextRequest) {
    try {
        const formData = await req.formData();
        const image = formData.get('image') as File;
        const imageType = formData.get('type') as string;
        const patientName = formData.get('patientName') as string;
        const patientId = formData.get('patientId') as string;

        if (!image || !imageType) {
            return new NextResponse(
                JSON.stringify({ success: false, error: 'Missing required fields' }),
                { status: 400 }
            );
        }

        // Create uploads directory if it doesn't exist
        const uploadsDir = path.join(process.cwd(), 'uploads');
        await mkdir(uploadsDir, { recursive: true });

        // Save the uploaded image
        const buffer = Buffer.from(await image.arrayBuffer());
        const fileName = `${patientId}_${Date.now()}_${image.name}`;
        const imagePath = path.join(uploadsDir, fileName);
        await writeFile(imagePath, buffer);

        // Call Python inference script
        const pythonProcess = spawn('python', [
            path.join(process.cwd(), 'fl-backend/server/inference.py'),
            '--image_path', imagePath,
            '--image_type', imageType,
            '--patient_id', patientId,
            '--patient_name', patientName
        ]);

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

        const analysis = JSON.parse(result);

        return new NextResponse(
            JSON.stringify({
                success: true,
                result: analysis,
                imagePath: fileName
            }),
            { status: 200 }
        );

    } catch (error) {
        console.error('Inference error:', error);
        return new NextResponse(
            JSON.stringify({
                success: false,
                error: 'Inference failed'
            }),
            { status: 500 }
        );
    }
}