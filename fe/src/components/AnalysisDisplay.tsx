'use client';

import { AnalysisResult } from '../types';
import ReactMarkdown from 'react-markdown';
import { Box, Typography } from '@mui/material';

interface AnalysisDisplayProps {
    analysis: AnalysisResult;
}

export default function AnalysisDisplay({ analysis }: AnalysisDisplayProps) {
    return (
        <Box>
            <Typography variant="h6" gutterBottom>
                Analysis Result
            </Typography>
            <Box sx={{ typography: 'body1' }}>
                <ReactMarkdown>{analysis.analysis}</ReactMarkdown>
            </Box>
        </Box>
    );
}
