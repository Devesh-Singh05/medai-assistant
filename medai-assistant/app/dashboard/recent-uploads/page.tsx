'use client';

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import Image from "next/image";
import { Calendar, ImageIcon, FileText, Eye } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { NavLinks } from "@/components/nav-links";
import { Modal, ModalHeader, ModalTitle, ModalContent } from "@/components/ui/modal";

interface Report {
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
}

interface RecentUpload {
  patientName: string;
  patientId: string;
  imageType: string;
  timestamp: string;
  processedImage: string;
  report: Report;
  detections: number;
  confidences: number[];
}

export default function RecentUploads() {
  const [uploads, setUploads] = useState<RecentUpload[]>([]);
  const [selectedReport, setSelectedReport] = useState<RecentUpload | null>(null);

  useEffect(() => {
    try {
      // Load recent uploads from localStorage
      const storedUploads = localStorage.getItem('recentUploads');
      console.log('Raw stored uploads:', storedUploads);
      
      if (storedUploads) {
        const parsedUploads = JSON.parse(storedUploads);
        console.log('Parsed uploads:', parsedUploads);
        
        // Verify the data structure
        const validUploads = parsedUploads.filter((upload: any) => {
          const isValid = upload.patientName && 
                         upload.processedImage && 
                         upload.report;
          if (!isValid) {
            console.warn('Invalid upload data:', upload);
          }
          return isValid;
        });

        setUploads(validUploads);
        console.log('Valid uploads loaded:', validUploads.length);
      } else {
        console.log('No uploads found in localStorage');
      }
    } catch (error) {
      console.error('Error loading uploads:', error);
    }
  }, []);

  function formatDate(timestamp: string) {
    return new Date(timestamp).toLocaleString();
  }

  function downloadReport(report: RecentUpload) {
    const reportText = `
Medical Report
=============

Patient Information:
------------------
Name: ${report.patientName}
ID: ${report.patientId}
Date: ${formatDate(report.timestamp)}

Scan Details:
------------
Type: ${report.imageType}
Detections: ${report.report.scanResults.numDetections}
Confidence Levels: ${report.report.scanResults.confidences.map((confidence: number) => 
  (confidence * 100).toFixed(1) + '%'
).join(', ')}

Report:
-------
${report.report.report}
    `.trim();

    const blob = new Blob([reportText], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `report_${report.patientId}_${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }

  return (
    <>
      <NavLinks />
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="container mx-auto p-6"
      >
      <h1 className="text-3xl font-bold mb-6">Recent Uploads</h1>
      
      {uploads.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          No recent uploads found
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {uploads.map((upload, index) => (
            <Card key={index} className="overflow-hidden">
              <div className="relative h-48">
                <Image
                  src={upload.processedImage}
                  alt={`Scan for ${upload.patientName}`}
                  fill
                  className="object-cover"
                  unoptimized={true}
                />
              </div>
              <div className="p-4">
                <h3 className="text-lg font-semibold">{upload.patientName}</h3>
                <div className="mt-2 space-y-2 text-sm text-gray-500">
                  <div className="flex items-center">
                    <Calendar className="w-4 h-4 mr-2" />
                    {formatDate(upload.timestamp)}
                  </div>
                  <div className="flex items-center">
                    <ImageIcon className="w-4 h-4 mr-2" />
                    {upload.imageType}
                  </div>
                  <div className="flex items-center">
                    <FileText className="w-4 h-4 mr-2" />
                    ID: {upload.patientId}
                  </div>
                </div>
                
                <Button 
                  className="w-full mt-4"
                  onClick={() => setSelectedReport(upload)}
                >
                  <Eye className="w-4 h-4 mr-2" />
                  View Report
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Debug info */}
      <div className="fixed bottom-4 right-4 bg-gray-800 text-white p-2 rounded text-xs">
        Loaded uploads: {uploads.length}
      </div>

      <Modal 
        isOpen={!!selectedReport} 
        onClose={() => setSelectedReport(null)}
        className="max-w-4xl"
      >
        {selectedReport && (
          <>
            <ModalHeader>
              <ModalTitle>Medical Report - {selectedReport.patientName}</ModalTitle>
            </ModalHeader>
            
            <ModalContent>
              <div className="space-y-4">
                <div className="flex justify-end mb-4">
                  <Button
                    onClick={() => downloadReport(selectedReport)}
                    className="mb-4"
                  >
                    <FileText className="w-4 h-4 mr-2" />
                    Download Report
                  </Button>
                </div>

                <div className="space-y-6">
                  <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
                    <div>
                      <h4 className="font-semibold mb-2">Patient Information</h4>
                      <p>Name: {selectedReport.patientName}</p>
                      <p>ID: {selectedReport.patientId}</p>
                      <p>Date: {formatDate(selectedReport.timestamp)}</p>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-2">Scan Details</h4>
                      <p>Type: {selectedReport.imageType}</p>
                      <p>Detections: {selectedReport.report.scanResults.numDetections}</p>
                      <p>Confidence Levels:</p>
                      <ul className="list-disc list-inside">
                        {selectedReport.report.scanResults.confidences.map((confidence: number, index: number) => (
                          <li key={index}>{(confidence * 100).toFixed(1)}%</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold mb-2">Report</h4>
                    <div className="whitespace-pre-wrap text-gray-700 p-4 bg-gray-50 rounded-lg">
                      {selectedReport.report.report}
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold mb-2">Processed Image</h4>
                    <div className="relative h-64 rounded-lg overflow-hidden">
                      <Image
                        src={selectedReport.processedImage}
                        alt="Processed scan"
                        fill
                        className="object-contain"
                        unoptimized={true}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </ModalContent>
          </>
        )}
      </Modal>
      </motion.div>
    </>
  );
}
