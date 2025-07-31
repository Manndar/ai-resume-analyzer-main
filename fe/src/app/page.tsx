import ResumeAnalyzer from '../components/ResumeAnalyzer';
import { Box, Typography, Link } from '@mui/material';

export default function Home() {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: '#f3f4f6', // equivalent to Tailwind's bg-gray-100
      }}
    >
      <Box component="main" sx={{ flexGrow: 1, p: 4 }}>
        <Box sx={{ maxWidth: '800px', mx: 'auto' }}>
          <Typography
            variant="h4"
            component="h1"
            align="center"
            fontWeight="bold"
            gutterBottom
            color="text.primary"
          >
            AI Resume Analyzer
          </Typography>
          <ResumeAnalyzer />
        </Box>
      </Box>

      <Box
        component="footer"
        sx={{
          backgroundColor: '#1f2937', // Tailwind's gray-800
          color: '#fff',
          textAlign: 'center',
          py: 2,
          fontSize: '0.875rem',
        }}
      >
        Powered by <strong>Next.js</strong> and <strong>Google Gemini AI</strong> | Developed by{' '}
        <Link
          href="https://www.linkedin.com/in/mandar-lokhande/"
          target="_blank"
          rel="noopener"
          underline="hover"
          sx={{ color: '#fff', fontWeight: 'bold' }}
        >
          Mandar Lokhande
        </Link>
      </Box>
    </Box>
  );
}
