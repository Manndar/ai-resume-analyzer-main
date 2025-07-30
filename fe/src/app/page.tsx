import ResumeAnalyzer from '../components/ResumeAnalyzer';

export default function Home() {
  return (
    <main className="min-h-screen p-8 bg-gray-100">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-8 text-gray-800">
          AI Resume Analyzer
        </h1>
        <ResumeAnalyzer />
      </div>
    </main>
  );
}
