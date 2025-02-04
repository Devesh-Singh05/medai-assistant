"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { getCookie } from "cookies-next"
import Sidebar from "./components/Sidebar"
import type { UserRole } from "@/types/auth"
import type React from "react" // Added import for React

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [userRole, setUserRole] = useState<UserRole | null>(null)
  const router = useRouter()

  useEffect(() => {
    const role = getCookie("userRole") as UserRole | undefined
    if (!role) {
      router.push("/")
      return
    }
    setUserRole(role)
  }, [router])

  if (!userRole) {
    return <div>Loading...</div>
  }

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar role={userRole} />
      <main className="flex-1 overflow-y-auto p-8">{children}</main>
    </div>
  )
}