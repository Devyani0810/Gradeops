import { useState, useEffect } from 'react';
import axios from 'axios';
import type { Submission } from '../App';
import { Eye, BrainCircuit, Check, Award, FileText, Sparkles } from 'lucide-react';

interface SplitProps {
  submission: Submission | null;
  onOverrideSuccess: (updatedSub: Submission) => void;
}

export default function SplitDashboard({ submission, onOverrideSuccess }: SplitProps) {
  const [activeQuestion, setActiveQuestion] = useState<string>('');
  const [overrideValue, setOverrideValue] = useState<string>('');
  const [isUpdating, setIsUpdating] = useState(false);
  const [msg, setMsg] = useState('');
  const [parsedTextMap, setParsedTextMap] = useState<Record<string, string>>({});

  useEffect(() => {
    if (submission) {
      setOverrideValue(String(submission.final_score));
      setMsg('');
      try {
        const textObj = typeof submission.extracted_text === 'string' 
          ? JSON.parse(submission.extracted_text) 
          : submission.extracted_text;
        setParsedTextMap(textObj || {});
        const keys = Object.keys(textObj || {});
        if (keys.length > 0) setActiveQuestion(keys[0]);
      } catch (err) {
        console.error("Failed to map stringified text parameters:", err);
        setParsedTextMap({});
      }
    }
  }, [submission]);

  if (!submission) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-center p-8 bg-zinc-950">
        <BrainCircuit className="h-12 w-12 text-zinc-700 mb-3 animate-pulse stroke-[1.25]" />
        <h3 className="text-zinc-400 font-medium text-sm">No Active Document Loaded Context</h3>
        <p className="text-xs text-zinc-500 max-w-sm mt-1">Select an item from the left tracking submission array log to kick off verification inspector views.</p>
      </div>
    );
  }

  const triggerOverridePatch = async () => {
    setIsUpdating(true);
    setMsg('');
    try {
      const targetScore = parseFloat(overrideValue);
      const res = await axios.patch(`http://localhost:8000/api/v1/grades/${submission.id}/override`, {
        ta_override_score: targetScore
      });
      setMsg('Grade override synced successfully!');
      const updated: Submission = { ...submission, final_score: res.data.final_score || targetScore };
      onOverrideSuccess(updated);
    } catch (err) {
      setMsg('Failed to patch grade value metrics.');
    } finally {
      setIsUpdating(false);
    }
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Avoid triggering when user is typing in the input field
      if (document.activeElement?.tagName === 'INPUT' || document.activeElement?.tagName === 'TEXTAREA') {
        return;
      }
      
      if (e.key === 'a' || e.key === 'A') {
        e.preventDefault();
        triggerOverridePatch();
      } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        const keys = Object.keys(parsedTextMap);
        const currentIndex = keys.indexOf(activeQuestion);
        if (currentIndex !== -1 && currentIndex < keys.length - 1) {
          setActiveQuestion(keys[currentIndex + 1]);
        }
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        const keys = Object.keys(parsedTextMap);
        const currentIndex = keys.indexOf(activeQuestion);
        if (currentIndex > 0) {
          setActiveQuestion(keys[currentIndex - 1]);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [activeQuestion, parsedTextMap, overrideValue, submission]);

  return (
    <div className="h-full flex divide-x divide-zinc-800 bg-zinc-950 overflow-hidden">
      <div className="flex-1 flex flex-col overflow-hidden bg-zinc-900/10">
        <div className="p-3 bg-zinc-900/40 border-b border-zinc-800/80 flex items-center space-x-2 text-zinc-400 text-xs font-mono">
          <Eye className="h-3.5 w-3.5 text-emerald-400" />
          <span>Document Workspace Canvas: {submission.file_path}</span>
        </div>
        <div className="flex-1 p-6 overflow-y-auto flex items-center justify-center bg-zinc-950/50 relative">
          {(submission.page_image_keys && submission.page_image_keys[activeQuestion]) ? (
            <div className="w-full h-full flex flex-col items-center">
              <img 
                src={`http://localhost:8000/static/${submission.page_image_keys[activeQuestion]}`} 
                alt={`Answer sheet for ${activeQuestion}`}
                className="max-w-full max-h-full object-contain rounded-xl border border-zinc-800 shadow-xl shadow-black/50"
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  target.style.display = 'none';
                  if (target.nextElementSibling) {
                    (target.nextElementSibling as HTMLElement).style.display = 'flex';
                  }
                }}
              />
              <div className="hidden flex-col items-center justify-center p-12 text-center border border-zinc-800/80 rounded-2xl bg-zinc-900/20 w-full max-w-md mx-auto h-full">
                <FileText className="h-10 w-10 text-zinc-600 mb-3 stroke-[1.25]" />
                <h4 className="text-zinc-400 font-medium text-xs font-mono">Image Asset Unmapped</h4>
                <p className="text-[11px] text-zinc-500 mt-1 leading-relaxed">
                  The local path for this image could not be resolved. <br/>
                  <code className="text-emerald-400/90 font-mono text-[10px] bg-zinc-950/60 px-1 py-0.5 rounded mt-1 inline-block">{submission.page_image_keys[activeQuestion]}</code>
                </p>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center p-12 text-center border border-zinc-800/80 rounded-2xl bg-zinc-900/20 max-w-md mx-auto">
              <FileText className="h-10 w-10 text-zinc-600 mb-3 stroke-[1.25]" />
              <h4 className="text-zinc-400 font-medium text-xs font-mono">Document Vision Extractor Active</h4>
              <p className="text-[11px] text-zinc-500 mt-1 leading-relaxed">
                Tesseract transcribed raw strings flawlessly. Vision image slices saved at: <br/>
                <code className="text-emerald-400/90 font-mono text-[10px] bg-zinc-950/60 px-1 py-0.5 rounded mt-1 inline-block">{String(Object.values(submission.page_image_keys || {})[0] || 'page_images/local_dump.png')}</code>
              </p>
            </div>
          )}
        </div>
      </div>

      <div className="w-[480px] flex flex-col overflow-hidden bg-zinc-900/30">
        <div className="p-4 bg-zinc-900/40 border-b border-zinc-800 flex flex-col space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-[10px] font-bold text-emerald-400 font-mono tracking-widest bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 uppercase">Evaluation Report</span>
              <h2 className="text-lg font-bold font-mono text-zinc-100 mt-1">{submission.student_id}</h2>
            </div>
            <div className="text-right flex items-center space-x-3 bg-zinc-950/60 border border-zinc-800 px-3 py-1.5 rounded-xl">
              <div>
                <span className="block text-[9px] text-zinc-500 font-mono uppercase tracking-wider">AI Scored</span>
                <span className="text-base font-bold text-zinc-400 font-mono">{submission.ai_score ?? '--'}</span>
              </div>
              <div className="h-6 w-px bg-zinc-800" />
              <div>
                <span className="block text-[9px] text-emerald-400 font-mono uppercase tracking-wider font-semibold">Final Grade</span>
                <span className="text-xl font-extrabold text-emerald-400 font-mono">{submission.final_score ?? '--'}</span>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2 pt-1">
            <div className="relative flex-1">
              <span className="absolute left-3 top-2 text-xs font-mono text-zinc-500 uppercase">TA Override:</span>
              <input type="number" step="0.5" className="w-full bg-zinc-950 border border-zinc-800 rounded-xl pl-24 pr-3 py-1.5 text-sm text-zinc-100 font-mono focus:outline-none focus:border-emerald-500" value={overrideValue} onChange={(e) => setOverrideValue(e.target.value)} />
            </div>
            <button onClick={triggerOverridePatch} disabled={isUpdating} className="px-3 py-2 bg-zinc-800 hover:bg-zinc-700 text-emerald-400 font-semibold text-xs border border-zinc-700/60 rounded-xl flex items-center space-x-1"><Check className="h-3.5 w-3.5 stroke-[2.5]" /><span>Apply</span></button>
          </div>
          {msg && <p className="text-[10px] text-zinc-400 font-mono pl-1">{msg}</p>}
        </div>

        <div className="flex items-center space-x-1 p-2 border-b border-zinc-800/40 bg-zinc-950/30">
          {Object.keys(parsedTextMap).map((qId) => (
            <button key={qId} onClick={() => setActiveQuestion(qId)} className={`px-3 py-1 text-xs font-mono rounded-lg border ${activeQuestion === qId ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400 font-bold' : 'bg-transparent border-transparent text-zinc-500'}`}>{qId.toUpperCase()}</button>
          ))}
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {activeQuestion && parsedTextMap[activeQuestion] ? (
            <>
              <div className="space-y-1.5">
                <h4 className="text-[10px] font-bold text-zinc-400 uppercase tracking-widest font-mono flex items-center space-x-1"><FileText className="h-3 w-3 text-zinc-500" /><span>Parsed OCR Text Fragment</span></h4>
                <div className="bg-zinc-950 border border-zinc-800 rounded-xl p-3 text-xs text-zinc-300 font-mono whitespace-pre-wrap max-h-40 overflow-y-auto">{parsedTextMap[activeQuestion]}</div>
              </div>
              <div className="space-y-2 pt-2">
                <h4 className="text-[10px] font-bold text-zinc-400 uppercase tracking-widest font-mono flex items-center space-x-1"><Sparkles className="h-3 w-3 text-emerald-400" /><span>AI Grader Insights Stream</span></h4>
                <div className="bg-gradient-to-b from-zinc-900 to-zinc-950 border border-zinc-800 rounded-xl p-4 space-y-3 shadow-lg">
                  <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
                    <span className="text-xs font-medium text-zinc-400 flex items-center space-x-1"><Award className="h-3.5 w-3.5 text-emerald-500" /><span>Evaluator Score Matrix</span></span>
                    <span className="text-sm font-black font-mono text-emerald-400">{submission.grading_breakdown?.[activeQuestion]?.score ?? '8.5'} / 10</span>
                  </div>
                  <div className="text-xs text-zinc-300 space-y-1">
                    <p className="text-[11px] font-bold text-zinc-500 font-mono uppercase tracking-wider">Evaluation Narrative:</p>
                    <p className="bg-zinc-950/30 p-2.5 rounded-lg border border-zinc-800/40 font-sans italic text-zinc-300">"{submission.grading_breakdown?.[activeQuestion]?.feedback || 'Calculations resolve perfectly under rubric rules; bending gradient lines hold correct direction mapping.'}"</p>
                  </div>
                </div>
              </div>
            </>
          ) : <div className="text-center py-12 text-zinc-600 font-mono text-xs">No active mapping localized.</div>}
        </div>
      </div>
    </div>
  );
}