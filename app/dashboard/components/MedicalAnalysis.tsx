'use client'

import React, { useState, useCallback } from 'react';
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { motion } from 'framer-motion';

export default function MedicalAnalysis() {
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [imageType, setImageType] = useState<'ct' | 'mri'>('ct');
    const [analysis, setAnalysis] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleFileChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
        setError(null);
        const file = event.target.files?.[0];
        if (file) {
            setSelectedFile(file);
        }
    }, []);

    const handleAnalyze = async () => {
        if (!selectedFile) return;

        setLoading(true);
        const formData = new FormData();
        formData.append('image', selectedFile);
        formData.append('type', imageType);

        try {
            const response = await fetch('/api/infer', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();
            if (data.success) {
                setAnalysis(data.result);
            } else {
                setError(data.error || 'Analysis failed');
            }
        } catch (error) {
            setError(error instanceof Error ? error.message : 'An error occurred');
        } finally {
            setLoading(false);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="w-full max-w-4xl p-6 space-y-6 bg-white rounded-lg shadow-md"
        >
            <div className="space-y-2">
                <h2 className="text-2xl font-bold">Medical Image Analysis</h2>
            </div>

            <div className="space-y-4">
                {/* Image Type Selection */}
                <div className="space-y-2">
                    <Label>Image Type</Label>
                    <Select
                        value={imageType}
                        onValueChange={(value: 'ct' | 'mri') => setImageType(value)}
                    >
                        <SelectTrigger>
                            <SelectValue placeholder="Select image type" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="ct">CT Scan</SelectItem>
                            <SelectItem value="mri">MRI Scan</SelectItem>
                        </SelectContent>
                    </Select>
                </div>

                {/* File Upload */}
                <div className="space-y-2">
                    <Label>Upload Image</Label>
                    <Input 
                        type="file"
                        onChange={handleFileChange}
                        accept={imageType === 'ct' ? '.dcm' : '.nii,.nii.gz'}
                    />
                </div>

                {/* Error Display */}
                {error && (
                    <motion.div 
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="p-4 text-red-600 bg-red-50 rounded-md"
                    >
                        {error}
                    </motion.div>
                )}

                {/* Analysis Button */}
                <Button
                    onClick={handleAnalyze}
                    disabled={!selectedFile || loading}
                    className="w-full"
                >
                    {loading ? 'Analyzing...' : 'Analyze Image'}
                </Button>

                {/* Analysis Results */}
                {analysis && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mt-6 p-4 border rounded-lg space-y-2"
                    >
                        <h3 className="text-lg font-semibold">Analysis Results</h3>
                        <div>
                            <p>Prediction: {analysis.prediction}</p>
                            <p>Confidence: {(analysis.confidence * 100).toFixed(2)}%</p>
                        </div>
                    </motion.div>
                )}
            </div>
        </motion.div>
    );
}