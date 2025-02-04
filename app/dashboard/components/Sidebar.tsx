"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { motion } from "framer-motion"
import { Home, Clock, BarChartIcon as ChartBar, Settings, LogOut, Upload, Calendar } from "lucide-react"
import { Button } from "@/components/ui/button"

interface SidebarProps {
  role: "doctor" | "radiologist"
}

const menuItems = [
  { icon: Home, label: "Home", href: "/dashboard", roles: ["doctor", "radiologist"] },
  { icon: Clock, label: "Recent Uploads", href: "/dashboard/recent-uploads", roles: ["doctor", "radiologist"] },
  { icon: Upload, label: "Upload Images", href: "/dashboard/upload", roles: ["radiologist"] },
  {
    icon: Calendar,
    label: "Book Appointment",
    href: "https://www.practo.com/consult",
    roles: ["doctor", "radiologist"],
  },
  { icon: ChartBar, label: "Analytics", href: "/dashboard/analytics", roles: ["doctor", "radiologist"] },
  { icon: Settings, label: "Settings", href: "/dashboard/settings", roles: ["doctor", "radiologist"] },
]

export default function Sidebar({ role }: SidebarProps) {
  const pathname = usePathname()

  return (
    <div className="w-64 bg-white shadow-md">
      <div className="p-4">
        <h2 className="text-2xl font-bold text-indigo-600">MedAI Assist</h2>
      </div>
      <nav className="mt-8">
        {menuItems
          .filter((item) => item.roles.includes(role))
          .map((item) => (
            <Link
              key={item.href}
              href={item.href}
              target={item.href.startsWith("http") ? "_blank" : undefined}
              rel={item.href.startsWith("http") ? "noopener noreferrer" : undefined}
            >
              <motion.div
                whileHover={{ backgroundColor: "#EEF2FF" }}
                className={`flex items-center px-4 py-2 text-gray-700 ${
                  pathname === item.href ? "bg-indigo-100 text-indigo-600" : ""
                }`}
              >
                <item.icon className="w-5 h-5 mr-3" />
                {item.label}
              </motion.div>
            </Link>
          ))}
      </nav>
      <div className="absolute bottom-0 w-64 p-4">
        <Button variant="ghost" className="w-full justify-start" onClick={() => console.log("Logout clicked")}>
          <LogOut className="w-5 h-5 mr-3" />
          Logout
        </Button>
      </div>
    </div>
  )
}
