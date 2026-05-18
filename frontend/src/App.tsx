import { useState, useEffect } from 'react';
import axios from 'axios';
import { Upload, RefreshCw, Layers } from 'lucide-react';
import SubmissionSidebar from './components/SubmissionSidebar';
import SplitDashboard from './components/SplitDashboard';
import UploadPortal from './components/UploadPortal';

export interface Submission {
  id: number;
  student_id: string;
  status: 'Processing' | 'Completed' | 'Failed';
  file_path: string;
  extracted_text: string;
  page_image_keys: Record<string, string>;
  grading_breakdown: Record<string, { score: number; feedback: string }>;
  ai_score: number;
  final_score: number;
}

export interface Exam {
  id: number;
  title: string;
  rubric: Record<string, any>;
}

const API_BASE_URL = 'http://localhost:8000/api/v1';

export default function App() {
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [activeSubmission, setActiveSubmission] = useState<Submission | null>(null);
  const [exams, setExams] = useState<Exam[]>([]);
  const [selectedExamId, setSelectedExamId] = useState<number | null>(null);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const fetchExams = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/exams`);
      setExams(res.data);
      if (res.data.length > 0 && !selectedExamId) {
        setSelectedExamId(res.data[0].id);
      }
    } catch (err) {
      console.warn("Using fallback mock exam identifier track context.", err);
      const mockExams = [{ id: 3, title: 'Endsem Structural Mechanics', rubric: {} }];
      setExams(mockExams);
      setSelectedExamId(3);
    }
  };

  const fetchSubmissions = async () => {
    if (!selectedExamId) return;
    setIsLoading(true);
    try {
      const res = await axios.get(`${API_BASE_URL}/grades/${selectedExamId}`);
      setSubmissions(res.data);
    } catch (err) {
      console.error("Error pooling submission records:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchExams();
  }, []);

  useEffect(() => {
    if (selectedExamId) {
      fetchSubmissions();
    }
  }, [selectedExamId]);

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-50 font-sans flex flex-col selection:bg-emerald-500/30">
      <header className="border-b border-zinc-800 bg-zinc-900/50 backdrop-blur px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Layers className="h-6 w-6 text-emerald-500" />
          <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-zinc-50 to-zinc-400 bg-clip-text text-transparent">
            GradeOps <span className="text-sm text-emerald-400 font-mono ml-1">v1.5</span>
          </h1>
        </div>

        <div className="flex items-center space-x-4">
          <select 
            className="bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-1.5 text-sm text-zinc-200 focus:outline-none focus:border-emerald-500"
            value={selectedExamId || ''} 
            onChange={(e) => setSelectedExamId(Number(e.target.value))}
          >
            {exams.map((exam) => (
              <option key={exam.id} value={exam.id}>{exam.title}</option>
            ))}
          </select>

          <button 
            onClick={fetchSubmissions}
            className="p-2 text-zinc-400 hover:text-zinc-100 bg-zinc-800/50 hover:bg-zinc-800 border border-zinc-700/60 rounded-lg transition-all"
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin text-emerald-400' : ''}`} />
          </button>

          <button 
            onClick={() => setIsUploadModalOpen(true)}
            className="flex items-center space-x-2 bg-emerald-600 hover:bg-emerald-500 text-zinc-950 font-medium text-sm px-4 py-2 rounded-lg transition-all shadow-lg shadow-emerald-950/20"
          >
            <Upload className="h-4 w-4 stroke-[2.5]" />
            <span>Upload Evaluation Sheet</span>
          </button>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        <SubmissionSidebar 
          submissions={submissions}
          activeSubmission={activeSubmission}
          setActiveSubmission={setActiveSubmission}
          isLoading={isLoading}
          onRefresh={fetchSubmissions}
        />
        <main className="flex-1 overflow-hidden bg-zinc-950">
          <SplitDashboard 
            submission={activeSubmission} 
            onOverrideSuccess={(updatedSubmission) => {
              setActiveSubmission(updatedSubmission);
              setSubmissions(prev => prev.map(s => s.id === updatedSubmission.id ? updatedSubmission : s));
            }}
          />
        </main>
      </div>

      {isUploadModalOpen && (
        <UploadPortal 
          isOpen={isUploadModalOpen} 
          onClose={() => setIsUploadModalOpen(false)} 
          examId={selectedExamId}
          onUploadComplete={fetchSubmissions}
        />
      )}
    </div>
  );
}
