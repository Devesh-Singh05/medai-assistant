"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import Link from "next/link"
import { Calendar, ImageIcon } from "lucide-react"
import { Button } from "@/components/ui/button"

interface Upload {
  id: string
  patientName: string
  uploadTime: string
  imageType: "MRI" | "CT Scan (Lungs)"
  analysis: "Completed" | "In Progress"
}

export default function RecentUploads() {
  const [uploads, setUploads] = useState<Upload[]>([])

  useEffect(() => {
    // In a real application, you would fetch this data from your API
    const mockUploads: Upload[] = [
      { id: "1", patientName: "John Doe", uploadTime: "2023-05-10 14:30", imageType: "MRI", analysis: "Completed" },
      {
        id: "2",
        patientName: "Jane Smith",
        uploadTime: "2023-05-10 15:45",
        imageType: "CT Scan (Lungs)",
        analysis: "In Progress",
      },
      { id: "3", patientName: "Bob Johnson", uploadTime: "2023-05-10 16:20", imageType: "MRI", analysis: "Completed" },
      {
        id: "4",
        patientName: "Alice Brown",
        uploadTime: "2023-05-10 17:10",
        imageType: "CT Scan (Lungs)",
        analysis: "In Progress",
      },
      {
        id: "5",
        patientName: "Charlie Davis",
        uploadTime: "2023-05-10 18:00",
        imageType: "MRI",
        analysis: "Completed",
      },
    ]
    setUploads(mockUploads)
  }, [])

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="container mx-auto"
    >
      <h1 className="text-3xl font-bold mb-6">Recent Uploads</h1>
      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Patient Name
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Upload Time
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Image Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Analysis
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
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
                  <div className="flex items-center">
                    <div className="ml-4">
                      <div className="text-sm font-medium text-gray-900">{upload.patientName}</div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <Calendar className="h-5 w-5 text-gray-400 mr-2" />
                    <div className="text-sm text-gray-900">{upload.uploadTime}</div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <ImageIcon className="h-5 w-5 text-gray-400 mr-2" />
                    <div className="text-sm text-gray-900">{upload.imageType}</div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span
                    className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      upload.analysis === "Completed" ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"
                    }`}
                  >
                    {upload.analysis}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <Button asChild>
                    <Link href={`/dashboard/patient/${upload.id}`}>View Details</Link>
                  </Button>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  )
}

