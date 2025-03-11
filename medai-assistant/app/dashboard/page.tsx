"use client"

import { motion } from "framer-motion"

interface DashboardCardProps {
  title: string
  value: string
  description: string
}

export default function Dashboard() {
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5 }}>
      <h1 className="text-3xl font-bold mb-6">Welcome, Dr. Smith</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <DashboardCard title="Recent Uploads" value="23" description="Images uploaded this week" />
        <DashboardCard title="Analyses Completed" value="18" description="AI analyses performed this week" />
        <DashboardCard title="Accuracy Rate" value="97%" description="AI diagnosis accuracy" />
      </div>
    </motion.div>
  )
}

function DashboardCard({ title, value, description }: DashboardCardProps) {
  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      className="bg-white p-6 rounded-lg shadow-md transition-all duration-300 ease-in-out hover:bg-gray-100 hover:shadow-lg"
    >
      <h2 className="text-xl font-semibold mb-2">{title}</h2>
      <p className="text-3xl font-bold text-indigo-600 mb-2">{value}</p>
      <p className="text-gray-600">{description}</p>
    </motion.div>
  )
}