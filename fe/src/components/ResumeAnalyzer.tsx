'use client';

import { useEffect, useState } from 'react';
import { Box, Button, TextField, Typography, Alert, CircularProgress } from '@mui/material';
import { AnalysisResult } from '../types';
import AnalysisDisplay from './AnalysisDisplay';
import CloseIcon from '@mui/icons-material/Close';
import IconButton from '@mui/material/IconButton';

export default function ResumeAnalyzer() {
    const [file, setFile] = useState<File | null>(null);
    const [jobDescription, setJobDescription] = useState('');
    const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!file) {
            setAnalysis(null);
        }
        setError(null);
    }, [file]);

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
        <Box
            sx={{
                backgroundColor: 'gray.50',
                borderRadius: 2,
                boxShadow: 3,
                p: 4,
                maxWidth: 800,
                mx: 'auto',
                mt: 4,
            }}
        >
            <form onSubmit={handleSubmit}>
                <Box mb={3}>
                    <Typography variant="subtitle1" gutterBottom>
                        Upload Resume (PDF)
                    </Typography>
                    <input
                        type="file"
                        accept=".pdf"
                        onChange={(e) => setFile(e.target.files?.[0] || null)}
                    />
                    {file && (
                        <IconButton
                            onClick={() => setFile(null)}
                            color="secondary"
                            sx={{ ml: 2 }}
                            aria-label="Remove File"
                        >
                            <CloseIcon />
                        </IconButton>
                    )}
                </Box>

                <Box mb={3}>
                    <TextField
                        label="Job Description (Optional)"
                        multiline
                        rows={4}
                        fullWidth
                        value={jobDescription}
                        onChange={(e) => setJobDescription(e.target.value)}
                        variant="outlined"
                    />
                </Box>

                <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    color="primary"
                    disabled={loading || !file}
                    startIcon={loading ? <CircularProgress size={20} color="inherit" /> : null}
                >
                    {loading ? 'Analyzing...' : 'Analyze Resume'}
                </Button>
            </form>

            {error && (
                <Box mt={3}>
                    <Alert severity="error">{error}</Alert>
                </Box>
            )}

            {analysis && (
                <Box mt={4}>
                    <AnalysisDisplay analysis={analysis} />
                </Box>
            )}
        </Box>
    );
}
