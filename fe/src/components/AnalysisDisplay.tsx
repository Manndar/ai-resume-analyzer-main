'use client';

import { AnalysisResult } from '../types';
import ReactMarkdown from 'react-markdown';

interface AnalysisDisplayProps {
    analysis: AnalysisResult;
}

export default function AnalysisDisplay({ analysis }: AnalysisDisplayProps) {
    return (
        <div className="prose prose-blue max-w-none">
            <ReactMarkdown>{analysis.analysis}</ReactMarkdown>
        </div>
    );
}
