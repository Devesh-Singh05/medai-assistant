'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import { motion } from 'framer-motion'
import { Calendar, Clock, ImageIcon, User } from 'lucide-react'

interface PatientUpload {
  id: string
  patientName: string
  uploadTime: string
  imageType: string
  status: 'Pending' | 'Analyzed'
  patientAge: number
  patientGender: 'Male' | 'Female' | 'Other'
  diagnosis: string | null
}

export default function PatientDetails() {
  const params = useParams()
  const [upload, setUpload] = useState<PatientUpload | null>(null)

  useEffect(() => {
    // In a real application, you would fetch this data from your API based on the ID
    const mockUpload: PatientUpload = {
      id: params.id as string,
      patientName: 'John Doe',
      uploadTime: '2023-05-10 14:30',
      imageType: 'X-Ray',
      status: 'Analyzed',
      patientAge: 45,
      patientGender: 'Male',
      diagnosis: 'Mild pneumonia detected in the lower right lung.'
    }
    setUpload(mockUpload)
  }, [params.id])

  if (!upload) {
    return <div>Loading...</div>
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="container mx-auto"
    >
      <h1 className="text-3xl font-bold mb-6">Patient Details</h1>
      <div className="bg-white shadow-md rounded-lg overflow-hidden p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h2 className="text-xl font-semibold mb-4">Patient Information</h2>
            <div className="space-y-2">
              <div className="flex items-center">
                <User className="h-5 w-5 text-gray-400 mr-2" />
                <span className="text-gray-700">Name: {upload.patientName}</span>
              </div>
              <div className="flex items-center">
                <Calendar className="h-5 w-5 text-gray-400 mr-2" />
                <span className="text-gray-700">Age: {upload.patientAge}</span>
              </div>
              <div className="flex items-center">
                <User className="h-5 w-5 text-gray-400 mr-2" />
                <span className="text-gray-700">Gender: {upload.patientGender}</span>
              </div>
            </div>
          </div>
          <div>
            <h2 className="text-xl font-semibold mb-4">Upload Information</h2>
            <div className="space-y-2">
              <div className="flex items-center">
                <Clock className="h-5 w-5 text-gray-400 mr-2" />
                <span className="text-gray-700">Upload Time: {upload.uploadTime}</span>
              </div>
              <div className="flex items-center">
                <ImageIcon className="h-5 w-5 text-gray-400 mr-2" />
                <span className="text-gray-700">Image Type: {upload.imageType}</span>
              </div>
              <div className="flex items-center">
                <div className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                  upload.status === 'Analyzed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {upload.status}
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="mt-6">
          <h2 className="text-xl font-semibold mb-4">Diagnosis</h2>
          <p className="text-gray-700">{upload.diagnosis || 'Pending analysis'}</p>
        </div>
      </div>
    </motion.div>
  )
}

