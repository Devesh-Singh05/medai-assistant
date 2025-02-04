"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"

interface Metrics {
  ct: {
    accuracy: number
    loss: number
    completed: number
    total: number
  }
  mri: {
    accuracy: number
    loss: number
    completed: number
    total: number
  }
  xray: {
    accuracy: number
    loss: number
    completed: number
    total: number
  }
}

export default function TrainingStatus() {
  const [metrics, setMetrics] = useState<Metrics | null>(null)

  useEffect(() => {
    // Simulating API call to fetch metrics
    setMetrics({
      ct: {
        accuracy: 85,
        loss: 0.15,
        completed: 750,
        total: 1000
      },
      mri: {
        accuracy: 90,
        loss: 0.1,
        completed: 800,
        total: 1000
      },
      xray: {
        accuracy: 88,
        loss: 0.12,
        completed: 900,
        total: 1000
      }
    })
  }, [])

  if (!metrics) {
    return <div>Loading metrics...</div>
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {/* CT Metrics */}
      <Card className="p-4">
        <h3 className="text-lg font-semibold mb-4">CT Scan Training</h3>
        <div className="space-y-4">
          <div>
            <div className="flex justify-between mb-2">
              <span className="text-sm font-medium">Accuracy</span>
              <span className="text-sm text-muted-foreground">{metrics.ct.accuracy}%</span>
            </div>
            <Progress value={metrics.ct.accuracy} />
          </div>
          <div>
            <div className="flex justify-between mb-2">
              <span className="text-sm font-medium">Loss</span>
              <span className="text-sm text-muted-foreground">{metrics.ct.loss.toFixed(2)}</span>
            </div>
            <Progress value={(1 - metrics.ct.loss) * 100} />
          </div>
          <div className="text-sm text-muted-foreground">
            {metrics.ct.completed} / {metrics.ct.total} images processed
          </div>
        </div>
      </Card>

      {/* MRI Metrics */}
      <Card className="p-4">
        <h3 className="text-lg font-semibold mb-4">MRI Training</h3>
        <div className="space-y-4">
          <div>
            <div className="flex justify-between mb-2">
              <span className="text-sm font-medium">Accuracy</span>
              <span className="text-sm text-muted-foreground">{metrics.mri.accuracy}%</span>
            </div>
            <Progress value={metrics.mri.accuracy} />
          </div>
          <div>
            <div className="flex justify-between mb-2">
              <span className="text-sm font-medium">Loss</span>
              <span className="text-sm text-muted-foreground">{metrics.mri.loss.toFixed(2)}</span>
            </div>
            <Progress value={(1 - metrics.mri.loss) * 100} />
          </div>
          <div className="text-sm text-muted-foreground">
            {metrics.mri.completed} / {metrics.mri.total} images processed
          </div>
        </div>
      </Card>

      {/* X-Ray Metrics */}
      <Card className="p-4">
        <h3 className="text-lg font-semibold mb-4">X-Ray Training</h3>
        <div className="space-y-4">
          <div>
            <div className="flex justify-between mb-2">
              <span className="text-sm font-medium">Accuracy</span>
              <span className="text-sm text-muted-foreground">{metrics.xray.accuracy}%</span>
            </div>
            <Progress value={metrics.xray.accuracy} />
          </div>
          <div>
            <div className="flex justify-between mb-2">
              <span className="text-sm font-medium">Loss</span>
              <span className="text-sm text-muted-foreground">{metrics.xray.loss.toFixed(2)}</span>
            </div>
            <Progress value={(1 - metrics.xray.loss) * 100} />
          </div>
          <div className="text-sm text-muted-foreground">
            {metrics.xray.completed} / {metrics.xray.total} images processed
          </div>
        </div>
      </Card>
    </div>
  )
}

