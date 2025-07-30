'use client';

import { useState } from 'react';
import { AnalysisResult } from '../types';
import AnalysisDisplay from './AnalysisDisplay';

export default function ResumeAnalyzer() {
    const [file, setFile] = useState<File | null>(null);
    const [jobDescription, setJobDescription] = useState('');
    const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!file) {
            setError('Please upload a resume PDF file');
            return;
        }

        setLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append('resume', file);
        if (jobDescription) {
            formData.append('job_description', jobDescription);
        }

        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/analyze-resume/`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`Error: ${response.statusText}`);
            }

            const result = await response.json();
            setAnalysis(result);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred while analyzing the resume');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-white rounded-lg shadow-lg p-6">
            <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Upload Resume (PDF)
                    </label>
                    <input
                        type="file"
                        accept=".pdf"
                        onChange={(e) => setFile(e.target.files?.[0] || null)}
                        className="block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-full file:border-0
              file:text-sm file:font-semibold
              file:bg-blue-50 file:text-blue-700
              hover:file:bg-blue-100"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Job Description (Optional)
                    </label>
                    <textarea
                        value={jobDescription}
                        onChange={(e) => setJobDescription(e.target.value)}
                        rows={4}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        placeholder="Paste the job description here..."
                    />
                </div>

                <button
                    type="submit"
                    disabled={loading || !file}
                    className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white 
            ${loading || !file
                            ? 'bg-gray-400 cursor-not-allowed'
                            : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'
                        }`}
                >
                    {loading ? 'Analyzing...' : 'Analyze Resume'}
                </button>
            </form>

            {error && (
                <div className="mt-4 p-4 bg-red-50 text-red-700 rounded-md">
                    {error}
                </div>
            )}

            {analysis && (
                <div className="mt-8">
                    <AnalysisDisplay analysis={analysis} />
                </div>
            )}
        </div>
    );
}
