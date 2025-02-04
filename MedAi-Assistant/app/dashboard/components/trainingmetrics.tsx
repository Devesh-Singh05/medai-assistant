"use client"

import { useState, useEffect } from "react";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

interface TrainingMetrics {
    ct: {
        accuracy: number;
        loss: number;
    };
    mri: {
        accuracy: number;
        loss: number;
    };
    xray: {
        accuracy: number;
        loss: number;
    };
}

export default function TrainingMetrics() {
    const [metrics, setMetrics] = useState<TrainingMetrics>({
        ct: { accuracy: 0, loss: 0 },
        mri: { accuracy: 0, loss: 0 },
        xray: { accuracy: 0, loss: 0 },
    });

    useEffect(() => {
        // Simulating fetching metrics from an API
        const fetchMetrics = () => {
            // This is a mock implementation. In a real app, you'd fetch from your API.
            setMetrics({
                ct: { accuracy: 85, loss: 0.15 },
                mri: { accuracy: 90, loss: 0.1 },
                xray: { accuracy: 88, loss: 0.12 },
            });
        };

        fetchMetrics();
        // Set up an interval to fetch metrics every 5 seconds
        const intervalId = setInterval(fetchMetrics, 5000);

        // Clean up the interval on component unmount
        return () => clearInterval(intervalId);
    }, []);

    return (
        <div className="space-y-4">
            <h2 className="text-2xl font-bold">Training Metrics</h2>
            {Object.entries(metrics).map(([key, value]) => (
                <div key={key} className="space-y-2">
                    <Label className="text-lg capitalize">{key}</Label>
                    <div className="flex items-center space-x-2">
                        <span className="w-20">Accuracy:</span>
                        <Progress value={value.accuracy} className="w-full" />
                        <span>{value.accuracy.toFixed(2)}%</span>
                    </div>
                    <div className="flex items-center space-x-2">
                        <span className="w-20">Loss:</span>
                        <Progress value={(1 - value.loss) * 100} className="w-full" />
                        <span>{value.loss.toFixed(2)}</span>
                    </div>
                </div>
            ))}
            <Button onClick={() => console.log("Refresh metrics")}>
                Refresh Metrics
            </Button>
        </div>
    );
}

