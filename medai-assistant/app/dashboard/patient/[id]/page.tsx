"use client"

import { useState, useEffect } from "react"
import { useParams } from "next/navigation"
import Image from "next/image"
import { motion } from "framer-motion"
import { Calendar, Clock, ImageIcon, User, ZoomIn, ZoomOut, ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

interface PatientReport {
  id: string
  patientName: string
  patientAge: number
  patientGender: "Male" | "Female" | "Other"
  uploadTime: string
  imageType: "MRI" | "CT Scan (Lungs)"
  analysis: "Completed" | "In Progress"
  diagnosis: string
  recommendations: string
  scanImage: string
}

const patientReports: PatientReport[] = [
  {
    id: "1",
    patientName: "John Doe",
    patientAge: 45,
    patientGender: "Male",
    uploadTime: "2023-05-10 14:30",
    imageType: "MRI",
    analysis: "Completed",
    diagnosis: "Early-stage brain tumor detected in the frontal lobe. No signs of metastasis.",
    recommendations:
      "Immediate consultation with a neurosurgeon. Follow-up MRI in 2 weeks. Consider biopsy for further analysis.",
    scanImage: "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/MRI-1-Ddg9I6Yyk3tahFy9FRDCQTtolCgO55.jpeg",
  },
  {
    id: "2",
    patientName: "Jane Smith",
    patientAge: 32,
    patientGender: "Female",
    uploadTime: "2023-05-10 15:45",
    imageType: "CT Scan (Lungs)",
    analysis: "In Progress",
    diagnosis: "Pending final analysis. Preliminary results show possible early-stage lung nodules.",
    recommendations: "Await final analysis. Follow up with pulmonologist. Consider PET scan for further evaluation.",
    scanImage:
      "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/CT%20scan-1-ngkmX0x8k3W2YwsHMntHukmgi4dRTf.jpeg",
  },
  {
    id: "3",
    patientName: "Bob Johnson",
    patientAge: 58,
    patientGender: "Male",
    uploadTime: "2023-05-10 16:20",
    imageType: "MRI",
    analysis: "Completed",
    diagnosis: "Multiple sclerosis (MS) lesions detected in the brain. White matter changes observed.",
    recommendations:
      "Urgent consultation with neurologist. Consider starting immunomodulatory therapy. Schedule follow-up MRI in 3 months.",
    scanImage: "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/MRI-3-tu1SkmKNfamPISZCQZOR1Fz3KwV47E.jpeg",
  },
  {
    id: "4",
    patientName: "Alice Brown",
    patientAge: 27,
    patientGender: "Female",
    uploadTime: "2023-05-10 17:10",
    imageType: "CT Scan (Lungs)",
    analysis: "In Progress",
    diagnosis:
      "Pending final analysis. Initial review suggests possible pneumonia in both lungs with characteristic ground-glass opacities.",
    recommendations:
      "Await final analysis. Start broad-spectrum antibiotics. Monitor symptoms closely. Follow up in 48 hours.",
    scanImage:
      "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/CT%20scan-2-5ifoiJK6bbzXoMxs0QzyHGe2fxPx5X.jpeg",
  },
  {
    id: "5",
    patientName: "Charlie Davis",
    patientAge: 50,
    patientGender: "Male",
    uploadTime: "2023-05-10 18:00",
    imageType: "MRI",
    analysis: "Completed",
    diagnosis:
      "Multiple sclerosis (MS) lesions detected in the brain. Disease appears to be in early stages with characteristic white matter lesions.",
    recommendations:
      "Consult with neurologist specializing in MS. Consider starting disease-modifying therapy. Schedule follow-up MRI in 3 months.",
    scanImage: "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/MRI-4-5m1KQEQtYBsApdYxxJK6ISb1nhY19e.jpeg",
  },
]

export default function PatientDetail() {
  const params = useParams()
  const [report, setReport] = useState<PatientReport | null>(null)
  const [imageZoomed, setImageZoomed] = useState(false)
  const [imagePosition, setImagePosition] = useState(0)

  useEffect(() => {
    const foundReport = patientReports.find((r) => r.id === params.id)
    setReport(foundReport || null)
  }, [params.id])

  const handlePan = (direction: "left" | "right") => {
    setImagePosition((prev) => {
      const newPosition = direction === "left" ? prev + 50 : prev - 50
      return Math.max(Math.min(newPosition, 0), -200) // Adjust these values based on your image size
    })
  }

  if (!report) {
    return <div>Loading...</div>
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="container mx-auto py-8"
    >
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="text-2xl font-bold">Patient Report</CardTitle>
          <CardDescription>Detailed analysis and recommendations</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h2 className="text-xl font-semibold mb-4">Patient Information</h2>
              <div className="space-y-2">
                <div className="flex items-center">
                  <User className="h-5 w-5 text-gray-400 mr-2" />
                  <span className="text-gray-700">Name: {report.patientName}</span>
                </div>
                <div className="flex items-center">
                  <Calendar className="h-5 w-5 text-gray-400 mr-2" />
                  <span className="text-gray-700">Age: {report.patientAge}</span>
                </div>
                <div className="flex items-center">
                  <User className="h-5 w-5 text-gray-400 mr-2" />
                  <span className="text-gray-700">Gender: {report.patientGender}</span>
                </div>
              </div>
            </div>
            <div>
              <h2 className="text-xl font-semibold mb-4">Scan Information</h2>
              <div className="space-y-2">
                <div className="flex items-center">
                  <Clock className="h-5 w-5 text-gray-400 mr-2" />
                  <span className="text-gray-700">Upload Time: {report.uploadTime}</span>
                </div>
                <div className="flex items-center">
                  <ImageIcon className="h-5 w-5 text-gray-400 mr-2" />
                  <span className="text-gray-700">Image Type: {report.imageType}</span>
                </div>
                <div className="flex items-center">
                  <div
                    className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      report.analysis === "Completed" ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"
                    }`}
                  >
                    {report.analysis}
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="mt-6">
            <h2 className="text-xl font-semibold mb-4">Diagnosis</h2>
            <p className="text-gray-700">{report.diagnosis}</p>
          </div>
          <div className="mt-6">
            <h2 className="text-xl font-semibold mb-4">Recommendations</h2>
            <p className="text-gray-700">{report.recommendations}</p>
          </div>
          <div className="mt-6">
            <h2 className="text-xl font-semibold mb-4">Scan Image</h2>
            <div className="relative">
              <motion.div
                animate={{
                  scale: imageZoomed ? 2 : 1,
                  x: imageZoomed ? imagePosition : 0,
                }}
                transition={{ duration: 0.3 }}
                className="relative w-full h-64 md:h-96 overflow-hidden"
              >
                <Image
                  src={report.scanImage || "/placeholder.svg"}
                  alt={`${report.imageType} scan`}
                  layout="fill"
                  objectFit="contain"
                  className="rounded-lg"
                />
              </motion.div>
              <div className="absolute top-2 right-2 space-x-2">
                <Button
                  onClick={() => {
                    setImageZoomed(!imageZoomed)
                    setImagePosition(0)
                  }}
                >
                  {imageZoomed ? <ZoomOut className="h-4 w-4" /> : <ZoomIn className="h-4 w-4" />}
                </Button>
                {imageZoomed && (
                  <>
                    <Button onClick={() => handlePan("left")} disabled={imagePosition >= 0}>
                      <ChevronLeft className="h-4 w-4" />
                    </Button>
                    <Button onClick={() => handlePan("right")} disabled={imagePosition <= -200}>
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  </>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}

