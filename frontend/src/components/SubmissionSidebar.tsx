
import type { Submission } from '../App'; // Cleaned type import structure
import { CheckCircle2, AlertTriangle, Loader2, User, FileText } from 'lucide-react';

interface SidebarProps {
  submissions: Submission[];
  activeSubmission: Submission | null;
  setActiveSubmission: (sub: Submission) => void;
  isLoading: boolean;
  onRefresh: () => void;
}

export default function SubmissionSidebar({ 
  submissions, 
  activeSubmission, 
  setActiveSubmission, 
  isLoading, 
  onRefresh 
}: SidebarProps) {
  return (
    <aside className="w-80 border-r border-zinc-800 bg-zinc-900/20 flex flex-col overflow-hidden">
      <div className="p-4 border-b border-zinc-800/80 flex items-center justify-between">
        <h2 className="text-xs font-semibold text-zinc-400 tracking-wider uppercase">Student Submissions</h2>
        <button 
          onClick={onRefresh}
          className="text-xs bg-zinc-800 hover:bg-zinc-700 text-zinc-300 font-mono px-2 py-0.5 rounded-full border border-zinc-700/50 transition-colors"
        >
          {isLoading ? 'Pooling...' : `${submissions.length} Total`}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {submissions.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-center px-4">
            <FileText className="h-8 w-8 text-zinc-600 mb-2 stroke-[1.5]" />
            <p className="text-xs text-zinc-500">No active uploads loaded for this track context.</p>
          </div>
        ) : (
          submissions.map((sub) => {
            const isActive = activeSubmission?.id === sub.id;
            return (
              <button
                key={sub.id}
                onClick={() => setActiveSubmission(sub)}
                className={`w-full text-left p-3.5 rounded-xl border transition-all flex flex-col space-y-2 group ${
                  isActive ? 'bg-zinc-800/70 border-emerald-500/50 shadow-inner' : 'bg-transparent border-transparent hover:bg-zinc-900/50'
                }`}
              >
                <div className="flex items-center justify-between w-full">
                  <div className="flex items-center space-x-2">
                    <div className={`p-1.5 rounded-lg ${isActive ? 'bg-emerald-500/10 text-emerald-400' : 'bg-zinc-800 text-zinc-400'}`}>
                      <User className="h-3.5 w-3.5" />
                    </div>
                    <span className="text-sm font-medium font-mono text-zinc-200">{sub.student_id}</span>
                  </div>
                  
                  <div>
                    {sub.status === 'Completed' && (
                      <span className="flex items-center space-x-1 text-[11px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/25 px-2 py-0.5 rounded-full">
                        <CheckCircle2 className="h-3 w-3" />
                        <span>Score: {sub.final_score}</span>
                      </span>
                    )}
                    {sub.status === 'Processing' && (
                      <span className="flex items-center space-x-1 text-[11px] font-medium bg-amber-500/10 text-amber-400 border border-amber-500/25 px-2 py-0.5 rounded-full animate-pulse">
                        <Loader2 className="h-3 w-3 animate-spin" />
                        <span>Parsing...</span>
                      </span>
                    )}
                    {sub.status?.startsWith('Failed') && (
                      <span className="flex items-center space-x-1 text-[11px] font-medium bg-rose-500/10 text-rose-400 border border-rose-500/25 px-2 py-0.5 rounded-full">
                        <AlertTriangle className="h-3 w-3" />
                        <span>Failed</span>
                      </span>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center justify-between text-[11px] text-zinc-500 font-mono w-full">
                  <span>Sub ID: #{sub.id}</span>
                  <span className="truncate max-w-[140px] text-right">{sub.file_path ? sub.file_path.split('/').pop() : 'sheet.pdf'}</span>
                </div>
              </button>
            );
          })
        )}
      </div>
    </aside>
  );
}
