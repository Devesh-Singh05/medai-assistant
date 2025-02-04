"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { Stethoscope, Radio } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import type { UserRole } from "@/types/auth"
import { setCookie } from "cookies-next"

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
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-r from-[#36D1DC] to-[#5B86E5] p-4">
      <motion.div
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        <Card className="bg-white/10 backdrop-blur-sm border-white/20">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl font-bold text-center text-white">MedAI Assist Login</CardTitle>
            <CardDescription className="text-center text-white/80">
              Choose your role and login to continue
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4 mb-6">
              <Button
                variant="outline"
                className={`w-full h-24 flex flex-col items-center justify-center gap-2 border-2 transition-all duration-200
                  ${
                    selectedRole === "doctor"
                      ? "bg-white/30 text-white border-white"
                      : "bg-transparent text-white border-white/50 hover:bg-white/20 hover:border-white"
                  }`}
                onClick={() => setSelectedRole("doctor")}
              >
                <Stethoscope className="h-8 w-8" />
                <span className="font-semibold">Doctor</span>
              </Button>
              <Button
                variant="outline"
                className={`w-full h-24 flex flex-col items-center justify-center gap-2 border-2 transition-all duration-200
                  ${
                    selectedRole === "radiologist"
                      ? "bg-white/30 text-white border-white"
                      : "bg-transparent text-white border-white/50 hover:bg-white/20 hover:border-white"
                  }`}
                onClick={() => setSelectedRole("radiologist")}
              >
                <Radio className="h-8 w-8" />
                <span className="font-semibold">Radiologist</span>
              </Button>
            </div>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email" className="text-white">
                  Email
                </Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="doctor@hospital.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="bg-white/10 border-white/20 text-white placeholder:text-white/50"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password" className="text-white">
                  Password
                </Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="bg-white/10 border-white/20 text-white"
                />
              </div>
              {error && <div className="text-red-300 text-sm">{error}</div>}
              <Button
                type="submit"
                className="w-full bg-white/20 text-white border-white hover:bg-white/30 transition-colors"
              >
                Login
              </Button>
            </form>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}