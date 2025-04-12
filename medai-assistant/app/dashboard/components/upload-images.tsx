'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Upload, X, Loader2, AlertCircle, RefreshCw } from 'lucide-react'
import Image from 'next/image'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { NavLinks } from "@/components/nav-links"

interface UploadedImage {
  file: File;
  preview: string;
  processedImage?: string;
  detections?: number;
  confidences?: number[];
  isProcessing?: boolean;
  processingStatus?: 'uploading' | 'processing' | 'loading-result';
  error?: string;
  retryCount?: number;
  report?: {
    patientInfo: {
      name: string;
      id: string;
      date: string;
    };
    scanResults: {
      numDetections: number;
      confidences: number[];
    };
    report: string;
    generatedAt: string;
  };
}

export default function UploadImage() {
  const [images, setImages] = useState<UploadedImage[]>([])
  const [patientName, setPatientName] = useState('')
  const [patientId, setPatientId] = useState('')
  const [imageType, setImageType] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [selectedImage, setSelectedImage] = useState<string | null>(null)

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    const newImages = files.map(file => ({
      file,
      preview: URL.createObjectURL(file)
    }))
    setImages(prev => [...prev, ...newImages])
  }

  const removeImage = (index: number) => {
    setImages(prev => prev.filter((_, i) => i !== index))
  }

    const processImage = async (image: UploadedImage, index: number) => {
      const maxRetries = 3;
      const retryDelay = 1000;

      const updateImageStatus = (
        status: 'uploading' | 'processing' | 'loading-result' | undefined,
        attempt?: number,
        error?: string
      ) => {
        setImages(prev => prev.map((img, i) => 
          i === index ? {
            ...img,
            isProcessing: status !== undefined,
            processingStatus: status,
            retryCount: attempt,
            error: error
          } : img
        ));
      };

      try {
        updateImageStatus('uploading');
        const formData = new FormData();
        formData.append('file', image.file);

        for (let attempt = 0; attempt < maxRetries; attempt++) {
          try {
            updateImageStatus(
              attempt === 0 ? 'processing' : 'loading-result',
              attempt
            );

            // Add patient information to form data
            formData.append('patientName', patientName);
            formData.append('patientId', patientId);
            formData.append('imageType', imageType);

            const response = await fetch('/api/detect', {
              method: 'POST',
              body: formData,
            });

            if (!response.ok) {
              const errorData = await response.json();
              throw new Error(errorData.error || 'Server error');
            }

            const data = await response.json();
            console.log('API Response:', data);
            
            if (!data.success) {
              throw new Error(data.error || 'Processing failed');
            }

            console.log('Report data:', data.report);
            console.log('Image data:', data.processedImage?.substring(0, 100) + '...');

            // Store the report in localStorage for recent uploads
            try {
              if (data.report) {
                const newUpload = {
                  patientName,
                  patientId,
                  imageType: imageType || 'brain-mri',
                  timestamp: new Date().toISOString(),
                  processedImage: data.processedImage,
                  report: data.report,
                  detections: data.numDetections,
                  confidences: data.confidences
                };

                console.log('Saving upload to localStorage:', newUpload);

                const recentUploads = JSON.parse(localStorage.getItem('recentUploads') || '[]');
                recentUploads.unshift(newUpload);
                
                // Keep only last 10 uploads
                const trimmedUploads = recentUploads.slice(0, 10);
                localStorage.setItem('recentUploads', JSON.stringify(trimmedUploads));
                
                console.log('Successfully saved to localStorage');
              } else {
                console.warn('No report data received from API');
              }
            } catch (storageError) {
              console.error('Error saving to localStorage:', storageError);
            }

            // Success - update image with report
            setImages(prev => prev.map((img, i) => 
              i === index ? {
                ...img,
                isProcessing: false,
                processingStatus: undefined,
                processedImage: data.processedImage,
                detections: data.numDetections,
                confidences: data.confidences,
                report: data.report,
                retryCount: undefined,
                error: undefined
              } : img
            ));
            return;

          } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
            
            if (attempt === maxRetries - 1) {
              throw new Error(`Failed after ${maxRetries} attempts: ${errorMessage}`);
            }

            console.warn(`Attempt ${attempt + 1} failed:`, errorMessage);
            updateImageStatus(
              'loading-result',
              attempt,
              `Retrying... (${attempt + 1}/${maxRetries})`
            );
            await new Promise(resolve => setTimeout(resolve, retryDelay));
          }
        }

      // If we get here, all retries failed
      throw new Error('Failed to process image after multiple attempts');

    } catch (error) {
      setImages(prev => prev.map((img, i) => 
        i === index ? {
          ...img,
          isProcessing: false,
          processingStatus: undefined,
          error: error instanceof Error ? error.message : 'Failed to process image',
          retryCount: undefined
        } : img
      ));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (images.length === 0) return;
    
    setIsProcessing(true);
    try {
      // Process each image
      for (let i = 0; i < images.length; i++) {
        await processImage(images[i], i);
      }
    } finally {
      setIsProcessing(false);
    }
  }

  return (
    <>
      <NavLinks />
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="container mx-auto p-4"
      >
        <h1 className="text-2xl font-bold mb-4">Upload New Images</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Label htmlFor="patientName">Patient Name</Label>
          <Input
            id="patientName"
            value={patientName}
            onChange={(e) => setPatientName(e.target.value)}
            required
          />
        </div>
        <div>
          <Label htmlFor="patientId">Patient ID</Label>
          <Input
            id="patientId"
            value={patientId}
            onChange={(e) => setPatientId(e.target.value)}
            required
          />
        </div>
        <div>
          <Label htmlFor="imageType">Scan Type</Label>
          <Select value={imageType} onValueChange={setImageType}>
            <SelectTrigger>
              <SelectValue placeholder="Select scan type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="brain-mri">Brain MRI</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div>
          <Label htmlFor="images">Upload Images</Label>
          <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
            <div className="space-y-1 text-center">
              <Upload className="mx-auto h-12 w-12 text-gray-400" />
              <div className="flex text-sm text-gray-600">
                <label
                  htmlFor="images"
                  className="relative cursor-pointer bg-white rounded-md font-medium text-indigo-600 hover:text-indigo-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500"
                >
                  <span>Upload files</span>
                  <Input
                    id="images"
                    type="file"
                    multiple
                    accept="image/*"
                    className="sr-only"
                    onChange={handleImageUpload}
                  />
                </label>
                <p className="pl-1">or drag and drop</p>
              </div>
              <p className="text-xs text-gray-500">PNG, JPG, GIF up to 10MB</p>
            </div>
          </div>
        </div>
        {images.length > 0 && (
          <div className="mt-4">
            <h3 className="text-lg font-medium mb-2">Uploaded Images:</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {images.map((image, index) => (
              <div key={index} className="relative bg-gray-100 rounded-lg p-4">
                <div 
                  className="relative cursor-pointer"
                  onClick={() => setSelectedImage(image.processedImage || image.preview)}
                >
                  <Image
                    src={image.processedImage || image.preview}
                    alt={`Uploaded image ${index + 1}`}
                    width={200}
                    height={200}
                    className="rounded-lg object-cover w-full h-48"
                    unoptimized={true}
                  />
                  <div className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-10 transition-opacity" />
                  <button
                    type="button"
                    onClick={() => removeImage(index)}
                    className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1"
                    aria-label={`Remove image ${index + 1}`}
                  >
                    <X size={16} />
                  </button>
                </div>
                
                {image.isProcessing && (
                  <div className="mt-2">
                    <div className="flex items-center text-blue-500">
                      <Loader2 className="animate-spin mr-2" size={16} />
                      {image.processingStatus === 'uploading' ? 'Uploading...' :
                       image.processingStatus === 'processing' ? 'Processing scan (this may take longer on CPU)...' :
                       image.processingStatus === 'loading-result' ? 'Loading results...' :
                       'Processing...'}
                    </div>
                    <div className="text-xs text-blue-400 mt-1">
                      {image.retryCount !== undefined && image.retryCount > 0 ? (
                        <div className="flex items-center">
                          <RefreshCw size={12} className="mr-1" />
                          Retry {image.retryCount}/3
                        </div>
                      ) : image.processingStatus === 'processing' ? (
                        <div>Please wait, this operation may take several seconds</div>
                      ) : null}
                    </div>
                  </div>
                )}
                
                {image.error && (
                  <div className="mt-2">
                    <div className="flex items-center text-red-500 text-sm font-semibold">
                      <AlertCircle size={16} className="mr-1" />
                      Error:
                    </div>
                    <div className="text-red-500 text-sm mt-1">
                      {image.error.includes('Model not found') ? (
                        <>
                          Model file not found. Please ensure the YOLO model file (best.pt) 
                          is present in the Back-end directory.
                        </>
                      ) : image.error.includes('Failed to read processed image') ? (
                        <>
                          Failed to read processed image. The system might be busy, 
                          please try again.
                        </>
                      ) : (
                        image.error
                      )}
                    </div>
                  </div>
                )}
                
                {image.detections !== undefined && !image.error && (
                  <div className="mt-2">
                    {image.detections === 0 ? (
                      <div className="text-green-600">No tumors detected</div>
                    ) : (
                      <div>
                        <div className="text-amber-600 font-semibold mb-1">
                          {`${image.detections} tumor${image.detections > 1 ? 's' : ''} detected`}
                        </div>
                        <div className="text-sm space-y-1">
                          {image.confidences?.map((conf, idx) => (
                            <div key={idx} className="text-gray-600">
                              {`Tumor ${idx + 1}: ${(conf * 100).toFixed(1)}% confidence`}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
              ))}
            </div>
          </div>
        )}
        <Button 
          type="submit" 
          className="w-full" 
          disabled={images.length === 0 || isProcessing}
          variant={images.length === 0 ? "outline" : "default"}
        >
          {isProcessing ? (
            <>
              <Loader2 className="animate-spin mr-2" size={16} />
              Processing Images...
            </>
          ) : (
            'Analyze Images'
          )}
        </Button>
      </form>

      {/* Full size image preview */}
      {selectedImage && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedImage(null)}
        >
          <div 
            className="relative bg-white rounded-lg overflow-hidden max-w-4xl w-full mx-auto"
            onClick={e => e.stopPropagation()}
          >
            <div className="relative h-[80vh]">
              <Image
                src={selectedImage}
                alt="Full size preview"
                fill
                className="object-contain"
                unoptimized={true}
              />
            </div>
            <button
              className="absolute top-2 right-2 bg-white rounded-full p-2 shadow-lg"
              onClick={() => setSelectedImage(null)}
              aria-label="Close preview"
            >
              <X aria-hidden="true" />
            </button>
          </div>
        </div>
      )}
      </motion.div>
    </>
  )
}
