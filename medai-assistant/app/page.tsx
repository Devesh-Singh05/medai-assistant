"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { Stethoscope, Radio, Mail, Lock } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { setCookie } from "cookies-next"
import type { UserRole } from "@/types/auth"
import Image from "next/image"

export default function Login() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [selectedRole, setSelectedRole] = useState<UserRole | null>(null)
  const [error, setError] = useState("")
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedRole) {
      setError("Please select a role")
      return
    }

    if (email && password) {
      setCookie("userRole", selectedRole, {
        maxAge: 60 * 60 * 24,
        path: "/",
      })

      router.push("/dashboard")
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#2d3a8c]">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-5xl flex overflow-hidden rounded-2xl shadow-2xl"
      >
        {/* Left Panel - Image and Branding */}
        <div className="hidden md:flex md:w-1/2 bg-gradient-to-br from-[#4263eb] to-[#3b82f6] p-8 relative">
          <div className="absolute top-6 left-6">
            <h1 className="text-white text-2xl font-bold">MED-AI</h1>
          </div>

          <div className="flex flex-col items-center justify-center h-full relative">
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-64 h-64 rounded-full bg-blue-400/30 absolute"></div>
              <div className="w-40 h-40 rounded-full bg-pink-400/20 absolute -right-10"></div>
              <div className="w-32 h-32 rounded-full bg-yellow-400/20 absolute -bottom-10 -left-5"></div>
            </div>

            {/* Elevated Logo Section */}
            <motion.div
              initial={{ y: 50, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{
                type: "spring",
                stiffness: 300,
                damping: 20,
                delay: 0.2,
              }}
              className="z-10 mb-4 relative"
            >
              {/* Shadow effect for elevation */}
              <div className="absolute -inset-4 bg-blue-400/20 rounded-full blur-xl"></div>

              {/* Light blue circle background */}
              <div className="absolute -inset-8 bg-blue-300/20 rounded-full"></div>

              {/* Logo container */}
              <div className="relative">
                <Image
                  src="E:\RBL 2.0\medai-assistant\Images\Med-ai.png"
                  alt="MED-AI Healthcare Logo"
                  width={320}
                  height={320}
                  className="object-contain relative z-10"
                />
              </div>
            </motion.div>

            <motion.div
              initial={{ y: 30, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="mt-12 text-white text-center z-10"
            >
              <h2 className="text-3xl font-bold mb-2 text-shadow">AI-Powered Medical Imaging</h2>
              <p className="opacity-80 text-lg">Advanced diagnostics for healthcare professionals</p>
            </motion.div>
          </div>

          <div className="absolute bottom-6 left-6 text-white/60 text-xs">
            © 2025 MedAI Assist. All rights reserved.
          </div>
        </div>

        {/* Right Panel - Login Form */}
        <div className="w-full md:w-1/2 bg-white p-8 flex flex-col">
          <div className="flex justify-center mb-4">
            <h1 className="text-[#4263eb] text-2xl font-bold">MED-AI</h1>
          </div>
          <div className="mb-8 text-center">
            <h2 className="text-2xl font-bold text-gray-800">Sign In</h2>
            <p className="text-gray-500 mt-2">Access your MedAI Assist account</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6 flex-1">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-gray-700 font-medium">
                Email
              </Label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                <Input
                  id="email"
                  type="email"
                  placeholder="doctor@hospital.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="pl-10 border-gray-300 focus:border-[#4263eb] focus:ring focus:ring-[#4263eb]/20"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-gray-700 font-medium">
                Password
              </Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="pl-10 border-gray-300 focus:border-[#4263eb] focus:ring focus:ring-[#4263eb]/20"
                />
              </div>
            </div>

            <div className="space-y-3">
              <Label className="text-gray-700 font-medium">Select Role</Label>
              <div className="grid grid-cols-2 gap-4">
                <button
                  type="button"
                  onClick={() => setSelectedRole("doctor")}
                  className={`flex items-center justify-center p-3 rounded-lg border-2 transition-all ${
                    selectedRole === "doctor"
                      ? "border-[#4263eb] bg-[#4263eb]/5 text-[#4263eb]"
                      : "border-gray-200 hover:border-[#4263eb]/50 hover:bg-[#4263eb]/5"
                  }`}
                >
                  <Stethoscope className="mr-2" size={20} />
                  Doctor
                </button>
                <button
                  type="button"
                  onClick={() => setSelectedRole("radiologist")}
                  className={`flex items-center justify-center p-3 rounded-lg border-2 transition-all ${
                    selectedRole === "radiologist"
                      ? "border-[#4263eb] bg-[#4263eb]/5 text-[#4263eb]"
                      : "border-gray-200 hover:border-[#4263eb]/50 hover:bg-[#4263eb]/5"
                  }`}
                >
                  <Radio className="mr-2" size={20} />
                  Radiologist
                </button>
              </div>
            </div>

            {error && <div className="text-red-500 text-sm">{error}</div>}

            <Button
              type="submit"
              className="w-full bg-[#4263eb] hover:bg-[#3b5bdb] text-white py-3 rounded-lg transition-colors"
            >
              Sign In
            </Button>

            <p className="text-center text-gray-500 text-sm mt-4">
              <button type="button" className="text-[#4263eb] hover:underline">
                Forgot your password?
              </button>
            </p>
          </form>

          <div className="mt-8">
            <div className="flex items-center justify-center space-x-4">
              <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-500 hover:bg-gray-200 transition-colors">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"></path>
                </svg>
              </div>
              <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-500 hover:bg-gray-200 transition-colors">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path>
                  <rect x="2" y="9" width="4" height="12"></rect>
                  <circle cx="4" cy="4" r="2"></circle>
                </svg>
              </div>
              <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-500 hover:bg-gray-200 transition-colors">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M22 4s-.7 2.1-2 3.4c1.6 10-9.4 17.3-18 11.6 2.2.1 4.4-.6 6-2C3 15.5.5 9.6 3 5c2.2 2.6 5.6 4.1 9 4-.9-4.2 4-6.6 7-3.8 1.1 0 3-1.2 3-1.2z"></path>
                </svg>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
