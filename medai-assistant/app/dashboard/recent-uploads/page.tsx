'use client'

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import Link from "next/link"
import Image from "next/image"
import { Calendar, ImageIcon, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { format } from 'date-fns'
import type { StoredScan } from '@/types/scan'
import { getScanHistory, deleteScan } from '@/types/scan'

export default function RecentUploads() {
  const [uploads, setUploads] = useState<StoredScan[]>([])
  const [selectedImage, setSelectedImage] = useState<string | null>(null)

  useEffect(() => {
    try {
      const history = getScanHistory();
      setUploads(history);
    } catch (error) {
      console.error('Error loading scan history:', error);
      // Show error message to user
      setUploads([]);
    }
  }, [])

  // Add safeguard for SSR/missing localStorage
  if (typeof window === 'undefined') {
    return null;
  }

  const handleDelete = (id: string) => {
    if (deleteScan(id)) {
      setUploads(prev => prev.filter(upload => upload.id !== id));
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="container mx-auto p-4"
    >
      <h1 className="text-3xl font-bold mb-6">Recent Uploads</h1>
      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Image
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Patient Details
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Upload Time
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Results
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {uploads.map((upload) => (
              <motion.tr
                key={upload.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <td className="px-6 py-4 whitespace-nowrap">
                  <div 
                    className="w-20 h-20 relative cursor-pointer rounded-lg overflow-hidden"
                    onClick={() => setSelectedImage(upload.processedImage || upload.originalImage)}
                  >
                    <Image
                      src={upload.processedImage || upload.originalImage}
                      alt={`Scan for ${upload.patientName}`}
                      fill
                      className="object-cover"
                      unoptimized={true}
                    />
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex flex-col">
                    <div className="text-sm font-medium text-gray-900">{upload.patientName}</div>
                    <div className="text-sm text-gray-500">ID: {upload.patientId}</div>
                    <div className="text-sm text-gray-500">{upload.imageType}</div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <Calendar className="h-5 w-5 text-gray-400 mr-2" />
                    <div className="text-sm text-gray-900">{format(new Date(upload.uploadTime), 'PPpp')}</div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {upload.status === 'completed' ? (
                    <div className="space-y-1">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        upload.numDetections > 0 ? 'bg-amber-100 text-amber-800' : 'bg-green-100 text-green-800'
                      }`}>
                        {upload.numDetections > 0 
                          ? `${upload.numDetections} tumor${upload.numDetections > 1 ? 's' : ''} detected` 
                          : 'No tumors detected'}
                      </span>
                      {upload.confidences?.map((conf, idx) => (
                        <div key={idx} className="text-xs text-gray-500">
                          {`Tumor ${idx + 1}: ${(conf * 100).toFixed(1)}% confidence`}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                      Failed
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                  <Button 
                    variant="outline"
                    size="sm"
                    onClick={() => setSelectedImage(upload.processedImage || upload.originalImage)}
                  >
                    View
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="text-red-600 hover:text-red-800"
                    onClick={() => handleDelete(upload.id)}
                  >
                    Delete
                  </Button>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>

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
  )
}
