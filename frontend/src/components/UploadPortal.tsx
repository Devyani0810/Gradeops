import { useState } from 'react';
import type { FormEvent } from 'react';
import axios from 'axios';
import { X, FileCode, CheckCircle, Loader2 } from 'lucide-react';

interface UploadProps {
  isOpen: boolean;
  onClose: () => void;
  examId: number | null;
  onUploadComplete: () => void;
}

export default function UploadPortal({ onClose, examId, onUploadComplete }: UploadProps) {
  const [activeTab, setActiveTab] = useState<'upload' | 'create_exam'>('upload');
  const [studentId, setStudentId] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [examTitle, setExamTitle] = useState('');
  const [rubricStr, setRubricStr] = useState(
    JSON.stringify({ q1: { max_marks: 10, criteria: "Correct reactions and accurate bending moment direction." } }, null, 2)
  );

  const [isProcessing, setIsProcessing] = useState(false);
  const [errorLog, setErrorLog] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const handleCreateExamSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsProcessing(true);
    setErrorLog('');
    setSuccessMsg('');
    try {
      const formData = new FormData();
      formData.append('title', examTitle);
      formData.append('rubric_str', rubricStr);

      await axios.post('http://localhost:8000/api/v1/exams', formData);
      setSuccessMsg('Exam architecture blueprint injected cleanly!');
      setExamTitle('');
      setTimeout(() => window.location.reload(), 1000);
    } catch (err: any) {
      setErrorLog(err.response?.data?.detail || 'Validation exception during creation execution.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleUploadSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!examId) return setErrorLog('Please select an active Exam track identifier context.');
    if (!selectedFile) return setErrorLog('Please attach a target physical paper document asset.');

    setIsProcessing(true);
    setErrorLog('');
    setSuccessMsg('');

    try {
      const formData = new FormData();
      formData.append('student_id', studentId);
      formData.append('file', selectedFile);

      const res = await axios.post(`http://localhost:8000/api/v1/upload-exam/${examId}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setSuccessMsg(`Sheet dispatched! Active trace generation context ID: ${res.data.submission_id}`);
      setStudentId('');
      setSelectedFile(null);
      onUploadComplete();
    } catch (err: any) {
      setErrorLog(err.response?.data?.detail || 'Background asynchronous trigger pipeline mismatch.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-zinc-950/80 backdrop-blur-sm p-4">
      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl w-full max-w-xl shadow-2xl flex flex-col max-h-[90vh] overflow-hidden">
        <div className="p-4 border-b border-zinc-800 flex items-center justify-between bg-zinc-900/50">
          <div className="flex space-x-4">
            <button 
              onClick={() => { setActiveTab('upload'); setErrorLog(''); }}
              className={`pb-1 text-sm font-medium ${activeTab === 'upload' ? 'text-emerald-400 border-b-2 border-emerald-400 font-semibold' : 'text-zinc-400'}`}
            >
              Upload Answer Sheet
            </button>
            <button 
              onClick={() => { setActiveTab('create_exam'); setErrorLog(''); }}
              className={`pb-1 text-sm font-medium ${activeTab === 'create_exam' ? 'text-emerald-400 border-b-2 border-emerald-400 font-semibold' : 'text-zinc-400'}`}
            >
              Configure Fresh Exam
            </button>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200">
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {errorLog && <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl text-xs font-mono">❌ {errorLog}</div>}
          {successMsg && (
            <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-xl text-xs flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 shrink-0 animate-bounce" />
              <span>{successMsg}</span>
            </div>
          )}

          {activeTab === 'upload' ? (
            <form onSubmit={handleUploadSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-1.5">Student Roll Identifier</label>
                <input 
                  type="text" required placeholder="e.g. IITG_STUDENT_01"
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3.5 py-2 text-sm text-zinc-100 font-mono focus:outline-none focus:border-emerald-500"
                  value={studentId} onChange={(e) => setStudentId(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-1.5">Answer Sheet Document</label>
                <div className="border-2 border-dashed border-zinc-800 hover:border-zinc-700/80 rounded-xl p-6 text-center cursor-pointer relative bg-zinc-950/40 group">
                  <input type="file" required accept="application/pdf,image/*" className="absolute inset-0 opacity-0 cursor-pointer" onChange={(e) => e.target.files && setSelectedFile(e.target.files[0])} />
                  <FileCode className="h-8 w-8 text-zinc-600 group-hover:text-zinc-400 mx-auto mb-2 stroke-[1.5]" />
                  <p className="text-sm text-zinc-300 font-medium">{selectedFile ? selectedFile.name : 'Select or drop evaluation sheet asset'}</p>
                </div>
              </div>
              <button type="submit" disabled={isProcessing} className="w-full flex items-center justify-center space-x-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-zinc-800 disabled:text-zinc-600 text-zinc-950 font-semibold py-2.5 rounded-xl transition-all shadow-xl shadow-emerald-950/10 mt-6">
                {isProcessing ? <Loader2 className="h-5 w-5 animate-spin" /> : <span>Execute Asynchronous Agent Pipeline</span>}
              </button>
            </form>
          ) : (
            <form onSubmit={handleCreateExamSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-1.5">Exam Assignment Title</label>
                <input type="text" required placeholder="e.g. Endsem Structural Mechanics" className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3.5 py-2 text-sm text-zinc-100 focus:outline-none focus:border-emerald-500" value={examTitle} onChange={(e) => setExamTitle(e.target.value)} />
              </div>
              <div>
                <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-1.5">Structured Rubric Specifications Matrix</label>
                <textarea required rows={6} className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3.5 py-2.5 text-xs text-zinc-200 font-mono focus:outline-none focus:border-emerald-500" value={rubricStr} onChange={(e) => setRubricStr(e.target.value)} />
              </div>
              <button type="submit" disabled={isProcessing} className="w-full flex items-center justify-center space-x-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-zinc-800 disabled:text-zinc-600 text-zinc-950 font-semibold py-2.5 rounded-xl transition-all mt-6">
                {isProcessing ? <Loader2 className="h-5 w-5 animate-spin" /> : <span>Inject New Exam Rubric Schema</span>}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}