import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import * as path from 'path';
import * as fs from 'fs';
import { writeFile } from 'fs/promises';

// Configure CORS headers
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

// Handle CORS preflight requests
export async function OPTIONS() {
  return NextResponse.json({}, { headers: corsHeaders });
}

// Temporary directory for image processing
const UPLOAD_DIR = path.join(process.cwd(), 'temp_uploads');

// Create upload directory if it doesn't exist
if (!fs.existsSync(UPLOAD_DIR)) {
  fs.mkdirSync(UPLOAD_DIR, { recursive: true });
}

export async function POST(req: NextRequest) {
  let filepath = '';
  let processedImagePath = '';

    // Cleanup function that handles one file at a time
    const cleanupFile = async (filePath: string, retries = 3, delay = 100) => {
      for (let i = 0; i < retries; i++) {
        try {
          if (fs.existsSync(filePath)) {
            await fs.promises.unlink(filePath);
            console.log('Cleaned up file:', filePath);
            return true;
          }
          return false;
        } catch (err) {
          console.warn(`Cleanup attempt ${i + 1} failed for ${filePath}:`, err);
          if (i < retries - 1) {
            await new Promise(resolve => setTimeout(resolve, delay));
          }
        }
      }
      return false;
    };

    // Main cleanup function
    const cleanup = async () => {
      console.log('Starting cleanup...');
      
      // Clean up input file first
      if (filepath) {
        await cleanupFile(filepath);
      }

      // Clean up processed file after we're done with it
      if (processedImagePath) {
        await cleanupFile(processedImagePath);
      }

      // Clean up predict directory
      try {
        const runsDir = path.join(process.cwd(), '..', 'Back-end', 'runs', 'detect', 'predict');
        if (fs.existsSync(runsDir)) {
          const files = await fs.promises.readdir(runsDir);
          for (const file of files) {
            const filePath = path.join(runsDir, file);
            const stats = await fs.promises.stat(filePath);
            if (stats.isFile()) {
              await cleanupFile(filePath);
            }
          }
        }
      } catch (err) {
        console.error('Error cleaning predict directory:', err);
      }
    };

  try {
    const formData = await req.formData();
    const file = formData.get('file') as File;

    if (!file) {
      return NextResponse.json(
        { success: false, error: 'No file provided' },
        { status: 400, headers: corsHeaders }
      );
    }

    // Convert File to Buffer
    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);

    // Create unique filename
    const uniqueFilename = `${Date.now()}-${file.name}`;
    filepath = path.join(UPLOAD_DIR, uniqueFilename);

    // Save file
    await writeFile(filepath, new Uint8Array(buffer));

    // Get absolute paths
    const backendDir = path.join(process.cwd(), '..', 'Back-end');
    const scriptPath = path.join(backendDir, 'test_single.py');
    
    if (!fs.existsSync(scriptPath)) {
      throw new Error(`Python script not found at ${scriptPath}`);
    }
    
    const modelPath = path.join(backendDir, 'best.pt');
    if (!fs.existsSync(modelPath)) {
      throw new Error(`Model file not found at ${modelPath}`);
    }

    // Run Python script from backend directory
    console.log('Starting brain tumor detection...');
    console.log(`Processing image from ${filepath}`);
    console.log('Running detection from:', backendDir);

    const pythonProcess = spawn('python', [
      scriptPath,
      filepath
    ], {
      cwd: backendDir // Set working directory to backend folder
    });

    // Collect data from Python script
    let result = '';
    let error = '';

    await new Promise((resolve, reject) => {
      pythonProcess.stdout.on('data', (data) => {
        result += data.toString();
      });

      pythonProcess.stderr.on('data', (data) => {
        error += data.toString();
      });

      pythonProcess.on('close', (code) => {
        if (code === 0) {
          resolve(result);
        } else {
          reject(new Error(`Python process exited with code ${code}. Error: ${error}`));
        }
      });
    });

    // Get the processed image path from Python output
    const processedImageMatch = result.match(/PROCESSED_IMAGE:(.+)$/m);
    if (!processedImageMatch) {
      throw new Error('Could not find processed image path in output');
    }

    processedImagePath = processedImageMatch[1].trim();
    console.log('Found processed image at:', processedImagePath);

    // Retry logic for reading the processed image
    const maxRetries = 3;
    const retryDelay = 500; // ms
    let processedImageBase64 = '';
    let lastError: Error | null = null;

    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        if (!fs.existsSync(processedImagePath)) {
          throw new Error(`Processed image not found at ${processedImagePath}`);
        }

        // Try to read the file
        const stats = fs.statSync(processedImagePath);
        if (stats.size === 0) {
          throw new Error('Processed image file is empty');
        }

        processedImageBase64 = fs.readFileSync(processedImagePath).toString('base64');
        console.log(`Successfully read processed image on attempt ${attempt + 1}`);
        lastError = null;
        break;
      } catch (err) {
        lastError = err as Error;
        console.warn(`Attempt ${attempt + 1} failed:`, err);
        if (attempt < maxRetries - 1) {
          console.log(`Waiting ${retryDelay}ms before retry...`);
          await new Promise(resolve => setTimeout(resolve, retryDelay));
        }
      }
    }

    if (lastError) {
      console.error('All attempts to read processed image failed');
      throw new Error(`Failed to read processed image: ${lastError.message}`);
    }

    // Parse detection results
    const detectionLines = result.split('\n');
    const confidences: number[] = [];
    
    detectionLines.forEach(line => {
      const match = line.match(/DETECTION:(\d+\.\d+)/);
      if (match) {
        confidences.push(parseFloat(match[1]));
      }
    });

    // Generate report using Python script
    const pythonReportProcess = spawn('python', [
      path.join(backendDir, 'report_generator.py')
    ], {
      cwd: backendDir,
      env: {
        ...process.env,
        PATIENT_INFO: JSON.stringify({
          name: formData.get('patientName') || 'Unknown',
          id: formData.get('patientId') || String(Date.now())
        }),
        SCAN_RESULTS: JSON.stringify({
          numDetections: confidences.length,
          confidences
        })
      }
    });

    let reportResult = '';
    let reportError = '';

    await new Promise((resolve, reject) => {
      pythonReportProcess.stdout.on('data', (data) => {
        reportResult += data.toString();
      });

      pythonReportProcess.stderr.on('data', (data) => {
        reportError += data.toString();
      });

      pythonReportProcess.on('close', (code) => {
        if (code === 0) {
          resolve(reportResult);
        } else {
          console.error('Report generation failed:', reportError);
          resolve(null); // Don't fail the whole request if report fails
        }
      });
    });

    // Parse report if available
    let report = null;
    try {
      report = reportResult ? JSON.parse(reportResult) : null;
    } catch (e) {
      console.error('Failed to parse report:', e);
    }

    // Return results and clean up afterwards
        // Structure the report data
        const reportData = {
          success: true,
          numDetections: confidences.length,
          confidences,
          processedImage: processedImageBase64 ? `data:image/jpeg;base64,${processedImageBase64}` : null,
          report: {
            patientInfo: {
              name: formData.get('patientName') || 'Unknown',
              id: formData.get('patientId') || String(Date.now()),
              date: new Date().toISOString()
            },
            scanResults: {
              numDetections: confidences.length,
              confidences
            },
            report: report?.report || 'No report generated',
            generatedAt: new Date().toISOString()
          },
          rawOutput: result
        };
        
        console.log('Sending report data:', reportData);

        const response = NextResponse.json(reportData, {
          headers: corsHeaders
        });

    // Run cleanup after response is sent
    setTimeout(cleanup, 100);
    return response;

  } catch (error) {
    console.error('Error processing image:', error);
    const response = NextResponse.json(
      { 
        success: false, 
        error: error instanceof Error ? error.message : 'Failed to process image'
      },
      { status: 500, headers: corsHeaders }
    );
    // Run cleanup after response is prepared
    setTimeout(cleanup, 100);
    return response;
  }
}
